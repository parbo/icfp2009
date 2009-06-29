from simulation import Simulation
from mathutils import Hohmann
from mathutils import score, major_axis_from_orbit_period, v_in_perigee
import math
from vector import Vector

def calc_phi(r, atx, m):
    return math.pi * (1.0 - (2.0 * m - 1.0) * ((atx / r ) ** (3.0/2.0)))

def calc_a(r, dphi, n):
    return r * ((1.0 - dphi / (2.0 * math.pi * n)) ** (2.0/3.0))

class EccentricMeetAndGreetSim(Simulation):
    def __init__(self, problem=None, conf=None):
        Simulation.__init__(self, problem, conf, 'Hohmann transfer simulation')        
        self.h = None
        self.tb = None
        self.phase = self.init
        self.burntime = 0
        self.dphi = None
        self.transferradius = 0.0
        self.current_sat = 0
        self.skipnext = False

    def get_target_orbit(self):
        return self.transferradius

    def input(self):
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0
        if self.skipnext:
            self.skipnext = False
            return
        newphase = self.phase()
        if newphase and newphase != self.phase:
            print "******************************************"
            self.phase = newphase
            self.skipnext = True

    def init(self):
        sat = self.state.satellites[self.current_sat]
        if sat.orbit:
            self.transferradius = (1.0-sat.orbit.e) * sat.orbit.a
            return self.transfer

    def catch_up(self):
        sat = self.state.satellites[self.current_sat]
        phi = sat.s.angle_signed(self.state.s)
        if abs(self.dphi-phi) < 0.5 * abs(self.state.v)/self.state.radius:
            self.transferradius = sat.radius
            return self.transfer
        
    def transfer(self):
        if not self.h:
            if self.tb:
                self.h = self.tb
                self.tb = None
            else:
                self.h = Hohmann(self.state.radius, self.transferradius)
            print self.h
            print "expected score:", score(self.h.dvt, self.initial_fuel, self.state.time+self.h.TOF+900)
            self.burntime = self.state.time
            dvx, dvy = self.h.burn(self.state.dir, self.state.s, self.state.v)
            print "Burn:", dvx, dvy, self.state.v
            self.vm.input[2], self.vm.input[3] = dvx, dvy
            if dvx != self.vm.input[2]:
                raise Exception
            if dvy != self.vm.input[3]:
                raise Exception

        if abs(self.state.time-(self.burntime+self.h.TOF)) < 1:            
            return self.intercept

    def intercept(self):
        print "Intercept burn"
        self.vm.input[2], self.vm.input[3] = self.h.interceptburn(self.state.dir, self.state.s, self.state.v)            

        self.h = None
        if abs(self.state.radius-self.transferradius) > 500.0:
            # didn't hit target, do a new transfer
            print "didn't hit target, do a new transfer"
            return self.transfer
        return self.target
        
    def target(self):
        sat = self.state.satellites[self.current_sat]
        if abs(Vector(1.0, 0.0).angle_signed(self.state.s) - sat.orbit.angle) < 0.005:
            self.h = Hohmann(self.state.radius, 2.0 * sat.orbit.a - self.state.radius)
            print self.h
            self.burntime = self.state.time
            dvx, dvy = self.h.burn(self.state.dir, self.state.s, self.state.v)
            self.vm.input[2], self.vm.input[3] = dvx, dvy
            return self.rendez_vous

    def wait(self):
        sat = self.state.satellites[self.current_sat]
        if abs(-Vector(1.0, 0.0).angle_signed(self.state.s) - sat.orbit.angle) < 0.005:
            self.perigee_passes -= 1
            if self.perigee_passes == 0:
                return self.adjust
        pass

    def adjust(self):
        # add adjuster
        return self.rendez_vous
        pass

    def rendez_vous(self):
        sat = self.state.satellites[self.current_sat]
        if abs(Vector(1.0, 0.0).angle_signed(self.state.s) - sat.orbit.angle) < 0.005:
            print "sat time to perigee", sat.orbit.time_to_perigee(sat.s)
            a = 0.0
            self.perigee_passes = 1
            t2p = sat.orbit.time_to_perigee(sat.s)
            op = sat.orbit.orbit_period
            if t2p > (op / 2.0):
                print "Sat is AHEAD"
                new_orbit_period = t2p
            else:
                print "Sat is BEHIND"
                new_orbit_period = op + t2p
            
            print "Orbit periods", op, t2p, new_orbit_period

            a = major_axis_from_orbit_period((self.perigee_passes) * new_orbit_period)
            print "Major axis", a
            print "Radius", abs(self.state.s)
            newv = v_in_perigee(abs(self.state.s), a)
            v = self.state.v
            vb = newv * v.normalize() - v
            self.vm.input[2], self.vm.input[3] = -vb.x, -vb.y
            self.burntime = self.state.time
            return self.wait
                

def Create(problem, conf):
    return EccentricMeetAndGreetSim(problem, conf)

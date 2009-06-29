from simulation import Simulation, EARTH_RADIUS
from mathutils import Hohmann
from mathutils import score, major_axis_from_orbit_period, v_in_perigee, Rj
import math
from vector import Vector
import ellipse

def calc_phi(r, atx, m):
    return math.pi * (1.0 - (2.0 * m - 1.0) * ((atx / r ) ** (3.0/2.0)))

def calc_a(r, dphi, n):
    return r * ((1.0 - dphi / (2.0 * math.pi * n)) ** (2.0/3.0))

def same_angle(a1, a2):
    diff = abs(a1-a2)
    while diff > 2.0 * math.pi:
        diff -= 2.0 * math.pi
    return diff < 0.005

def print_time_to_perigee(sat):
    print "SAT_PERIGEE", sat.orbit.angle_past_perigee(sat.s), sat.orbit.time_to_perigee(sat.s)
        
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
        self.adjust_ready_time = 0
        self.hack = False
        self.sat = None
        self.refuelling = False

    def get_target_orbit(self):
        return self.transferradius

    def input(self):
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0

        if self.refuelling:
            self.sat = self.state.fuel_station
        else:
            self.sat = self.state.satellites[self.current_sat]
        
        if self.sat.v:
            self.sat.create_orbit()
        if self.skipnext:
            self.skipnext = False
            return
        newphase = self.phase()
        # try:
        #     sat = self.sat
        #     print_time_to_perigee(sat)
        #     if same_angle(math.pi + sat.angle, sat.orbit.angle):
        #         print "ORBIT", self.state.time
        # except:
        #     pass
        if newphase and newphase != self.phase:
            print "******************************************"
            self.phase = newphase
            self.skipnext = True

    def init(self):
        self.h = None
        sat = self.sat
        if sat.orbit:
            self.transferradius = (1.0-sat.orbit.e) * sat.orbit.a
            return self.transfer

    def catch_up(self):
        sat = self.sat
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
        sat = self.sat
        print "Intercept burn"
        print self.conf
        if self.conf == 4004:
            self.hack = True
        dvx, dvy = self.h.interceptburn(self.state.dir, self.state.s, self.state.v, self.hack)
        self.vm.input[2], self.vm.input[3] = dvx, dvy
        
        self.h = None
        if self.adjust_orbit_needed(sat):
            return self.adjust_orbit
        return self.target
        
    def target(self):
        sat = self.sat
        if same_angle(math.pi + self.state.angle, sat.orbit.angle):
            self.h = Hohmann(self.state.radius, 2.0 * sat.orbit.a - self.state.radius)
            print self.h
            self.burntime = self.state.time
            dvx, dvy = self.h.burn(self.state.dir, self.state.s, self.state.v)
            self.vm.input[2], self.vm.input[3] = dvx, dvy
            return self.rendez_vous

    def wait(self):
        sat = self.sat
        sr = self.state.s
        tr = sat.s
        d = abs(sr - tr)
        if self.adjust_allowed(sat):
            print 'Enter adjust state at distance d = %.4e' % d
            return self.adjust
        if self.adjust_orbit_needed(sat):
            return self.adjust_orbit
        pass
        
    def adjust_orbit_needed(self, sat):
        # doesn't work
        return False

        sr = self.state.s
        o = self.sat.orbit
        tr = self.state.s.normalize() * (o.a-o.c)
        d = abs(sr - tr)
        ret = (d > 10e4)        
        print "ADJUST ORBIT NEEDED: ", ret
        return ret

    def adjust_allowed(self, sat):
        sr = self.state.s
        tr = sat.s
        d = abs(sr - tr)
        return (d < 100e4)

    def adjust(self):
        if self.time > self.adjust_ready_time:
            dt = 1200
            # Make thrust
            sr = self.state.s
            sv = self.state.v
            tr = self.sat.s
            tv = self.sat.v
            d = abs(sr - tr)
            if d < 500.0:
                return self.idle
            dv = tv - sv + (1.0 / dt) * (tr -sr)
            self.adjust_ready_time = self.time + 1000
            print 'Gravity free navigation'
            print 'Distance: %.0f' % abs(sr - tr)
            print 'Thrust (t=%d): %s' % (self.time, dv)
            self.vm.input[2] = -dv.x
            self.vm.input[3] = -dv.y

    def adjust_orbit(self):
        if self.time > self.adjust_ready_time:
            dt = 1200
            # Make thrust
            sr = self.state.s
            sv = self.state.v
            o = self.sat.orbit
            tr = self.state.s.normalize() * (o.a-o.c)
            tv = self.state.v.normalize() * ((o.a-o.c) / abs(sv))
            d = abs(sr - tr)
            if d < 500.0:
                return self.target
            dv = 0.1 * tv - sv + (1.0 / dt) * (tr -sr)
            self.adjust_ready_time = self.time + 1000
            print 'Gravity free navigation'
            print 'Distance: %.0f' % abs(sr - tr)
            print 'Thrust (t=%d): %s' % (self.time, dv)
            self.vm.input[2] = -dv.x
            self.vm.input[3] = -dv.y

    def rendez_vous(self):
        sat = self.sat
        if same_angle(math.pi + self.state.angle, sat.orbit.angle):
            a = 0.0
            self.perigee_passes = 0
            e = None
            while e == None or abs((e.a-e.c) - Rj) < 20000.0:
                t2p = sat.orbit.time_to_perigee(sat.s)
                op = sat.orbit.orbit_period
                if t2p > (op / 2.0):
                    print "Sat is AHEAD"
                    new_orbit_period = t2p
                else:
                    print "Sat is BEHIND"
                    new_orbit_period = op + t2p
                    
                print "Orbit periods", op, t2p, new_orbit_period

                a = major_axis_from_orbit_period((1+self.perigee_passes) * new_orbit_period)
                print "Major axis", a
                print "Radius", abs(self.state.s)

                newv = v_in_perigee(abs(self.state.s), a)
                v = self.state.v
                vb = newv * v.normalize() - v
                e = ellipse.create(self.state.s, vb)                

                print "Earth check", abs((e.a-e.c) - Rj)

                self.perigee_passes += 1

            self.vm.input[2], self.vm.input[3] = -vb.x, -vb.y
            self.burntime = self.state.time
            return self.wait
            
    def idle(self):
        self.current_sat += 1
        print "Switching to satellite", self.current_sat
        if self.current_sat < len(self.state.satellites):
            print "Going back to init"
            if self.refuelling:
                self.refuelling = False
            else:
                self.refuelling = True
            return self.init
                

def Create(problem, conf):
    return EccentricMeetAndGreetSim(problem, conf)

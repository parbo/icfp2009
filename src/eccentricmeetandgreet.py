from simulation import Simulation
from mathutils import Hohmann
from mathutils import score
import math
from vector import Vector

def calc_phi(r, atx, m):
    return math.pi * (1.0 - (2.0 * m - 1.0) * ((atx / r ) ** (3.0/2.0)))

def calc_a(r, dphi, n):
    return r * ((1.0 - dphi / (2.0 * math.pi * n)) ** (2.0/3.0))

class EccentricMeetAndGreetSim(Simulation):
    INIT = 0
    CATCH_UP = 1
    TRANSFER = 2
    INTERCEPT = 3
    TARGET = 4
    RENDEZ_VOUS = 5
    def __init__(self, problem=None, conf=None):
        Simulation.__init__(self, problem, conf, 'Hohmann transfer simulation')        
        self.h = None
        self.tb = None
        self.phase = EccentricMeetAndGreetSim.INIT
        self.burntime = 0
        self.dphi = None
        self.transferradius = 0.0

    def get_target_orbit(self):
        return self.transferradius

    def input(self):
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0
        if self.phase == EccentricMeetAndGreetSim.INIT:
            newphase = self.init()
        elif self.phase == EccentricMeetAndGreetSim.CATCH_UP:
            newphase = self.catch_up()
        elif self.phase == EccentricMeetAndGreetSim.TRANSFER:
            newphase = self.transfer()
        elif self.phase == EccentricMeetAndGreetSim.INTERCEPT:
            newphase = self.intercept()
        elif self.phase == EccentricMeetAndGreetSim.TARGET:
            newphase = self.target()
        elif self.phase == EccentricMeetAndGreetSim.RENDEZ_VOUS:
            newphase = self.rendez_vous()
        if newphase and newphase != self.phase:
            self.phase = newphase
            print "New phase:", self.phase

    def init(self):
        sat = self.state.satellites[0]
        if sat.orbit:
            self.transferradius = (1.0-sat.orbit.e) * sat.orbit.a
            return EccentricMeetAndGreetSim.TRANSFER

    def catch_up(self):
        sat = self.state.satellites[0]
        phi = sat.s.angle_signed(self.state.s)
        if abs(self.dphi-phi) < 0.5 * abs(self.state.v)/self.state.radius:
            self.transferradius = sat.radius
            return EccentricMeetAndGreetSim.TRANSFER
        
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
            return EccentricMeetAndGreetSim.INTERCEPT

    def intercept(self):
        print "Intercept burn"
        self.vm.input[2], self.vm.input[3] = self.h.interceptburn(self.state.dir, self.state.s, self.state.v)            

        self.h = None
        if abs(self.state.radius-self.transferradius) > 500.0:
            # didn't hit target, do a new transfer
            print "didn't hit target, do a new transfer"
            return EccentricMeetAndGreetSim.TRANSFER
        return EccentricMeetAndGreetSim.TARGET
        
    def target(self):
        sat = self.state.satellites[0]
        #print "Orbit periods:", self.state.orbit.orbit_period, sat.orbit.orbit_period
        if abs(Vector(1.0, 0.0).angle_signed(self.state.s) - sat.orbit.angle) < 0.005:
            self.h = Hohmann(self.state.radius, 2.0 * sat.orbit.a - self.state.radius)
            print self.h
            self.burntime = self.state.time
            dvx, dvy = self.h.burn(self.state.dir, self.state.s, self.state.v)
            self.vm.input[2], self.vm.input[3] = dvx, dvy
            return EccentricMeetAndGreetSim.RENDEZ_VOUS            

    def rendez_vous(self):
        pass

def Create(problem, conf):
    return EccentricMeetAndGreetSim(problem, conf)

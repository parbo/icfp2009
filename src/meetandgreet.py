from simulation import Simulation
from mathutils import Hohmann
from mathutils import score
import math
from vector import Vector

def calc_phi(r, atx, m):
    return math.pi * (1.0 - (2.0 * m - 1.0) * ((atx / r ) ** (3.0/2.0)))

def calc_a(r, dphi, n):
    return r * ((1.0 - dphi / (2.0 * math.pi * n)) ** (2.0/3.0))

class MeetAndGreetSim(Simulation):
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
        self.phase = MeetAndGreetSim.INIT
        self.burntime = 0
        self.dphi = None
        self.transferradius = 0.0

    def get_target_orbit(self):
        return self.transferradius

    def input(self):
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0
        if self.phase == MeetAndGreetSim.INIT:
            newphase = self.init()
        elif self.phase == MeetAndGreetSim.CATCH_UP:
            newphase = self.catch_up()
        elif self.phase == MeetAndGreetSim.TRANSFER:
            newphase = self.transfer()
        elif self.phase == MeetAndGreetSim.INTERCEPT:
            newphase = self.intercept()
        elif self.phase == MeetAndGreetSim.TARGET:
            newphase = self.target()
        elif self.phase == MeetAndGreetSim.RENDEZ_VOUS:
            newphase = self.rendez_vous()
        if newphase and newphase != self.phase:
            self.phase = newphase
            print "New phase:", self.phase

    def init(self):
        sat = self.state.satellites[0]
        if sat.radius:
            self.dphi = calc_phi(sat.radius, (self.state.radius + sat.radius)/2.0, 1)
            return MeetAndGreetSim.CATCH_UP

    def catch_up(self):
        sat = self.state.satellites[0]
        phi = sat.s.angle_signed(self.state.s)
        if abs(self.dphi-phi) < 0.5 * abs(self.state.v)/self.state.radius:
            self.transferradius = sat.radius
            return MeetAndGreetSim.TRANSFER
        
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
            return MeetAndGreetSim.INTERCEPT

    def intercept(self):
        print "Intercept burn"
        self.vm.input[2], self.vm.input[3] = self.h.interceptburn(self.state.dir, self.state.s, self.state.v)            

        self.h = None
        if abs(self.state.radius-self.transferradius) > 500.0:
            # didn't hit target, do a new transfer
            print "didn't hit target, do a new transfer"
            return MeetAndGreetSim.TRANSFER
        return MeetAndGreetSim.TARGET
        
    def target(self):
        sat = self.state.satellites[0]
        if abs(self.state.s-sat.s) > 1000.0:
            return MeetAndGreetSim.RENDEZ_VOUS

    def rendez_vous(self):
        if not self.h:
            sat = self.state.satellites[0]
            d = sat.s-self.state.s            
            phi = sat.s.angle_signed(self.state.s)
            atx = calc_a(sat.radius, phi, 1)
            print "Semi major axis:", atx
            print "phi:", phi
            self.h = Hohmann(sat.radius, 2.0 * atx - sat.radius)
            print self.h
            self.burntime = self.state.time
            dvx, dvy = self.h.burn(self.state.dir, self.state.s, self.state.v)
            print "Burn:", dvx, dvy, abs(Vector(dvx, dvy))
            self.vm.input[2], self.vm.input[3] = dvx, dvy
            if abs(self.state.time-(self.burntime + 2.0 * self.h.TOF)) <= 1.0:
                return MeetAndGreetSim.INTERCEPT
            
def Create(problem, conf):
    return MeetAndGreetSim(problem, conf)

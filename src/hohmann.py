from simulation import Simulation, State, MeetAndGreetState, EARTH_RADIUS
from mathutils import Hohmann, TangentBurn, get_hohmann_score_func, score, hohmann_score
from mathutils import score
import math
from vector import Vector
#import matplotlib.pyplot as plt
import numpy
import scipy.optimize

def calc_phi(r, atx, m):
    return math.pi * (1.0 - (2.0 * m - 1.0) * ((atx / r ) ** (3.0/2.0)))

def calc_a_before(r, dphi, n):
    return r * (((1.0 + (2.0 * math.pi - dphi) / (2.0 * math.pi * n)) ** 2.0) ** (1.0/3.0))
def calc_a_after(r, dphi, n):
    return r * ((1.0 - dphi / (2.0 * math.pi * n)) ** (2.0/3.0))

def genfunc(ra, rb, fuel, scorefunc):
    def myfunc(atx):
        if atx < ra or atx > rb:
            return 0.0
        tb = TangentBurn(ra, rb, atx)
        sc = scorefunc(fuel-tb.dvt, fuel, tb.TOF+900)
        return -sc
    return myfunc

class HohmannSim(Simulation):
    INIT = 0
    CATCH_UP = 1
    TRANSFER = 2
    INTERCEPT = 3
    TARGET = 4
    RENDEZ_VOUS = 5
    GRAVITY_FREE = 6
    def __init__(self, problem=None, conf=None):
        Simulation.__init__(self, problem, conf, 'Hohmann transfer simulation')        
        self.h = None
        self.tb = None
        self.phase = HohmannSim.INIT
        self.burntime = 0
        self.dphi = None
        self.transferradius = 0.0

    def get_target_orbit(self):
        return self.transferradius

    def input(self):
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0
        if self.phase == HohmannSim.INIT:
            newphase = self.init()
        elif self.phase == HohmannSim.CATCH_UP:
            newphase = self.catch_up()
        elif self.phase == HohmannSim.TRANSFER:
            newphase = self.transfer()
        elif self.phase == HohmannSim.INTERCEPT:
            newphase = self.intercept()
        elif self.phase == HohmannSim.TARGET:
            newphase = self.target()
        elif self.phase == HohmannSim.RENDEZ_VOUS:
            newphase = self.rendez_vous()
        if newphase and newphase != self.phase:
            self.phase = newphase
            print "New phase:", self.phase

    def init(self):
        if self.scenariotype == "Hohmann":
            if self.state.s and self.state.v:
                if False:
                    f = get_hohmann_score_func(self.state.radius, self.state.vm.output[4], self.initial_fuel)
                    g = lambda x: -f(x)
                    opt = scipy.optimize.fmin(g, self.state.vm.output[4])
                    print "Optimum intermediate transfer radius:", opt
                    self.transferradius = opt[0]
                else:
                    atx = scipy.optimize.fmin(genfunc(self.state.radius, self.state.vm.output[4], self.initial_fuel, hohmann_score), 3.0 * (self.state.radius+self.state.vm.output[4]) / 4.0)                   
                    print atx
                    self.transferradius = self.state.vm.output[4]
                    self.tb = TangentBurn(self.state.radius, self.transferradius, atx)
                return HohmannSim.TRANSFER
        elif self.scenariotype == "MeetAndGreet":
            sat = self.state.satellites[0]
            if sat.radius:
                self.dphi = calc_phi(sat.radius, (self.state.radius + sat.radius)/2.0, 1)
                return HohmannSim.CATCH_UP
            return self.phase

    def catch_up(self):
        sat = self.state.satellites[0]
        phi = sat.s.angle_signed(self.state.s)
        print self.dphi, phi
        print abs(self.dphi-phi)
        if abs(self.dphi-phi) < 0.5 * abs(self.state.v)/self.state.radius:
            self.transferradius = sat.radius
            return HohmannSim.TRANSFER
        
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
            dvx, dvy = self.h.burn(self.state)
            print "Burn:", dvx, dvy
            self.vm.input[2], self.vm.input[3] = dvx, dvy
            if dvx != self.vm.input[2]:
                raise Exception
            if dvy != self.vm.input[3]:
                raise Exception

        if abs(self.state.time-(self.burntime+self.h.TOF)) < 1:            
            return HohmannSim.INTERCEPT

    def intercept(self):
        print "Intercept burn"
        if self.scenariotype == "Hohmann":
            tmp1x, tmp1y = self.h.interceptburn(self.state, False)
            tmp2x, tmp2y = self.h.interceptburn(self.state, True)
            dv1 = Vector(tmp1x, tmp1y)
            dv2 = Vector(tmp2x, tmp2y)
            adv1 = abs(dv1)
            adv2 = abs(dv2)
            dvx, dvy = dv1.x, dv1.y
            if adv2 < self.state.current_fuel and adv2 > adv1:
                dvx, dvy = dv2.x, dv2.y
            self.vm.input[2], self.vm.input[3] = dvx, dvy
        else:
            self.vm.input[2], self.vm.input[3] = self.h.interceptburn(self.state)            

        self.h = None
        if self.scenariotype == "Hohmann":
#            print "Distance:", abs(self.state.radius-self.transferradius), self.state.radius, self.transferradius
            if abs(self.state.radius-self.transferradius) > 500.0:
                # didn't hit target, do a new transfer
                return HohmannSim.TRANSFER
            elif abs(self.transferradius-self.state.vm.output[4]) > 500.0:
                # target hit, but were not at final target
                self.transferradius = self.state.vm.output[4]
                return HohmannSim.TRANSFER
        return HohmannSim.TARGET
        
    def target(self):
        if self.scenariotype != "Hohmann":
            sat = self.state.satellites[0]
            if abs(self.state.s-sat.s) > 1000.0:
                return HohmannSim.RENDEZ_VOUS

    def rendez_vous(self):
        if not self.h:
            sat = self.state.satellites[0]
            d = sat.s-self.state.s            
            phi = sat.s.angle_signed(self.state.s)
#            if d * v > 0.0:
            atx = calc_a_after(sat.radius, phi, 1)
#            else:
#                atx = calc_a_before(sat.radius, phi, 1)
            print "Semi major axis:", atx
            self.h = Hohmann(sat.radius, 2.0 * atx - sat.radius)
            print self.h
            self.burntime = self.state.time
            self.vm.input[2], self.vm.input[3] = self.h.burn(self.state)
        if abs(self.state.time-(self.burntime + 2.0 * self.h.TOF)) <= 1.0:            
            return HohmannSim.INTERCEPT

def Create(problem, conf):
    return HohmannSim(problem, conf)

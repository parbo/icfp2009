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
            if self.state.sx and self.state.vx:
                if False:
                    f = get_hohmann_score_func(self.state.radius, self.state.vm.output[4], self.initial_fuel)
                    t = numpy.arange(self.state.radius, 10.0*max(self.state.radius, self.state.vm.output[4]), 5000.0)
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
            return self.phase
        elif self.scenariotype == "MeetAndGreet":
            sat = self.state.satellites[0]
            if sat.radius:
                self.dphi = calc_phi(sat.radius, (self.state.radius + sat.radius)/2.0, 1)
                return HohmannSim.CATCH_UP
            return self.phase

    def catch_up(self):
        sat = self.state.satellites[0]
        satpos = Vector(sat.sx, sat.sy)
        pos = Vector(self.state.sx, self.state.sy)
        phi = satpos.angle_signed(pos)
        print self.dphi, phi
        print abs(self.dphi-phi)
        if abs(self.dphi-phi) < 0.5 * abs(Vector(self.state.vx, self.state.vy))/self.state.radius:
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
            self.vm.input[2], self.vm.input[3] = self.h.burn(self.state.sx, self.state.sy, self.state.vx, self.state.vy)
        if abs(self.state.time-(self.burntime+self.h.TOF)) < 1:            
            return HohmannSim.INTERCEPT

    def intercept(self):
        print "Intercept burn"
        self.vm.input[2], self.vm.input[3] = self.h.interceptburn(self.state.sx, self.state.sy, self.state.vx, self.state.vy)
        self.h = None
        if self.scenariotype == "Hohmann":
            print "Distance:", abs(self.state.radius-self.transferradius), self.state.radius, self.transferradius
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
            satpos = Vector(sat.sx, sat.sy)
            pos = Vector(self.state.sx, self.state.sy)
            if abs(pos-satpos) > 1000.0:
                return HohmannSim.RENDEZ_VOUS

    def rendez_vous(self):
        if not self.h:
            sat = self.state.satellites[0]
            satpos = Vector(sat.sx, sat.sy)
            pos = Vector(self.state.sx, self.state.sy)
            v = Vector(self.state.vx, self.state.vy)
            d = satpos-pos            
            phi = satpos.angle_signed(pos)
#            if d * v > 0.0:
            atx = calc_a_after(sat.radius, phi, 1)
#            else:
#                atx = calc_a_before(sat.radius, phi, 1)
            print "Semi major axis:", atx
            self.h = Hohmann(sat.radius, 2.0 * atx - sat.radius)
            print self.h
            self.burntime = self.state.time
            self.vm.input[2], self.vm.input[3] = self.h.burn(self.state.sx, self.state.sy, self.state.vx, self.state.vy)
        if abs(self.state.time-(self.burntime + 2.0 * self.h.TOF)) < 1:            
            return HohmannSim.INTERCEPT

def Create(problem, conf):
    return HohmannSim(problem, conf)

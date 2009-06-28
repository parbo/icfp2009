from simulation import Simulation
from mathutils import Hohmann, TangentBurn, hohmann_score
import math
from vector import Vector
import scipy.optimize

def calc_phi(r, atx, m):
    return math.pi * (1.0 - (2.0 * m - 1.0) * ((atx / r ) ** (3.0/2.0)))

def calc_a(r, dphi, n):
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
    TRANSFER = 2
    INTERCEPT = 3
    TARGET = 4
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
        elif self.phase == HohmannSim.TRANSFER:
            newphase = self.transfer()
        elif self.phase == HohmannSim.INTERCEPT:
            newphase = self.intercept()
        elif self.phase == HohmannSim.TARGET:
            newphase = self.target()
        if newphase and newphase != self.phase:
            self.phase = newphase
            print "New phase:", self.phase

    def init(self):
        if self.state.s and self.state.v:
            atx = scipy.optimize.fmin(genfunc(self.state.radius, 
                                              self.state.vm.output[4], 
                                              self.initial_fuel, 
                                              hohmann_score), 
                                      3.0 * (self.state.radius+self.state.vm.output[4]) / 4.0)
            print "Optimum semi major axis for one-tangent burn", atx
            self.transferradius = self.state.vm.output[4]
            self.tb = TangentBurn(self.state.radius, self.transferradius, atx)
            return HohmannSim.TRANSFER

    def transfer(self):
        if not self.h:
            if self.tb:
                self.h = self.tb
                self.tb = None
            else:
                self.h = Hohmann(self.state.radius, self.transferradius)
            print self.h
            print "expected score:", hohmann_score(self.h.dvt, self.initial_fuel, self.state.time+self.h.TOF+900)
            self.burntime = self.state.time
            dvx, dvy = self.h.burn(self.state.dir, self.state.s, self.state.v)
            print "Burn:", dvx, dvy, self.state.v
            self.vm.input[2], self.vm.input[3] = dvx, dvy

        if abs(self.state.time-(self.burntime+self.h.TOF)) < 1:            
            return HohmannSim.INTERCEPT

    def intercept(self):
        print "Intercept burn"
        tmp1x, tmp1y = self.h.interceptburn(self.state.dir, self.state.s, self.state.v, False)
        tmp2x, tmp2y = self.h.interceptburn(self.state.dir, self.state.s, self.state.v, True)
        dv1 = Vector(tmp1x, tmp1y)
        dv2 = Vector(tmp2x, tmp2y)
        adv1 = abs(dv1)
        adv2 = abs(dv2)
        dvx, dvy = dv1.x, dv1.y
        if adv2 < self.state.current_fuel and adv2 > adv1:
            dvx, dvy = dv2.x, dv2.y
        print "BURRRRNNN"
        print self.h
        print "Fuel", self.state.current_fuel
        self.vm.input[2], self.vm.input[3] = dvx, dvy
        self.h = None
        if abs(self.state.radius-self.transferradius) > 500.0:
            # didn't hit target, do a new transfer
            print "didn't hit target, do a new transfer"
            return HohmannSim.TRANSFER
        return HohmannSim.TARGET
        
    def target(self):
        pass

def Create(problem, conf):
    return HohmannSim(problem, conf)

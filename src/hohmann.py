from simulation import Simulation, State, MeetAndGreetState, EARTH_RADIUS
from mathutils import Hohmann, TangentBurn, get_hohmann_score_func
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
        self.phase = HohmannSim.INIT
        self.burntime = 0
        self.dphi = None
        self.transferradius = 0.0

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
                f = get_hohmann_score_func(self.state.radius, self.state.vm.output[4], self.initial_fuel)
                t = numpy.arange(self.state.radius, 10.0*max(self.state.radius, self.state.vm.output[4]), 5000.0)
                #plt.plot([f(x) for x in t])
                #plt.show()
                g = lambda x: -f(x)
                opt = scipy.optimize.fmin(g, self.state.vm.output[4])
                print "Optimum intermediate transfer radius:", opt
                self.transferradius = opt[0]
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
            self.h = Hohmann(self.state.radius, self.transferradius)
            print self.h
            print "expected score:", score(self.h.dvt, self.initial_fuel, self.state.time+self.h.TOF+900)
            self.burntime = self.state.time
            v = Vector(self.state.vx, self.state.vy)
            d = v.normalize()
            dva = (d * self.h.dva) 
            dvax = -dva.x
            dvay = -dva.y
            print d, dva, dvax, dvay
            self.vm.input[2] = dvax
            self.vm.input[3] = dvay
        if abs(self.state.time-(self.burntime+self.h.TOF)) < 1:            
            return HohmannSim.INTERCEPT

    def intercept(self):
        v = Vector(self.state.vx, self.state.vy)
        d = v.normalize()
        dvb = (d * self.h.dvb) 
        dvbx = -dvb.x
        dvby = -dvb.y
        print d, dvb, dvbx, dvby
        self.vm.input[2] = dvbx
        self.vm.input[3] = dvby
        self.h = None
        if self.scenariotype == "Hohmann":
            print "Distance:", abs(self.transferradius-self.state.vm.output[4]), self.transferradius, self.state.vm.output[4]
            if abs(self.transferradius-self.state.vm.output[4]) > 500.0:
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
            v = Vector(self.state.vx, self.state.vy)
            d = v.normalize()
            dva = (d * self.h.dva) 
            dvax = -dva.x
            dvay = -dva.y
            print d, dva, dvax, dvay
            self.vm.input[2] = dvax
            self.vm.input[3] = dvay
        if abs(self.state.time-(self.burntime + 2.0 * self.h.TOF)) < 1:            
            return HohmannSim.INTERCEPT

def Create(problem, conf):
    return HohmannSim(problem, conf)

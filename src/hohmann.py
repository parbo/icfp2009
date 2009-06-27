from simulation import Simulation, EARTH_RADIUS
from mathutils import Hohmann
from mathutils import score
import math
from vector import Vector

class HohmannSim(Simulation):
    def __init__(self, problem=None, conf=None):
        Simulation.__init__(self, problem, conf, 'Hohmann transfer simulation')        
        self.h = None
        self.secondapplied = False

    def input(self):
        if not self.state.sx:
            return
        if not self.state.vx:
            return
        e2s = Vector(self.state.sx, self.state.sy)
        r = abs(e2s)
        tr = self.vm.output[4]
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0
        if not self.h:
            self.h = Hohmann(r, tr)
            print self.h
            print "expected score:", score(self.h.dvt, self.initial_fuel, self.h.TOF+900)
            v = Vector(self.state.vx, self.state.vy)
            d = v.normalize()
            dva = (d * self.h.dva) 
            dvax = -dva.x
            dvay = -dva.y
            print d, dva, dvax, dvay
            self.vm.input[2] = dvax
            self.vm.input[3] = dvay
        if (not self.secondapplied) and abs(self.state.time-self.h.TOF) < 1:            
            print "Applying second burn"
            v = Vector(self.state.vx, self.state.vy)
            d = v.normalize()
            dvb = (d * self.h.dvb) 
            dvbx = -dvb.x
            dvby = -dvb.y
            print d, dvb, dvbx, dvby
            self.vm.input[2] = dvbx
            self.vm.input[3] = dvby
            self.secondapplied = True
        

def Create(problem, conf):
    return HohmannSim(problem, conf)

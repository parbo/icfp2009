from simulation import Simulation, State, MeetAndGreetState, EARTH_RADIUS
from mathutils import Hohmann
from mathutils import score
import math
from vector import Vector

class HohmannSim(Simulation):
    def __init__(self, problem=None, conf=None):
        Simulation.__init__(self, problem, conf, 'Hohmann transfer simulation')        
        self.h = None
        self.firstapplied = False
        self.secondapplied = False
        self.firstapplytime = 0
        self.satx = None
        self.saty = None
        self.prevsatx = None
        self.prevsaty = None
        self.satvx = None
        self.satvy = None

    def input(self):
        e2s = Vector(self.state.sx, self.state.sy)
        r = abs(e2s)
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0

#        if self.firstapplied:
#            print "dist:", abs(e2s-Vector(self.satx, self.saty))

        if not self.firstapplied:
            applythrust = False
            if self.scenariotype == "Hohmann":
                if self.state.sx and self.state.vx:
                    tr = self.vm.output[4]
                    self.h = Hohmann(r, tr)
                    applythrust = True
            elif self.scenariotype == "MeetAndGreet":                
                sat = self.state.satellites[0]
                satpos = Vector(sat.sx, sat.sy)
                apos = Vector(self.state.sx, self.state.sy)                
                bpos = -sat.radius * apos.normalize()
                angle = bpos.angle_signed(satpos)
                while angle < 0:
                    angle += 2 * math.pi
                s = sat.radius * angle
                if sat.vx and sat.vy:
                    satv = Vector(sat.vx, sat.vy)                    
                    print "Sat pos", satpos, abs(satpos)
                    print "Sat radius", sat.radius
                    print "Sat speed", satv, abs(satv)
                    print "Angle", angle
                    if not self.h:
                        self.h = Hohmann(r, sat.radius)
                    print "Time:", s/abs(satv), self.h.TOF
                    if s > 0 and abs(s/abs(satv)-self.h.TOF) < 0.5:
                        applythrust = True            

            if applythrust:
                print self.h
                print "expected score:", score(self.h.dvt, self.initial_fuel, self.state.time+self.h.TOF+900)
                self.firstapplytime = self.state.time
                v = Vector(self.state.vx, self.state.vy)
                d = v.normalize()
                dva = (d * self.h.dva) 
                dvax = -dva.x
                dvay = -dva.y
                print d, dva, dvax, dvay
                self.vm.input[2] = dvax
                self.vm.input[3] = dvay
                self.firstapplied = True
        if self.firstapplied and not self.secondapplied and abs(self.state.time-(self.firstapplytime+self.h.TOF)) < 1:            
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

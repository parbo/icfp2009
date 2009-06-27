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
            if self.conf in [1001, 1002, 1003, 1004]:
                if self.state.sx and self.state.vx:
                    tr = self.vm.output[4]
                    self.h = Hohmann(r, tr)
                    applythrust = True
            elif self.conf in [2001, 2002, 2003, 2004]:
                self.satx = self.state.sx - self.vm.output[4]
                self.saty = self.state.sy - self.vm.output[5]
                if self.prevsatx:
                    self.satvx = self.satx - self.prevsatx
                if self.prevsaty:
                    self.satvy = self.saty - self.prevsaty
                self.prevsatx = self.satx
                self.prevsaty = self.saty
                satpos = Vector(self.satx, self.saty)
                tr = abs(satpos)
                apos = Vector(self.state.sx, self.state.sy)                
                bpos = -tr * apos.normalize()
                angle = bpos.angle_signed(satpos)
                s = tr * angle
                if self.satvx and self.satvy:
                    satv = Vector(self.satvx, self.satvy)                    
                    print "Sat pos", satpos, abs(satpos)
                    print "Sat speed", satv, abs(satv)
                    print "Angle", angle
                    self.h = Hohmann(r, tr)
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

import math 

G = 6.67428e-11
Rj = 6.357e6
Me = 6e24

class Hohmann(object):
    def __init__(self, ra, rb):
        self.ra = ra
        self.rb = rb
        self.atx = (ra+rb) / 2.0
        self.via = math.sqrt(G * Me / self.ra)
        self.vfb = math.sqrt(G * Me / self.rb)
        self.vtxa = math.sqrt(G * Me * ((2.0 / self.ra) - (1.0 / self.atx)))
        self.vtxb = math.sqrt(G * Me * ((2.0 / self.rb) - (1.0 / self.atx)))
        self.dva = self.vtxa-self.via        
        self.dvb = self.vfb-self.vtxb
        self.dvt = self.dva + self.dvb

    def __str__(self):
        tmp = []
        tmp.append("Radius A: %f"%self.ra)        
        tmp.append("Radius B: %f"%self.rb)
        tmp.append("Semi-major axis of transfer ellipse: %f"%self.atx)
        tmp.append("Initial velocity at point A: %f"%self.via)
        tmp.append("Final velocity at point B: %f"%self.vfb)
        tmp.append("Velocity on transfer orbit at initial orbit (point A): %f"%self.vtxa)
        tmp.append("Velocity on transfer orbit at final orbit (point B): %f"%self.vtxb)
        tmp.append("Initial velocity change: %f"%self.dva)
        tmp.append("Final velocity change: %f"%self.dvb)
        tmp.append("Total velocity change: %f"%self.dvt)
        return "\n".join(tmp)

if __name__=="__main__":
    h = Hohmann(Rj + 100000, Rj + 200000)
    print h







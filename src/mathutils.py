import math 

G = 6.67428e-11
Rj = 6.357e6
Me = 6e24

def clamp(val, minval, maxval):
    return max(min(val, maxval), minval)

def score(frem, fstart, t):
    return 25 + 45 * (frem/fstart) + (30 - math.log(t/1000, 2))

class OrbitTransfer(object):
    def __init__(self, ra, rb, atx):
        self.ra = ra
        self.rb = rb
        self.atx = atx
        self.vtxa = math.sqrt(G * Me * ((2.0 / self.ra) - (1.0 / self.atx)))
        self.vtxb = math.sqrt(G * Me * ((2.0 / self.rb) - (1.0 / self.atx)))
        self.via = math.sqrt(G * Me / self.ra)
        self.vfb = math.sqrt(G * Me / self.rb)

    def __str__(self):
        tmp = []
        tmp.append("ra, radius A: %f"%self.ra)        
        tmp.append("rb, radius B: %f"%self.rb)
        tmp.append("atx, semi-major axis of transfer ellipse: %f"%self.atx)
        tmp.append("via, initial velocity at point A: %f"%self.via)
        tmp.append("vfb, final velocity at point B: %f"%self.vfb)
        tmp.append("vtxa, velocity on transfer orbit at initial orbit (point A): %f"%self.vtxa)
        tmp.append("vtxb, velocity on transfer orbit at final orbit (point B): %f"%self.vtxb)
        return "\n".join(tmp)

class Hohmann(OrbitTransfer):
    def __init__(self, ra, rb):
        self.atx = (ra+rb) / 2.0
        OrbitTransfer.__init__(self, ra, rb, self.atx)
        self.dva = self.vtxa-self.via        
        self.dvb = self.vfb-self.vtxb
        self.dvt = self.dva + self.dvb
        self.TOF = math.pi * math.sqrt(((self.ra+self.rb)**3)/(8.0*G*Me))

    def __str__(self):
        tmp = ["Hohmann orbital transfer"]
        tmp.append(OrbitTransfer.__str__(self))
        tmp.append("dva, initial velocity change: %f"%self.dva)
        tmp.append("dvb, final velocity change: %f"%self.dvb)
        tmp.append("dvt, total velocity change: %f"%self.dvt)
        tmp.append("TOF, time-of-flight: %f"%self.TOF)
        return "\n".join(tmp)

class TangentBurn(OrbitTransfer):
    def __init__(self, ra, rb, atx):
        OrbitTransfer.__init__(self, ra, rb, atx)
        self.e = 1.0 - self.ra / self.atx
        tmp = (((self.atx * (1.0 - self.e**2)) / self.rb) - 1.0) / self.e
        tmp = clamp(tmp, -1.0, 1.0)
        self.ny = math.acos(tmp)
        self.phi = math.atan(self.e * math.sin(self.ny) / (1.0 + self.e * math.cos(self.ny)))
        self.dva = self.vtxa-self.via        
        self.dvb = math.sqrt(self.vtxb**2 + self.vfb**2 - 2.0 * self.vtxb * self.vfb * math.cos(self.phi))
        self.dvt = self.dva + self.dvb
        tmp1 = math.sqrt(1.0 - self.e**2) * math.sin(self.ny)
        tmp2 = self.e + math.cos(self.ny)
        self.E = math.atan(tmp1 / tmp2)
        while self.E < 0.0:
            self.E += math.pi
        self.TOF = (self.E - self.e * math.sin(self.E)) * math.sqrt(self.atx**3 / (G * Me))

    def __str__(self):
        tmp = ["TangentBurn orbital transfer"]
        tmp.append(OrbitTransfer.__str__(self))
        tmp.append("e, eccentricity of transfer ellipse: %f"%self.e)
        tmp.append("ny, true anomaly at second burn: %f"%self.ny)
        tmp.append("phi, flight-path angle at second burn: %f"%self.phi)
        tmp.append("dva, initial velocity change: %f"%self.dva)
        tmp.append("dvb, final velocity change: %f"%self.dvb)
        tmp.append("dvt, total velocity change: %f"%self.dvt)
        tmp.append("E, eccentric anomaly: %f"%self.E)        
        tmp.append("TOF, time-of-flight: %f"%self.TOF)
        return "\n".join(tmp)                             

if __name__=="__main__":
    h = Hohmann(Rj + 100000, Rj + 200000)
    tb = TangentBurn(Rj + 100000, Rj + 200000, Rj + 160000)
    tb2 = TangentBurn(Rj + 200000, 42164170, 30000000)
    print h
    print
    print tb
    print
    print tb2







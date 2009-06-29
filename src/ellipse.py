import math
from vector import Vector

Me = 6e24
Re = 6.357e6
G = 6.67428e-11
GMe = G * Me

def sign(x):
    return 1.0 if x >= 0 else -1.0
    
def eccentric_anomaly(angle, e):
    return math.acos((e + math.cos(angle)) / (1 + e * math.cos(angle)))
    
def mean_anomaly(E, e):
    return E - e * math.sin(E)

def create(vr, vv):
    """
    Create ellipse object from:
    vr - Position vector relative earth.
    vv - Velocity vector relative earth.
    """
    h = vr.cross(vv)
    r = abs(vr)
    v = abs(vv)
    # Semi-major axis length.
    a = 1.0 / (2 / r - v ** 2 / GMe)
    # Semi-minor axis length.
    b = abs(h) * math.sqrt(a / GMe)
    c = math.sqrt(a ** 2 - b ** 2)
    # Angle between position and velocity vectors.
    apv = vr.angle_signed(vv)
    #apv = apv if apv < math.pi / 2 else math.pi - apv
    # Other focus point.
    f = vr + (2 * a - r) * vv.rotate(apv).normalize()
    # Ellipse axis angle.
    ea = f.direction()
    # Center
    vc = 0.5 * f
    x, y = vc.point()
    return Ellipse(x, y, a, b, ea, h, f)

class Ellipse(object):
    def __init__(self, x, y, major, minor, angle, angular_momentum, focus):
        self.x = x                  # Center point x.
        self.y = y                  # Center point y.
        self.a = major              # Length of semi-major axis.
        self.b = minor              # Length of semi-minor axis.
        self.angle = angle          # Angle between major axis and x axis.
        self.angular_momentum = angular_momentum
        # Distance from center to foci.
        self.c = math.sqrt(self.a ** 2 - self.b ** 2)
        self.e = self.c / self.a    # Excentricity.
        self.secondary_focus = focus
        
    def __str__(self):
        return 'Ellipse(%f, %f, %f, %f, %f)' % (self.x, self.y, self.a, self.b, self.angle)
        
    @property
    def orbit_period(self):
        return 2 * math.pi * math.sqrt(self.a ** 3 / GMe)

    def angle_past_perigee(self, pos):
            # angle past perigee
        vperigee = -1.0 * self.secondary_focus
        angle = vperigee.angle_signed(pos)
        if self.angular_momentum < 0.0:
            angle = -angle
        return angle

    def time_to_perigee(self, pos):
        angle = self.angle_past_perigee(pos)
            
        if angle < 0.0:
            t = -self.time(angle, 0.0)
        else:
            t = self.orbit_period / 2.0 + self.time(angle, math.pi)            
        return t
        
    def time(self, start, end):
        ''' Calculate time to travel from angle start to angle end. '''
        # Ref: http://www.braeunig.us/space/problem.htm#4.11
        E = eccentric_anomaly(end, self.e)
        E0 = eccentric_anomaly(start, self.e)
        M = mean_anomaly(E, self.e)
        M0 = mean_anomaly(E0, self.e)
        return (M - M0) * self.orbit_period / (2 * math.pi)
        
    def points(self, n=100):
        ang = [2 * k * math.pi / n for k in range(n)]
        p = [Vector(self.a * math.cos(w), self.b * math.sin(w)) for w in ang]
        return [(v.rotate(self.angle) + Vector(self.x, self.y)).point() for v in p]
        
if __name__ == '__main__':
    ellipse = create(2 * Re * Vector(1, 1).normalize(), 6000 * Vector(-1, 1).normalize())
    print ellipse
    print 'c =', ellipse.c
    print 'e =', ellipse.e
    print
    print ellipse.time(0, math.pi / 4)

import math
from vector import Vector

Me = 6e24
Re = 6.357e6
G = 6.67428e-11
GMe = G * Me

def sign(x):
    return 1.0 if x >= 0 else -1.0

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
    f = vr + (2 * a - r) * vr.rotate(2 * apv).normalize()
    # Ellipse axis angle.
    ea = math.pi - f.direction()
    # Center
    vc = 0.5 * f
    x, y = vc.point()
    return Ellipse(x, y, a, b, ea)

class Ellipse(object):
    def __init__(self, x, y, major, minor, angle):
        self.x = x                  # Center point x.
        self.y = y                  # Center point y.
        self.a = major              # Length of semi-major axis.
        self.b = minor              # Length of semi-minor axis.
        self.angle = angle          # Angle between major axis and x axis.
        # Distance from center to foci.
        self.c = math.sqrt(self.a ** 2 - self.b ** 2)
        self.e = self.c / self.a    # Excentricity.
        
    def __str__(self):
        return 'Ellipse(%f, %f, %f, %f, %f)' % (self.x, self.y, self.a, self.b, self.angle)
        
    def orbit_period(self):
        return 2 * math.pi * math.sqrt(self.a ** 3 / GMe)
        
    def points(self, n=100):
        ang = [2 * k * math.pi / n for k in range(n)]
        p = [Vector(self.a * math.cos(w), self.b * math.sin(w)) for w in ang]
        return [(v.rotate(self.angle) + Vector(self.x, self.y)).point() for v in p]
        
if __name__ == '__main__':
    ellipse = create(2 * Re * Vector(1, 1).normalize(), 6000 * Vector(-1, 1).normalize())
    print ellipse
    print 'c =', ellipse.c
    print 'e =', ellipse.e
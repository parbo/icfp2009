import math

class Vector(object):
    def __init__(self, x, y = None):
        if isinstance(x, tuple):
            x, y = x
        self.x = float(x)
        self.y = float(y)
        
    def __str__(self):
        return 'Vector(' + str(self.x) + ', ' + str(self.y) + ')'
        
    def __mul__(self, other):
        if isinstance(other, Vector):
            # Dot product.
            return self.x * other.x + self.y * other.y
        elif isinstance(other, int) or isinstance(other, float):
            # Element product.
            return Vector(other * self.x, other * self.y)
        else:
            raise TypeError
        
    def __rmul__(self, other):
        return self * other
        
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            raise TypeError
            
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            raise TypeError
            
    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
        
    def normalize(self):
        a = abs(self)
        return Vector(self.x / a, self.y / a)
        
    def rotate(self, angle):
        return Vector(self.x * math.cos(angle) - self.y * math.sin(angle), self.x * math.sin(angle) + self.y * math.cos(angle))
        
    def angle(self, other):
        return math.acos(self * other / (abs(self) * abs(other)))

    def angle_signed(self, other):
        a = self.angle(other)
        cross = self.x * other.y - self.y * other.x
        if cross > 0.0:
            return a
        return -a

    def point(self):
        return (self.x, self.y)           

ITYPE_ENTER = 0
ITYPE_EXIT = 1

def intersection(start_vector, goal_vector, center, radius):
    xc, yc = center
    # Vector pointing at center:
    vc = Vector(xc, yc)
    # Vector (start->goal):
    vsg = (goal_vector - start_vector)
    # Normalized vector (start->goal):
    vsgn = vsg.normalize()
    # Vector (start->center):
    vsc = vc - start_vector
    # Intersection test:
    s = vsgn * vsc
    if s < 0:
        return False
    m2 = abs(vsc) ** 2 - s ** 2
    r2 = radius ** 2
    if m2 >= r2:
        return False
    q = math.sqrt(r2 - m2)
    lvsg = abs(vsg)
    intersections = []
    if s - q < lvsg:
        intersections.append((s - q, ITYPE_ENTER))
    if s + q < lvsg:
        intersections.append((s + q, ITYPE_EXIT))
    return intersections

if __name__ == '__main__':
    v1 = Vector(1, 2)
    v2 = Vector(4, 5)
    v3 = Vector(1, 0)
    v4 = Vector(1, 1)
    print 'v1 =', v1
    print 'v2 =', v2
    print 'v3 =', v3
    print 'v4 =', v4
    print 'v1 + v2 =', v1 + v2
    print 'v1 - v2 =', v1 - v2
    print 'v1 * v2 =', v1 * v2
    print '2 * v1 =', 2 * v1
    print 'v2 * 0.5 =', v2 * 0.5
    print 'abs(v1) =', abs(v1)
    print 'v1.normalize() =', v1.normalize()
    print 'abs(v1.normalize()) =', abs(v1.normalize())
    print 'v3.rotate(pi / 2) =', v3.rotate(math.pi / 2)
    print 'v3.rotate(pi / 4) =', v3.rotate(math.pi / 4)
    print 'v3.rotate(-pi / 4) =', v3.rotate(-math.pi / 4)
    print 'v3.angle(v4) =', v3.angle(v4)
    print 'v4.angle(v3) =', v4.angle(v3)

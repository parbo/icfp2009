import matplotlib.pyplot as plt
import numpy as np

import ellipse
import math
from vector import Vector

def time_to_perigee(e, angle):
    if angle < 0.0:
        t = -e.time(angle, 0.0)
    else:
        t = e.orbit_period / 2.0 + e.time(angle, math.pi)            
    return t


def f(t):
    e = ellipse.create(Vector(10000000.0, 0.0), Vector(0.0, -5000.0))
    return time_to_perigee(e, t)
    
e = ellipse.create(Vector(10000000.0, 0.0), Vector(0.0, -5000.0))
print e.orbit_period
t = np.arange(-math.pi, math.pi, 0.1)
#plt.plot(t, (f(bla) for bla in t))
plt.plot(t, [f(bla) for bla in t])
plt.show()

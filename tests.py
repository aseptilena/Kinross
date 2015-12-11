#!/usr/bin/env python3.5
# Tests for the Kinback library. The expected output is on right.
from kinback.ellipse import *
from kinback.pathery import *
from kinback.affines import *
import time
celestia = parsepath("m2.9-.4c.9-.5 1.7-.7 2 .4s1.5.8 1.2-.2c.6.7.2 1.6-.8 1.8s-1.4-1-2.8 0") # where the name comes from it being part of my vector of Princess Celestia's cutie mark
print(prettypath(celestia)) # <2.9,-.4 3.8,-.9 4.6,-1.1 4.9,0> <4.9,0 5.2,1.1 6.4,.8 6.1,-.2> <6.1,-.2 6.7,.5 6.3,1.4 5.3,1.6> <5.3,1.6 4.3,1.8 3.9,.6 2.5,1.6>
print(pathbounds(celestia)) # ((2.500000000000001-0.8023751982484958j), (6.38190799272728+1.6229638212934947j))
print(pathlength(celestia)) # 10.191302138062914
print()
# Performance tests for arc length of Bézier curves. The required time depends on "curvature variation" (reflected in inflection point and self-intersection count).
b0 = bezier(0, 3j, 3j, 5) # 0
b1 = bezier(0, 3j, 0, 5) # 1
b2 = bezier(0, 3j, -1+1j, 5) # 2
bl = bezier(0, 3j, -2, 5) # loop
for b in (b0, b1, b2, bl):
    start = time.perf_counter()
    for q in range(100): l = b.length()
    end = time.perf_counter()
    print(l) # 7.504871040167711, 6.4788922059020155, 6.879770127854843, 6.982407360576698
    print((end - start) * 10) # Approximate times in milliseconds for a Lenovo U41: 3.5, 4.5, 5, 16 (TODO implement self-intersection detection)

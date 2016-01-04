#!/usr/bin/env python3.5
# Tests for the Kinback library. The expected output is on right.
from kinback.pathery import *
import time
celestia = parsepath("m2.9-.4c.9-.5 1.7-.7 2 .4s1.5.8 1.2-.2c.6.7.2 1.6-.8 1.8s-1.4-1-2.8 0") # part of my Princess Celestia cutie mark vector
print(prettypath(celestia)) # <2.9,-.4 3.8,-.9 4.6,-1.1 4.9,0> <4.9,0 5.2,1.1 6.4,.8 6.1,-.2> <6.1,-.2 6.7,.5 6.3,1.4 5.3,1.6> <5.3,1.6 4.3,1.8 3.9,.6 2.5,1.6>
print(pathbounds(celestia)) # ((2.500000000000001-0.8023751982484959j), (6.38190799272728+1.622963821293495j))
print(pathlength(celestia)) # 10.191302138062916
# Performance tests for arc length of Bézier curves. The comments immediately below show the expected output for the first line in the loop (curve kind).
b0 = bezier(0, 3j, 3j, 5) # (0, [])
b1 = bezier(0, 3j, 0, 5) # (1, [0, 0.5])
b2 = bezier(0, 3j, -1+1j, 5) # (2, [0.16233115592918057, 0.5435511970119958])
bl = bezier(0, 3j, -2, 5) # (-1, [0.2005445095326301, 0.4869554904673699])
for b in (b0, b1, b2, bl):
    print(b.kind())
    start = time.perf_counter()
    for q in range(100): l = b.length()
    end = time.perf_counter()
    print(l) # 7.504871040167711, 6.4788922059020155, 6.879770127854842, 6.982407360576694
    print((end - start) * 10) # Approximate times in milliseconds for a Lenovo U41: 3.4, 4.3, 5, 9
print(b2.projection(0.3+1j)) # 0.1387419826232051

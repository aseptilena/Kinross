#!/usr/bin/env python3.5
# Stress tests for the Kinback library (times are for the computer I use, a Lenovo U41)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com

# Bézier curve arc length
from kinback.pathery import *
from kinback.algebra import *
import time
b0 = bezier(0, 3j, 3j, 5) # (0, [])
b1 = bezier(0, 3j, 0, 5) # (1, [0, 0.5])
b2 = bezier(0, 3j, -1+1j, 5) # (2, [0.16233115592918057, 0.5435511970119958])
bl = bezier(0, 3j, -2, 5) # (-1, [0.2005445095326301, 0.4869554904673699])
for b in (b0, b1, b2, bl):
    print(b.kind())
    start = time.perf_counter()
    for q in range(100): l = b.length()
    end = time.perf_counter()
    print(l) # 7.504871040167711, 6.4788922059020155, 6.879770127854842, 6.982407360576692
    print((end - start) * 10, "ms / length") # 1.6, 2, 2.3, 4 ms

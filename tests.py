#!/usr/bin/env python3.5
# Stress tests for the Kinback library (times are for the computer I use, a Lenovo U41)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com

# Bézier curve arc length
from kinback.pathery import *
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

parsepath("M -12.8,27 C -23.9,10.4 -3.2,7.85 -3.2,0.2 s -21.9,-10.5 -5.4,-26.6 H 11.5 C 24.2,-5.8 3.9,-7.1 3.9,0.4 s 20.9,7 10.7,26.9 z")
parsepath("m -10.7,26.1 c -8.4,-18.2 10,-16 10,-24.9 0,-7.6 -10.2,-9.5 -10.8,-18.9 0,0 10.9,-2.1 22.9,0.6 -1.5,10 -9.7,10.1 -9.7,17.4 0,10.3 17.1,8.2 10.1,25 z")
parsepath("m 16.9,-21.6 s -15.8,-3 -31.8,-1.3 v -9.2 s 13.2,-2.9 31.8,2 z m 3,45.8 s -28.5,-0.1 -39.8,1 l 1,7.4 s 24.3,0.7 37.6,-0.1 z")
parsepath("m -6.9,-22.3 s -4.4,-4.5 -1.1,-11 H 3 s -4,6.1 -0.6,11.2 z M -9.8,24 s -3.7,5.1 0.5,9.6 h 10 s -4.3,-3.7 0.2,-9.8 z")

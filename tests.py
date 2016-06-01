#!/usr/bin/env python3.5
# Stress tests for the Kinback library (times are for the computer I use, a Lenovo U41)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com

# Bézier curve arc length
'''from kinback.pathery import *
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
    print(l) # 7.504871040167711, 6.4788922059020155, 6.879770127854844, 6.982407360576693
    print((end - start) * 10, "ms / length") # 3.4, 4.3, 5, 9 ms

print()
# Random number generation
from kinback.discord import KinrossRandom
rr, bbins = KinrossRandom(), [0 for q in range(33)]
start = time.perf_counter()
for q in range(100000): bbins[rr.binomialvariate(32, 0.6)] += 1
end = time.perf_counter()
print(bbins[19], sum([n * bbins[n] for n in range(len(bbins))]) / 100000) # Mode and mean (14205 and 19.2 expected)
print((end - start) * 10, "μs / binomial variate") # 26 μs

d = {}
start = time.perf_counter()
for q in range(100000):
    v = rr.poissonvariate(24)
    d[v] = d.get(v, 0) + 1
end = time.perf_counter()
print(d) # 24 should have the largest associated value, since it is the mean
print((end - start) * 10, "μs / Poisson variate") # 28 μs'''
from kinback.affines import tf
print(tf.minstr("matrix(-0.81996625,-0.2160501,-0.2160501,0.81996625,271.27629,-39.763406)")) # rotate(194.76117 133.06281-37.451292)scale(.84795182-.84795182)

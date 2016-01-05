#!/usr/bin/env python3.4
# Script for magically generating pony colour schemes.
# They may not make sense from a colour harmony perspective and they don't come with highlights,
# but at least they're good starts.
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
import random, sys
from cmath import rect
rng = random.SystemRandom()

def lx(k): return k ** 3 if k > 6 / 29 else 108 / 841 * (k - 4 / 29)
def xr(k): return 12.92 * k if k <= 0.0031308 else 1.055 * k ** (1 / 2.4) - 0.055
def lch2rgb(l, c, h): # Converts CIELCH to sRGB and returns the latter as a hex value… if it's valid
    # CIELCH → CIELAB
    ab = rect(c, h)
    a, b = ab.real, ab.imag
    # CIELAB → CIEXYZ
    j = (l + 16) / 116
    x, y, z = 0.95047 * lx(j + a / 500), lx(j), 1.08883 * lx(j - b / 200)
    # CIEXYZ → sRGB
    rgb = [xr(3.24062548 * x - 1.53720797 * y -  .49862860 * z),
           xr(-.96893071 * x + 1.87575606 * y +  .04151752 * z),
           xr( .05571012 * x -  .20402105 * y + 1.05699594 * z)]
    if 0 <= rgb[0] <= 1 and 0 <= rgb[1] <= 1 and 0 <= rgb[2] <= 1: return "".join(["{:02x}".format(round(n * 255)) for n in rgb])

coatcons = (((5.5, 1.3), (2.5, 1 / 8.2), (1.8, 7.7), (5.0, 1.1)),
            ((4.3, 1.5), (2.2, 1 / 7.5), (1.5, 8.6), (4.7, 1.1)))
manecons = (((2.8, 1.4), (2.9, 1 / 7.1), (5.5, 5.4), (2.0, 0.7)),
            ((1.6, 1.1), (1.5, 1 / 4.6), (1.4, 4.1), (4.8, 1.4)))
eyescons = (((4.2, 2.4), (5.4, 1 /11.8), (5.4,  25), (6.0, 109), (2.7, 0.6)),
            ((4.4, 2.2), (4.3, 1 / 9.5), (1.6,  69), (2.3,  43), (4.6, 1.1)))
def coatgen(gender):
    nums, col = coatcons[gender], None
    while col == None:
        l, c, p = rng.betavariate(*nums[0]), rng.gammavariate(*nums[1]), rng.randrange(7)
        h = rng.vonmisesvariate(*nums[2 if p < 3 else 3])
        col = lch2rgb(l * 100, c * 100, h)
    return col
def manegen(gender):
    nums, col = manecons[gender], None
    while col == None:
        l, c, p = rng.betavariate(*nums[0]), rng.gammavariate(*nums[1]), rng.randrange(7)
        h = rng.vonmisesvariate(*nums[2 if p < 3 else 3])
        col = lch2rgb(l * 100, c * 100, h)
    return col
def eyesgen(gender):
    nums, col = eyescons[gender], None
    while col == None:
        l, c, p = rng.betavariate(*nums[0]), rng.gammavariate(*nums[1]), rng.randrange(5)
        h = rng.vonmisesvariate(*nums[2 if p == 0 else (3 if p == 1 else 4)])
        col = lch2rgb(l * 100, c * 100, h)
    return col

if len(sys.argv) != 3 or not sys.argv[1].isdecimal() or not sys.argv[2].isdecimal():
    print("Usage: " + sys.argv[0] + " [number of mares] [number of stallions]")
    sys.exit(1)
mares, stallions = max(int(sys.argv[1]), 0), max(int(sys.argv[2]), 0)
if mares:
    print("Mare colours (coat, mane, eyes):")
    for q in range(mares): print("#{}, #{}, #{}".format(coatgen(0), manegen(0), eyesgen(0)))
if stallions:
    print("Stallion colours (coat, mane, eyes):")
    for q in range(stallions): print("#{}, #{}, #{}".format(coatgen(1), manegen(1), eyesgen(1)))

#!/usr/bin/env python3.4
# A starfield generator - insanely good for something almost looking bootstrapped.
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import sys, os, random
sys.path.append(os.path.abspath("./utilities")) # When the script is run in-place in the Kinross folder
sys.path.append(os.path.abspath("../utilities")) # or in a folder containing the utilities as a sub-folder,
from filestamps import timestamp                # these three lines ensure the last import occurs successfully.

def star(d = 3, m = 6, b = 3.5, s = 1.5):
    # d = decay rate (how many times less frequent the next lower magnitude of star is)
    # m = number of possible magnitudes
    # b = radius of the lowest-magnitude (N = 0) star
    # s = step in radius between adjacent-magnitude stars
    r, N = random.SystemRandom(), 0
    while r.random() < 1 / d: N += 1
    return '<circle cx="{0}" cy="{1}" r="{2}"/>\n'.format(round(r.random() * 1000, 3), round(r.random() * 1000, 3), s * min(m - 1, N) + b)

d = input("Decay rate (default 3)? ")
d = 3 if d == "" else float(d)
m = input("Number of magnitudes (default 6)? ")
m = 6 if m == "" else int(m)
b = input("Radius of smallest star (default 3.5)? ")
b = 3.5 if b == "" else float(b)
s = input("Radius difference between adjacent-magnitude stars (default 1.5)? ")
s = 1.5 if s == "" else float(s)
r = input("Number of stars to write to 1000*1000 square (default 250)? ")
r = 250 if r == "" else int(r)
c = input("Colour of stars (default #b4a8fe)? ")
c, p = "b4a8fe" if c == "" else c, ""
if len(c) == 8:
    o = int(c[-2:], 16)
    p = "" if o == 255 else ' fill-opacity="{0}"'.format(o / 255)
with open(timestamp("starfield.svg"), 'w') as out:
    out.write('<svg><g fill="#{0}"{1}>'.format(c[:6], p))
    for i in range(r): out.write(star(d, m, b, s))
    out.write("</g></svg>")

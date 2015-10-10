#!/usr/bin/env python3.5
# Starfield generator with circles, meant primarily for MLPFIM but generalisable to other areas
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import random
from kinback.miscellanea import datestamp, xmlprettyprint
import xml.etree.ElementTree as t
z = t.ElementTree(t.fromstring("<svg><g/></svg>"))
sg = z.find("g")

def star(d, m, b, s):
    # d = decay rate (how many times less frequent the next lower magnitude of star is)
    # m = number of possible magnitudes
    # b = radius of the lowest-magnitude (N = 0) star
    # s = step in radius between adjacent-magnitude stars
    r, N = random.SystemRandom(), 0
    while r.random() < 1 / d: N += 1
    return t.Element("circle", {"cx": str(round(r.random() * 1000, 3)), "cy": str(round(r.random() * 1000, 3)), "r": str(s * min(m - 1, N) + b)})

d = input("Decay rate (default 3)? ") # spallator: distribution settings on command line (scaling with geometric distro)
d = 3 if d == "" else float(d)
m = input("Number of magnitudes (default 6)? ") # ditto
m = 6 if m == "" else int(m)
b = input("Radius of smallest star (default 3.5)? ") # spallator: in canvas
b = 3.5 if b == "" else float(b)
s = input("Radius difference between adjacent-magnitude stars (default 1.5)? ") # spallator: same as #1 and #2
s = 1.5 if s == "" else float(s)
r = input("Number of stars to write to 1000*1000 square (default 250)? ") # spallator: density
r = 250 if r == "" else int(r)
c = input("Colour of stars (default #b4a8fe)? ") # spallator: in canvas
c, p = "b4a8fe" if c == "" else c, 255
if len(c) == 8: p = int(c[-2:], 16)
with open(datestamp("starfield.svg"), 'w') as out:
    sg.set("fill", "#" + c[:6])
    for i in range(r): sg.append(star(d, m, b, s))
    out.write(xmlprettyprint(z))

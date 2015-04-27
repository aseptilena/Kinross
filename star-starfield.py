#!/usr/bin/env python3.4
# For those who love diffraction spikes...
import random, time
from math import pi

def star(d, m, b, s, sp, sr):
    r, N = random.SystemRandom(), 0
    while r.random() < 1 / d: N += 1
    M, th = s * min(m - 1, N) + b, 2 * r.random() * pi / sp
    return '<path sodipodi:type="star" sodipodi:sides="{0}" sodipodi:cx="{1}" sodipodi:cy="{2}" sodipodi:r1="{3}" sodipodi:r2="{4}" sodipodi:arg1="{5}" sodipodi:arg2="{6}"/>\n'.format(sp, round(r.uniform(0, 1000), 3), round(r.uniform(0, 1000), 3), M, M * sr, th, th + pi / sp)

d = input("Decay rate (default 2.5)? ")
d = 2.5 if d == "" else float(d)
m = input("Number of magnitudes (default 5)? ")
m = 5 if m == "" else int(m)
b = input("Radius of smallest star (default 5)? ")
b = 5 if b == "" else float(b)
s = input("Radius difference between adjacent-magnitude stars (default 5)? ")
s = 5 if s == "" else float(s)
sp = input("Number of spokes for each star (default 4)? ")
sp = 4 if sp == "" else int(sp)
sr = input("Spoke ratio (default 0.125)? ")
sr = 0.125 if sr == "" else float(sr)
r = input("Number of stars to write to 1000*1000 square (default 150)? ")
r = 150 if r == "" else int(r)
c = input("Colour of stars (default #b6ecff)? ")
c, p = "b6ecff" if c == "" else c, ""
if len(c) == 8:
    o = int(c[-2:], 16)
    p = "" if o == 255 else ' fill-opacity="{0}"'.format(o / 255)
with open("starfield-{0}.svg".format(time.strftime("%Y-%m-%d-%H-%M-%S")), 'w') as out:
    out.write('<svg xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"><g fill="#{0}"{1}>'.format(c[:6], p))
    for i in range(r): out.write(star(d, m, b, s, sp, sr))
    out.write("</g></svg>")

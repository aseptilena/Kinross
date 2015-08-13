#!/usr/bin/env python3.4
# Helper functions for Kinross: ellipses
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import * # local
from math import pi, sqrt, fabs

hpi = pi / 2
# Ellipses have a centre, two axis lengths and the signed angle from +x to semi-first axis. This last angle is normalised to (-pi/2, pi/2].
class ellipse:
    def __init__(self, centre, rx, ry, tilt = 0.):
        self.centre, self.rx, self.ry = centre, fabs(rx), fabs(ry)
        self.tilt = tilt - pi * int(tilt / pi) # (-pi, pi)
        if self.tilt <= -hpi: self.tilt += pi
        if self.tilt > hpi: self.tilt -= pi
    def __str__(self): return "Ellipse centred on {0} with axes {1} and {2}, the first axis tilted by {3}".format(ppp(self.centre), self.rx, self.ry, self.tilt)
    def __repr__(self): return "ellipse(point{0}, {1}, {2}, {3})".format(ppp(self.centre), self.rx, self.ry, self.tilt)
    def a(self): return max(self.rx, self.ry) # semi-major axis length
    def b(self): return min(self.rx, self.ry) # semi-minor axis length
    
    def smaj(self): return rect(self.a(), self.tilt + hpi * (self.rx <  self.ry))
    def smin(self): return rect(self.b(), self.tilt + hpi * (self.rx >= self.ry))
    def f(self): return sqrt(abs(self.rx * self.rx - self.ry * self.ry)) # distance from centre to either focus
    def e(self): return self.f() / self.a()
    def foci(self):
        fv = rect(self.f(), self.tilt + hpi * (self.rx < self.ry))
        return (self.centre + fv, self.centre - fv)

# Rytz's construction for finding axes from conjugated diameters or equivalently a transformed rectangle.
# Used to remove the transformation matrix from SVG ellipses.
def rytz(centre, a, b):
    if near(dot(a, b, centre), 0.): return ellipse(centre, abs(a - centre), abs(b - centre), phase(a - centre))
    else:
        c = rturn(a, centre)
        m = between(b, c)
        d = abs(m - centre)
        mb, mc = lhat(b, d, m), lhat(c, d, m)
        v1, v2 = lhat(mb, abs(mc - b), centre), lhat(mc, abs(mb - b), centre)
        return ellipse(centre, abs(v1 - centre), abs(v2 - centre), phase(v1 - centre))

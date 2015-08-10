#!/usr/bin/env python3.4
# Helper functions for Kinross: ellipses
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from vectors import *
from math import pi, sqrt

hpi = pi / 2
# The representation here has a point for its centre, two numbers for the axis lengths
# and the signed angle from +x to centre to a semi-rx axis point.
# This last angle is normalised to (-pi/2, pi/2]; positive on ry is then a +90 degrees rotation from the rx ray.
class Ellipse:
    def __init__(self, centre, rx, ry, tilt = 0.):
        self.centre, self.rx, self.ry = centre, float(rx), float(ry)
        self.tilt = tilt - pi * int(tilt / pi) # (-pi, pi)
        if self.tilt <= -hpi: self.tilt += pi
        if self.tilt > hpi: self.tilt -= pi
    def __str__(self): return "Ellipse with centre {0} and axes {1}/{2}, the first tilted by {3} to +x axis".format(self.centre, self.rx, self.ry, self.tilt)
    def __repr__(self): return "Ellipse({0}, {1}, {2}, {3})".format(repr(self.centre), self.rx, self.ry, self.tilt)
    
    def a(self): return max(self.rx, self.ry) # semi-major length
    def b(self): return min(self.rx, self.ry) # semi-minor length
    def semaja(self): return Point(self.a(), self.tilt + hpi * (self.rx <  self.ry), True)
    def semina(self): return Point(self.b(), self.tilt + hpi * (self.rx >= self.ry), True)
    def f(self): return sqrt(abs(self.rx * self.rx - self.ry * self.ry)) # distance from centre to either focus
    def e(self): return self.f() / self.a()
    def foci(self):
        fv = Point(self.f(), self.tilt + hpi * (self.rx < self.ry), True)
        return (self.centre + fv, self.centre - fv)

# Rytz's construction for finding axes from conjugated diameters, equivalently a transformed rectangle.
# Used to remove the transformation matrix from SVG ellipses.
def rytz(centre, a, b):
    if prox(dot(a, b, centre), 0.): return Ellipse(centre, a.dist(centre), b.dist(centre), a.dirc(centre))
    else:
        c = a.lturn(centre)
        m = midpoint(b, c)
        axav = m.dist(centre)
        mb, mc = b.lhat(axav, m), c.lhat(axav, m)
        v1, v2 = mb.lhat(mc.dist(b), centre), mc.lhat(mb.dist(b), centre)
        return Ellipse(centre, v1.dist(centre), v2.dist(centre), v1.dirc(centre))

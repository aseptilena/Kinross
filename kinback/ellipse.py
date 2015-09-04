#!/usr/bin/env python3.4
# Helper functions for Kinross: circles and ellipses
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import * # local
from .affinity import *
from math import pi, sqrt, fabs, hypot
hpi = pi / 2

# Ellipses have a centre, two axis lengths and the signed angle from +x to semi-first axis. This last angle is normalised to (-pi/2, pi/2].
class ellipse:
    def __init__(self, centre, rx, ry, tilt = 0.):
        self.centre, self.rx, self.ry = centre, fabs(rx), fabs(ry)
        self.tilt = tilt - pi * int(tilt / pi) # (-pi, pi)
        if self.tilt <= -hpi: self.tilt += pi
        if self.tilt > hpi: self.tilt -= pi
    def __str__(self): return "Ellipse centred on {} with axes {} and {}, the first axis tilted by {}".format(printpoint(self.centre), self.rx, self.ry, self.tilt)
    def __repr__(self): return "ellipse({}, {}, {}, {})".format(self.centre, self.rx, self.ry, self.tilt)
    
    def a(self): return max(self.rx, self.ry) # Semi-major axis length
    def b(self): return min(self.rx, self.ry) # Semi-minor axis length
    def a_vect(self): return rect(self.a(), self.tilt + hpi * (self.rx <  self.ry)) # Semi-major axis vector
    def b_vect(self): return rect(self.b(), self.tilt + hpi * (self.rx >= self.ry)) # Semi-minor axis vector
    def zerovertex(self): return self.centre + rect(self.rx, self.tilt) # This vertex is considered the zero point for angles
    def hpivertex(self): return self.centre + rect(self.ry, self.tilt + hpi) # The point perpendicular to the zero vertex
    def f(self): return sqrt(abs(self.rx * self.rx - self.ry * self.ry)) # Distance from centre to either focus
    def e(self): return self.f() / self.a() # Eccentricity
    def foci(self):
        fv = rect(self.f(), self.tilt + hpi * (self.rx < self.ry))
        return (self.centre + fv, self.centre - fv)
    
    def raypoint(self, p):
        """Intersection of the ray from the centre to the specified point with the ellipse.
        The Kinross elliptical arc representation uses this to determine endpoints."""
        if near(p, self.centre): return self.anglepoint()
        a = signedangle(p, self.zerovertex(), self.centre)
        r = self.rx * self.ry / hypot(self.ry * cos(a), self.rx * sin(a))
        return lenvec(p, r, self.centre)
    def anglepoint(self, th = 0.): return self.raypoint(turn(self.zerovertex(), th, self.centre))
    def tf(self, mat):
        """Transforms the ellipse by the given matrix."""
        return rytz(tf(mat, self.centre), tf(mat, self.zerovertex()), tf(mat, self.hpivertex()))
    def unitcircletf(self):
        """The transformation that maps this ellipse to the centred unit circle."""
        return composetf(scalemat(1 / self.rx, 1 / self.ry), rotmat(-self.tilt), transmat(-self.centre.real, -self.centre.imag))
    def unitcircleinvtf(self):
        """The inverse of unitcircletf() (i.e. the transformation from the unit circle to this ellipse). This is calculated separately to reduce floating-point error."""
        return composetf(transmat(self.centre.real, self.centre.imag), rotmat(self.tilt), scalemat(self.rx, self.ry))

class circle:
    """Circles are the same as ellipses, only with one radius and no tilt."""
    def __init__(self, centre = 0j, r = 1): self.centre, self.r = centre, fabs(r)
    def __str__(self): return "Circle with centre {} and radius {}".format(printpoint(self.centre), self.r)
    def __repr__(self): return "circle({}, {})".format(self.centre, self.r)
    def toellipse(self): return ellipse(self.centre, self.r, self.r) # A coercing function
    
    def raypoint(self, p): return lenvec(p, self.r, self.centre)
    def anglepoint(self, th = 0.): return self.centre + rect(self.r, th) # from the +x-axis
    def invertpoint(self, p):
        """The inversion of a point in this circle. None signifies the point at infinity."""
        if near(p, centre): return None
        return lenvec(p, self.r * self.r / abs(p - self.centre), self.centre)

def rytz(centre, a, b):
    """Rytz's construction for finding axes from conjugated diameters or equivalently a transformed rectangle.
    Used to remove the transformation matrix from SVG ellipses (and a lot of other things)."""
    if near(dot(a, b, centre)): return ellipse(centre, abs(a - centre), abs(b - centre), phase(a - centre))
    else:
        c = rturn(a, centre)
        m = between(b, c)
        d = abs(m - centre)
        mb, mc = lenvec(b, d, m), lenvec(c, d, m)
        v1, v2 = lenvec(mb, abs(mc - b), centre), lenvec(mc, abs(mb - b), centre)
        return ellipse(centre, abs(v1 - centre), abs(v2 - centre), phase(v1 - centre))

def ell5pts(a, b, c, d, e):
    pass # TODO

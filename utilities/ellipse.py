#!/usr/bin/env python3.4
# Helper functions for Kinross: ellipses
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from vectors import *
from math import pi

hpi = pi / 2
# The representation here has a point for its centre, two numbers for the axis lengths
# and the signed angle from +x to centre to a semi-rx axis point.
# This last angle is normalised to (-pi/2, pi/2]; positive on ry is a +90 degrees rotation from the rx ray.
class Ellipse:
    def __init__(self, centre, rx, ry, tilt):
        self.centre, self.rx, self.ry = centre, float(rx), float(ry)
        self.tilt = tilt - hpi * int(tilt / hpi)
        # Perturbations of 1e-16 and below change no bits
        if prox(self.tilt, -hpi, 1e-15): self.tilt = hpi
    def __str__(self): return "Ellipse with centre {0} and two axes {1} and {2}, the first axis tilted by {3} radians to the +x axis".format(self.centre, self.rx, self.ry, self.tilt)
    def __repr__(self): return "Ellipse({0}, {1}, {2}, {3})".format(repr(self.centre), self.rx, self.ry, self.tilt)
    def foci():
        pass

# Rytz's construction for finding axes from conjugated diameters
# (equivalently a centre and two points that were the intersections of the ellipse axes with the ellipse before a transformation).
# Used to remove the rotation matrix from SVG ellipses.
def rytz(centre, u, v):
    pass

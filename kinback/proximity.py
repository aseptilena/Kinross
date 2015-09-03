#!/usr/bin/env python3.4
# Helper functions for Kinross: proximities (intersections and nearest distance)
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import * # local
from .ellipse import *
# The names of intersection-finding functions here all begin with intersect_; this is followed by two letters indicating which objects it handles.
# l = line, e = ellipse/circle, r = rhythm; non-trivial solutions are returned as a tuple.

def intersect_ll(l, m, ext = False):
    """Finds the intersection of two lines. The ext parameter, if true, will allow intersections outside one or both of the line segments."""
    v, w = l[1] - l[0], m[1] - m[0]
    if not near(cross(v, w)):
        p, q = lineareq2(v.real, -w.real, (m[0] - l[0]).real, v.imag, -w.imag, (m[0] - l[0]).imag)
        if ext or 0. <= p <= 1. and 0. <= q <= 1.: return linterp(l[0], l[1], p)
    return ()

def intersect_ee(c, d):
    """Finds the intersection between two ellipses.
    The first one is transformed to a unit circle and the second is then rotated to be parallel to the axes."""
    m = c.unitcircletf()
    dp = d.tf(m)
    dpp = dp.tf(rotmat(-dp.tilt))
    # dpp's parametric equation is (cx + rx * cos(t), cy + ry * sin(t)).
    # Thus: cx^2 + 2 * cx * rx * cos(t) + rx^2 * cos^2(t) +
    #       cy^2 + 2 * cy * ry * sin(t) + ry^2 * sin^2(t) = 1
    # and how to solve this set of equations?
    pass # TODO

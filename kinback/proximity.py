# Helper functions for Kinross: proximity (nearest distances of points to shapes)
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import *
from .ellipse import *

def nearesttoline(p, l, real = True):
    """Returns the shortest distance from a point to a line (real = False) or the corresponding line segment (True).
    Note that the line, circle and ellipse are all convex functions, which makes searching for the nearest point easier."""
    if not real or dot(l[1], p, l[0]) > 0 and dot(l[0], p, l[1]) > 0: return perpdist(p, l)
    return min(abs(p - l[0]), abs(p - l[1]))

def nearesttocircle(p, c):
    """What? This is so easy?"""
    return abs(abs(p - c.centre) - c.r)

def nearesttoellipse(p, e):
    pass # TODO

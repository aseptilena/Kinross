#!/usr/bin/env python3.4
# Helper functions for Kinross: numeric functions and classical algebra
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sqrt
# Numeric functions
def near(a, b = 0., e = 1e-5):
    """Checks if the difference between two numbers is within the given tolerance (using the L2 metric for a more natural treatment of complex numbers).
    The second argument can be left out to represent zero."""
    return abs(b - a) <= e
# Algebraic functions
def lineareq2(a, b, p, c, d, q):
    """ax + by = p; cx + dy = q; returns (x, y)."""
    det = a * d - b * c
    if near(det): return (None, None)
    return ((p * d - q * b) / det, (a * q - c * p) / det)
def quadreq(a, b, c, real = True):
    """a * x ^ 2 + b * x + c = 0; real excludes complex roots"""
    d = b * b - 4 * a * c
    r, i = -b / (2 * a), sqrt(abs(d)) / (2 * a)
    if d < 0:
        if not real: return (complex(r, -i), complex(r, i))
    else: return (r - i, r + i)
    return ()
def cubeq(a, b, c, d, real = True):
    """Vieta's method, real is again self-explanatory"""
    pass # TODO

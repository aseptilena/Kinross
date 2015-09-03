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
    """Numerically stable a * x ^ 2 + b * x + c = 0; real excludes complex roots.
    See https://people.csail.mit.edu/bkph/articles/Quadratics.pdf for the derivation."""
    d = b * b - 4 * a * c
    e = sqrt(abs(d))
    if d < 0:
        if not real:
            r, i = -b / (2 * a), e / (2 * a)
            return (complex(r, -i), complex(r, i))
        return ()
    if b < 0: return (2 * c / (-b + e), (-b + e) / 2 / a)
    return ((-b - e) / 2 / a, 2 * c / (-b - e))
# To solve higher-order polynomials, we need to implement a class for them.
class polynomial:
    """A polynomial stores a list of coefficients [a0, a1, a2, ...]
    where a0 is the constant term, a1 is the x term and so on."""
    def __init__(self, coeffs):
        self.a = tuple(coeffs)
    def __str__(self): pass # TODO
    def __repr__(self): return "polynomial([" + ",".join(a) + "])"

def hornereval(p, x):
    res = 0.
    for i in range(len(p) - 1, -1, -1): res = p[i] + res * x
    return res

def cubeq(a, b, c, d, real = True):
    """Vieta's method, real is again self-explanatory"""
    pass # TODO

# Helper functions for Kinross: vector functions
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sin, cos, acos
from cmath import phase, rect, isclose

# Points in Kinross are complex numbers, but for the purposes of SVG +y is downwards and +angle is clockwise.
# For modulus, argument and polar constructors use abs, phase and rect respectively.

# Single-vector operations
def sqabs(p, q = 0j): return (p.real - q.real) * (p.real - q.real) + (p.imag - q.imag) * (p.imag - q.imag)
def hat(p, o = 0j): return o if isclose(p, o) else (p - o) / abs(p - o) + o
def lenvec(p, l, o = 0j):
    """Scales p to length l relative to o."""
    return o if isclose(p, o) else (p - o) / abs(p - o) * l + o
def turn(p, th, o = 0j): return (p - o) * complex(cos(th), sin(th)) + o
def lturn(p, o = 0j): return (o - p) * 1j + o
def rturn(p, o = 0j): return (p - o) * 1j + o
def reflect(p, o = 0j): return 2 * o - p
# Dot and cross products
# Unsigned angles, in [0, pi]; dot product maximum if OAB/OBA collinear, 0 if AOB perpendicular, minimum if AOB collinear
def dot(a, b, o = 0j): return (a.real - o.real) * (b.real - o.real) + (a.imag - o.imag) * (b.imag - o.imag)
def angle(a, b, o = 0j): return acos(dot(a, b, o) / (abs(a - o) * abs(b - o)))
def vecproject(p, base, o = 0j): return (p - o).real if isclose(base, o) else dot(p, base, o) / dot(base, base, o) * (base - o) + o 
# Signed angles, in [-pi, pi]; planar cross product maximum if A>O>B = +90 degs, minimum if = -90 degs and 0 if points collinear
def cross(a, b, o = 0j): return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
def signedangle(p, base, o = 0j): return phase((p - o) / (base - o)) # from base to o to p
def collinear(a, b, c): return isclose(cross(a, b, c), 0)
# Line functions; lines are 2-tuples of points
def between(p, q): return (p + q) / 2
def linterp(p, q, t): return t * (q - p) + p
def footperp(p, l): return vecproject(p, l[1], l[0])
def perpdist(p, l): return abs(cross(p, l[1], l[0]) / (l[1] - l[0]))
def perpbisect(a, b):
    m = between(a, b)
    return (lturn(a, m), rturn(a, m))
# Pretty printing of points and lines
def printpoint(p): return "({}, {})".format(p.real, p.imag)
def printline(l): return "Line from {} to {}".format(l[0], l[1])

# INTERMISSION: 2-variable linear equation solver and line/line intersection
def lineareq2(a, b, p, c, d, q):
    """ax + by = p; cx + dy = q; returns (x, y)."""
    det = a * d - b * c
    if isclose(det, 0.): return (None, None)
    return ((p * d - q * b) / det, (a * q - c * p) / det)
def intersect_ll(l, m, real = True):
    """Finds the intersection of two lines. real restricts to "real" intersections on both line segments that define the lines."""
    v, w = l[1] - l[0], m[1] - m[0]
    if not isclose(cross(v, w), 0):
        p, q = lineareq2(v.real, -w.real, (m[0] - l[0]).real, v.imag, -w.imag, (m[0] - l[0]).imag)
        if not real or 0. <= p <= 1. and 0. <= q <= 1.: return linterp(l[0], l[1], p)
    return None

def pointbounds(pts):
    """The orthogonal bounding box of an array of points, represented as a tuple of opposing corners."""
    xs, ys = tuple(map(lambda p: p.real, pts)), tuple(map(lambda p: p.imag, pts))
    return complex(min(xs), min(ys)), complex(max(xs), max(ys))

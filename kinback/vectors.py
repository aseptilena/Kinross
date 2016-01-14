# Helper functions for Kinross: vector functions
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
from math import sin, cos, acos
from cmath import phase, rect, isclose

# Points in Kinross are complex numbers, but for the purposes of SVG +y is downwards and +angle is clockwise.
# For modulus, argument and polar constructors use abs, phase and rect respectively.
def hat(p, o = 0j): return o if isclose(p, o) else (p - o) / abs(p - o) + o # in direction of p, length 1
def lenvec(p, l, o = 0j): return o if isclose(p, o) else (p - o) / abs(p - o) * l + o # in direction of p, length l
def turn(p, th, o = 0j): return (p - o) * complex(cos(th), sin(th)) + o
def lturn(p, o = 0j): return (o - p) * 1j + o
def rturn(p, o = 0j): return (p - o) * 1j + o
def reflect(p, o = 0j): return 2 * o - p

def dot(a, b, o = 0j): return (a.real - o.real) * (b.real - o.real) + (a.imag - o.imag) * (b.imag - o.imag)
def angle(a, b, o = 0j): return acos(dot(a, b, o) / (abs(a - o) * abs(b - o)))
def cross(a, b, o = 0j): return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
def signedangle(p, base, o = 0j): return phase((p - o) / (base - o)) # p relative to base with o as origin
def collinear(a, b, c): return isclose(cross(a, b, c), 0)

def between(p, q): return (p + q) / 2
def linterp(p, q, t): return (1 - t) * p + t * q
def perpbisect(a, b):
    m = between(a, b)
    return (lturn(a, m), rturn(a, m))
def saltire(l, m):
    """Intersects two lines to their common point – the figure looks like the Scottish cross, hence the name."""
    v, w = l[0] - l[1], m[0] - m[1]
    denom = cross(v, w)
    if abs(denom) < 1e-10: return None
    lc, mc = cross(l[0], l[1]), cross(m[0], m[1])
    return complex(lc * w.real - mc * v.real, lc * w.imag - mc * v.imag) / denom
def pointbounds(pts):
    """The orthogonal bounding box of an array of points, represented as a tuple of opposing corners."""
    xs, ys = tuple(map(lambda p: p.real, pts)), tuple(map(lambda p: p.imag, pts))
    return complex(min(xs), min(ys)), complex(max(xs), max(ys))

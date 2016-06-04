# Helper functions for Kinross: vector functions
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import sin, cos, acos
from cmath import phase, rect, isclose

# Points in Kinross are complex numbers, but for the purposes of SVG +y is downwards and +angle is clockwise.
# For modulus, argument and polar constructors use abs, phase and rect respectively.
def reflect(p, o = 0j): return 2 * o - p

def dot(a, b, o = 0j): return (a.real - o.real) * (b.real - o.real) + (a.imag - o.imag) * (b.imag - o.imag)
def angle(a, b, o = 0j): return acos(dot(a, b, o) / (abs(a - o) * abs(b - o)))
def cross(a, b, o = 0j): return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
def collinear(a, b, c): return isclose(cross(a, b, c), 0)

def linterp(p, q, t): return (1 - t) * p + t * q

def pointbounds(pts):
    """The orthogonal bounding box of an array of points, represented as a tuple of opposing corners."""
    xs, ys = tuple(map(lambda p: p.real, pts)), tuple(map(lambda p: p.imag, pts))
    return complex(min(xs), min(ys)), complex(max(xs), max(ys))

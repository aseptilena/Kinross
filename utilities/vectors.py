#!/usr/bin/env python3.4
# Helper functions for Kinross: vector geometry
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import hypot, atan2, sin, cos, acos

def prox(a, b = 0, e = 1e-5): return a - b <= e and a - b >= -e # Proximal function

# A point in the plane, equivalently a vector from the origin or complex number.
# The y-axis is downwards and positive angle is clockwise as in the SVG specs.
class Point:
    def __init__(self): # Origin
        self.x, self.y = 0.0, 0.0
    def __init__(self, iterb): # From list or tuple
        self.x, self.y = iterb[0], iterb[1]
    def __init__(self, x, y): # From Cartesian coordinates
        self.x, self.y = float(x), float(y)
    def __str__(self): return str((self.x, self.y))
    def __repr__(self): return "Point({0}, {1})".format(self.x, self.y)
    def __add__(self, that): return Point(self.x + that.x, self.y + that.y)
    def __sub__(self, that): return Point(self.x - that.x, self.y - that.y)
    def __neg__(self): return Point(-self.x, -self.y)
    def __mul__(self, that):
        if type(that) == Point: return Point(self.x * that.x - self.y * that.y, self.y * that.x + self.x * that.y)
        else: return Point(self.x * that, self.y * that)
    def __rmul__(self, that): return self * that
    def __truediv__(self, that):
        if type(that) == Point:
            n = that.x * that.x + that.y * that.y
            return Point(self.x * that.x + self.y * that.y, self.y * that.x - self.x * that.y) / n
        else: return Point(self.x / that, self.y / that)
    
    def is0(self): return prox(self.x) and prox(self.y)
    # Modulus and argument
    def md(self): return hypot(self.x, self.y)
    def md2(self): return self.x * self.x + self.y * self.y
    def th(self): return atan2(self.y, self.x)
    # Classic vector operations
    def hat(self): return self / self.md() if not self.is0() else Point(1, 0) # The normalised vector, denoted with a hat
    def lenbyhat(self, l): return self.hat() * l # length * hat(vector)
    def rot(self, th):
        s, c = sin(th), cos(th)
        return Point(self.x * c - self.y * s, self.x * s + self.y * c)
    def lturn(self): return Point(self.y, -self.x) # Both rotate by 90 degrees
    def rturn(self): return Point(-self.y, self.x)

# Functions of two vectors, hence outside the class
def dot(a, b): return a.x * b.x + a.y * b.y
def angle(a, b): return acos(dot(a, b) / a.md() / b.md()) # Unsigned, less than 180 degrees
def sangle(p, base): return (p / base).th() # A number in (-pi, pi]
# Each of the non-operator methods above has a relative version (mostly) r-prefixed.
def pnear(p, origin): return (p - origin).is0()
def dist(p, origin): return (p - origin).md()
def dirc(p, origin): return (p - origin).th()
def rhat(p, origin): return (p - origin).hat()
def rlenbyhat(p, origin, l): return (p - origin).lenbyhat(l)
def rrot(p, origin, th): return (p - origin).rot(th)
def rlturn(p, origin): return (p - origin).lturn()
def rrturn(p, origin): return (p - origin).rturn()
def rdot(a, origin, b): return dot(a - origin, b - origin)
def rsangle(p, origin, base): return sangle(p - origin, base - origin)

# Functions that genuinely have no relative counterpart
def midpoint(p, q): return (p + q) / 2
def slide(p, q, t): return p + t * (q - p)

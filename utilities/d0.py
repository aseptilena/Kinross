#!/usr/bin/env python3.4
# Helper functions defining all the flavours of Kinross
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import *

# Proximal function
def prox(a, b = 0, e = 1e-5):
    return a - b <= e and a - b >= -e

# A point in the plane, equivalently a vector from the origin or complex number.
# For trigonometric operations, positive angle is clockwise to follow SVG convention.
class Point:
    def __init__(self): # Origin
        self.x, self.y = 0.0, 0.0
    def __init__(self, iterb): # From list or tuple
        self.x, self.y = iterb[0], iterb[1]
    def __init__(self, x, y): # From Cartesian coordinates
        self.x, self.y = float(x), float(y)
    def __str__(self): return str(self.x) + " " + str(self.y)
    def __repr__(self): return str(self)
    
    def __add__(self, that): return Point(self.x + that.x, self.y + that.y)
    def __sub__(self, that): return Point(self.x - that.x, self.y - that.y)
    def __neg__(self): return node(-self.x, -self.y)
    
    def __mul__(self, that):
        if type(that) == Point: return Point(self.x * that.x - self.y * that.y, self.y * that.x + self.x * that.y)
        else: return Point(self.x * k, self.y * k)
    def __rmul__(self, k): return self * k
    def __truediv__(self, k):
        if type(that) == Point:
            n = that.x * that.x + that.y * that.y
            return Point(self.x * that.x + self.y * that.y, self.y * that.x - self.x * that.y) / n
        else: return Point(self.x / k, self.y / k)
    
    def is0(): return prox(self.x) and prox(self.y)
    # Modulus and argument
    def md(): return hypot(self.x, self.y)
    def md2(): return self.x * self.x + self.y * self.y
    def th(): return atan2(self.y, self.x)
    # Classic vector operations
    def hat(): return self / md(self) if !self.is0() else Point() # The normalised vector, denoted with a hat
    def rot(th):
        s, c = sin(th), cos(th)
        return Point(self.x * c - self.y * s, self.x * s + self.y * c)
    def lturn(): return Point(self.y, -self.x) # Both of these
    def rturn(): return Point(-self.y, self.x) # rotate by 90 degrees

def pplf(md, th): return Point(md * cos(th), md * sin(th)) # Point from polar form (argument in radians of course)
def pplf1(th): return Point(cos(th), sin(th)) # The same, but returning a unit vector

# Relative functions (origin is stated)
def md(p, origin): return md(p - origin)
def th(p, origin): return th(p - origin)

# TODO dot product

# Linear interpolation
def slide(p, q, t): return p + t * (q - p)

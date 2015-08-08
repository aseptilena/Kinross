#!/usr/bin/env python3.4
# Helper functions defining all the flavours of Kinross
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import *

# A point in the plane, equivalently a complex number.
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
    
    def __mul__(self, k): return Point(self.x * k, self.y * k) # Scalar multiplication
    def __rmul__(self, k): return self * k
    def __truediv__(self, k): return Point(self.x / k, self.y / k) # Scalar division
    # Modulus and argument
    def md(): return hypot(self.x, self.y)
    def th(): return atan2(self.y, self.x)

def pplf(md, th): return Point(md * cos(th), md * sin(th)) # Point from polar form (argument in radians of course)
# Complex multiplication and division
def cpmult(p1, p2): return Point(p1.x * p2.x - p1.y * p2.y, p1.y * p2.x + p1.x * p2.y)
def cpdiv(p1, p2):
    n = p2.x * p2.x + p2.y * p2.y
    return Point(p1.x * p2.x + p1.y * p2.y, p1.y * p2.x - p1.x * p2.y) / n
# Functions of the first point... if the second is the origin
def md(p, origin): return md(p - origin)
def th(p, origin): return th(p - origin)

#!/usr/bin/env python3.4
# Helper functions for Kinross: vector geometry
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import hypot, atan2, sin, cos

def prox(a, b = 0, e = 1e-5): return a - b <= e and a - b >= -e # Proximal function

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

# For each of the methods in Point above there is a corresponding relative function taking a given point as the origin.
# Some names change to reflect this distinction.
def pnear(p, origin): return (p - origin).is0()
def dist(p, origin): return (p - origin).md()
def dirc(p, origin): return (p - origin).th()
def hat(p, origin): return (p - origin).hat()
def lenbyhat(p, origin, l): return (p - origin).lenbyhat(l)
def rot(p, origin, th): return (p - origin).rot(th)
def lturn(p, origin): return (p - origin).lturn()
def rturn(p, origin): return (p - origin).rturn()

# TODO dot product

# Functions between two points
def midpoint(p, q): return (p + q) / 2
def slide(p, q, t): return p + t * (q - p)

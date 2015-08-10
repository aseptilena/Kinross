#!/usr/bin/env python3.4
# Helper functions for Kinross: vector geometry
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
# 
# +y is downwards and +angle is clockwise as per the SVG specifications
from math import hypot, atan2, sin, cos, acos

def prox(a, b, e = 1e-5): return a - b <= e and a - b >= -e
class Origin: x, y = 0., 0. # WHAT A HACK! CALAMITY!
class Point: # or vector or complex number
    def __init__(self, r = 0., s = 0., polar = False):
        if polar: self.x, self.y = r * cos(s), r * sin(s)
        elif type(r) == list or type(r) == tuple: self.x, self.y = float(r[0]), float(r[1])
        else: self.x, self.y = float(r), float(s)
    def __str__(self): return str((self.x, self.y))
    def __repr__(self): return "Point({0}, {1})".format(self.x, self.y)
    def __add__(self, that): return self if type(that) == Origin else Point(self.x + that.x, self.y + that.y)
    def __sub__(self, that): return self if type(that) == Origin else Point(self.x - that.x, self.y - that.y)
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
    # The methods below can all take an arbitrary point as the origin
    def near(self, o = Origin(), e = 1e-5): return prox(self.x, o.x, e) and prox(self.y, o.y, e)
    def dist(self, o = Origin()): return hypot(self.y - o.y, self.x - o.x)
    def sqdist(self, o = Origin()): return (self.y - o.y) ** 2 + (self.x - o.x) ** 2
    def dirc(self, o = Origin()): return atan2(self.y - o.y, self.x - o.x)
    def hat(self, o = Origin()): return (self - o) / self.dist(o) + o if not self.near(o) else self
    # Vector pointing in the same direction as self - o having length l
    def lhat(self, l, o = Origin()): return (self - o) / self.dist(o) * l + o if not self.near(o) else self
    def rot(self, theta, o = Origin()):
        s, c, d = sin(theta), cos(theta), self - o
        return Point(d.x * c - d.y * s, d.x * s + d.y * c) + o
    def lturn(self, o = Origin()): return Point(self.y - o.y, o.x - self.x) + o
    def rturn(self, o = Origin()): return Point(o.y - self.y, self.x - o.x) + o

# Functions of two vectors; these also accept arbitrary origins
def dot(a, b, o = Point()): return (a.x - o.x) * (b.x - o.x) + (a.y - o.y) * (b.y - o.y)
def angle(a, b, o = Point()): return acos(dot(a, b, o) / a.dist(o) / b.dist(o)) # [0, pi]
def sangle(p, base, o = Point()): return ((p - o) / (base - o)).th() # (-pi, pi]
# Interpolation functions
def midpoint(p, q): return (p + q) / 2
def linterp(p, q, t): return t * (q - p) + p

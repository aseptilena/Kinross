#!/usr/bin/env python3.4
# Helper functions for Kinross: vector geometry
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
# 
# Python natively supports complex numbers, why not use them to represent points?
# +y is downwards and +angle is clockwise as per the SVG specifications.
from math import hypot, atan2, sin, cos, acos
from cmath import phase

def prox(a, b, e = 1e-5): return a - b <= e and a - b >= -e
class Origin: x, y = 0., 0. # WHAT A HACK! CALAMITY!
class Point: # or vector or complex number
    def __init__(self, r = 0., s = 0., polar = False):
        if polar: self.x, self.y = r * cos(s), r * sin(s)
        elif type(r) == list or type(r) == tuple: self.x, self.y = float(r[0]), float(r[1])
        else: self.x, self.y = float(r), float(s)
    def __str__(self): return str((self.x, self.y))
    def __repr__(self): return "Point({0}, {1})".format(self.x, self.y)
    
    def near(self, o = Origin(), e = 1e-5): return prox(self.x, o.x, e) and prox(self.y, o.y, e)
    def dist(self, o = Origin()): return hypot(self.y - o.y, self.x - o.x) # dist() = abs(p - o)
    def dirc(self, o = Origin()): return atan2(self.y - o.y, self.x - o.x) # dirc() = phase(p - o)
    
    def rot(self, theta, o = Origin()):
        s, c, d = sin(theta), cos(theta), self - o
        return Point(d.x * c - d.y * s, d.x * s + d.y * c) + o

def polarp(r, th): return complex(r * cos(th), r * sin(th))

def hat(p, o = 0.): return (p - o) / abs(p - o) + o # TODO p near to o?
def lhat(p, l, o = 0.): return (p - o) / abs(p - o) * l + o # TODO ditto; vector pointing in same direction as p - o with length l

def lturn(p, o = 0.): return (o - p) * 1j
def rturn(p, o = 0.): return (p - o) * 1j

# Functions of two vectors; these also accept arbitrary origins
def dot(a, b, o = Point()): return (a.x - o.x) * (b.x - o.x) + (a.y - o.y) * (b.y - o.y)
def angle(a, b, o = Point()): return acos(dot(a, b, o) / a.dist(o) / b.dist(o)) # [0, pi]
def sangle(p, base, o = Point()): return ((p - o) / (base - o)).th() # (-pi, pi]
# Interpolation functions
def midpoint(p, q): return (p + q) / 2
def linterp(p, q, t): return t * (q - p) + p

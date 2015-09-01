#!/usr/bin/env python3.4
# Helper functions for Kinross: vector geometry (points and lines)
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

# Points in Kinross are complex numbers, supported natively by Python.
# +y is downwards and +angle is clockwise as per the SVG specifications.
# Modulus, argument and polar constructors are provided by the native abs, phase and rect respectively.
from math import sin, cos, acos
from cmath import phase, rect
from .numbers import near # local
point = complex
def printpoint(p): return "({}, {})".format(p.real, p.imag)
def hat(p, o = 0j): return o if near(p, o) else (p - o) / abs(p - o) + o
def lenvec(p, l, o = 0j): return o if near(p, o) else (p - o) / abs(p - o) * l + o # "Lengthed vector"; scales p to length l (l * hat(p))
def turn(p, th, o = 0j): return (p - o) * complex(cos(th), sin(th)) + o
def lturn(p, o = 0j): return (o - p) * 1j + o
def rturn(p, o = 0j): return (p - o) * 1j + o
def reflect(p, o = 0j): return 2 * o - p

# Unsigned angles, in [0, pi]; dot product maximum if points collinear and 0 if AOB perpendicular
def dot(a, b, o = 0j): return (a.real - o.real) * (b.real - o.real) + (a.imag - o.imag) * (b.imag - o.imag)
def angle(a, b, o = 0j): return acos(dot(a, b, o) / abs(a - o) / abs(b - o))
def scalproject(p, base, o = 0j): return dot(p, base, o) / abs(base - o)
def vecproject(p, base, o = 0j): return dot(p, base, o) / dot(base, base, o) * (base - o) + o
# Signed angles, in [-pi, pi]; planar cross product maximum if A>O>B = +90 degs, minimum if = -90 degs and 0 if points collinear
def cross(a, b, o = 0j): return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
def signedangle(p, base, o = 0j): return phase((p - o) / (base - o))

# Lines are 2-tuples of points (start, end). Since they are so closely associated with vectors, they come in the same script.
# If a line needs to be used with a point-based function passing l[0] and l[1] will suffice.
def printline(l): return "Line from {} to {}".format(l[0], l[1])
def between(p, q): return (p + q) / 2
def linterp(p, q, t): return t * (q - p) + p
def footperp(p, l): return vecproject(p, l[1], l[0])
def perpdist(p, l): return abs(cross(p, l[1], l[0])) / abs(l[1], l[0])
def lineparam(p, l): return scalproject(p, l[1], l[0]) / abs(l[1] - l[0]) # The parameter the point's projection would have

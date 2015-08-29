#!/usr/bin/env python3.4
# Helper functions for Kinross: vector geometry
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

# Points in Kinross are complex numbers, supported natively by Python.
# +y is downwards and +angle is clockwise as per the SVG specifications.
# Modulus, argument and polar constructors are provided by the native abs, phase and rect respectively.
from math import sin, cos, acos
from cmath import phase, rect
from .numbers import near # local
point = complex
def ppp(p): return "({0}, {1})".format(p.real, p.imag) # Pretty printing of a point
def hat(p, o = 0j): return o if near(p, o) else (p - o) / abs(p - o) + o
def lenvec(p, l, o = 0j): return o if near(p, o) else (p - o) / abs(p - o) * l + o # "Lengthed vector"; scales p to length l (l * hat(p))
def turn(p, th, o = 0j): return (p - o) * complex(cos(th), sin(th)) + o
def lturn(p, o = 0j): return (o - p) * 1j + o
def rturn(p, o = 0j): return (p - o) * 1j + o
def reflect(p, o = 0j): return 2 * o - p

def dot(a, b, o = 0j): return (a.real - o.real) * (b.real - o.real) + (a.imag - o.imag) * (b.imag - o.imag)
def angle(a, b, o = 0j): return acos(dot(a, b, o) / abs(a - o) / abs(b - o)) # Lesser angle between the vectors, in [0, pi]
def signedangle(p, base, o = 0j): return phase((p - o) / (base - o)) # In [-pi, pi]

def between(p, q): return (p + q) / 2
def linterp(p, q, t): return t * (q - p) + p

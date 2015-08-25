#!/usr/bin/env python3.4
# Helper functions for Kinross: affine transformations
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

# Affine transformations are 6-tuples of floats corresponding as follows (if the name is c):
# [c0 c2 c4]
# [c1 c3 c5]
# [0  0  1 ]
# Compositions of transformations are stored in the order they would be written down to denote matrix multiplication of a point, as per the SVG specifications.
from .vectors import * # local
from math import sin, cos, tan
def transform(mat, p): return point(mat[0] * p.real + mat[2] * p.imag + mat[4], mat[1] * p.real + mat[3] * p.imag + mat[5])
def compose(p, *q):
    for m in q:
        p = (p[0] * m[0] + p[2] * m[1],
             p[1] * m[0] + p[3] * m[1],
             p[0] * m[2] + p[2] * m[3],
             p[1] * m[2] + p[3] * m[3],
             p[0] * m[4] + p[2] * m[5] + p[4],
             p[1] * m[4] + p[3] * m[5] + p[5])
    return p
def inversemat(mat):
    det = mat[0] * mat[3] - mat[1] * mat[2]
    return (mat[3] / det, -mat[1] / det, -mat[2] / det, mat[0] / det,
            (mat[2] * mat[5] - mat[3] * mat[4]) / det,
            (mat[1] * mat[4] - mat[0] * mat[5]) / det)
def detransform(mat, p): return tf(inversemat(mat), p) # inverse transform
def transmat(x, y = 0.): return (1., 0., 0., 1., float(x), float(y))
def rotmat(th, o = None):
    if o == None: return (cos(th), sin(th), -sin(th), cos(th), 0., 0.)
    else: return compose(transmat(o.real, o.imag), rotmat(th), transmat(-o.real, -o.imag))
def scalemat(x, y = None): return (float(x), 0., 0., float(x if y == None else y), 0., 0.)
def skewmat(x, y): return (1., tan(x), tan(y), 1., 0., 0.)

# Scaling by unequal factors and skewing are un-collapsable transformations, in the sense that they cannot be reasonably "pushed" down the group hierarchy.
# The following function decomposes any transformation into the collapsable and uncollapsable parts; reduction can be done if the latter is zero.
# Even if it isn't, we can still proceed if none of the shapes has any fill.
# TODO
def decompose(t):
    pass

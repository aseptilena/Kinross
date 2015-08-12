#!/usr/bin/env python3.4
# Helper functions for Kinross: affine (SVG) transformations
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from vectors import *
# Affine transformations are 6-tuples of floats corresponding as follows (if the name is c):
# [c0 c2 c4]
# [c1 c3 c5]
# [0  0  1 ]

def fortrans(mat, p): return point(mat[0] * p.real + mat[2] * p.imag + mat[4], mat[1] * p.real + mat[3] * p.imag + mat[5])
def affcomp(p, q):
    return (p[0] * q[0] + p[2] * q[1],
            p[1] * q[0] + p[3] * q[1],
            p[0] * q[2] + p[2] * q[3],
            p[1] * q[2] + p[3] * q[3]
            p[0] * q[4] + p[2] * q[5] + p[4],
            p[1] * q[4] + p[3] * q[5] + p[5])
def minvert(mat): # Matrix inverted
    det = mat[0] * mat[3] - mat[1] * mat[2]
    return (mat[3] / det, -mat[1] / det, -mat[2] / det, mat[0] / det,
            (mat[2] * mat[5] - mat[3] * mat[4]) / det,
            (mat[1] * mat[4] - mat[0] * mat[5]) / det)
def backtrans(mat, p): return minvert(mat) * p

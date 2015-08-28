#!/usr/bin/env python3.4
# Helper functions for Kinross: numeric functions and linear algebra
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

def near(a, b, e = 1e-5): return abs(b - a) <= e
# ax + by = p; cx + dy = q; returns (x, y)
def lineareq2(a, b, p, c, d, q):
    det = a * d - b * c
    if near(det, 0.): return (None, None)
    return ((p * d - q * b) / det, (a * q - c * p) / det)

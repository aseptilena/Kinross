#!/usr/bin/env python3.4
# Helper functions for Kinross: numeric functions and linear algebra
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

def near(a, b, e = 1e-5): return abs(b - a) <= e

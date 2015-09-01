#!/usr/bin/env python3.4
# Helper functions for Kinross: proximities (intersections and nearest distance)
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

# The names of intersection-finding functions here all begin with intersect_; this is followed by two letters indicating which objects it handles.
# l = line, e = ellipse/circle, r = rhythm; non-trivial solutions are returned as a tuple.

def intersect_ll(l1, l2, real = True):
    """Finds the intersection of two lines. The real parameter, if true, will only allow intersections between each pair of endpoints."""
    if near(cross(l1[1] - l1[0], l2[1] - l2[0])): return ()
    # TODO
    pass

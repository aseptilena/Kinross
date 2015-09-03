#!/usr/bin/env python3.4
# Helper functions for Kinross: proximities (intersections and nearest distance)
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import * # local
from .ellipse import *
# The names of intersection-finding functions here are named intersect_ + two letters for the objects it handles.
# l = line, c = circle, e = ellipse, r = rhythm; non-trivial solutions are returned as a tuple.

# Categorising the different solutions in order of "hardness", lines come first.
def intersect_ll(l, m, ext = False):
    """Finds the intersection of two lines. The ext parameter, if true, will allow intersections outside one or both of the line segments."""
    v, w = l[1] - l[0], m[1] - m[0]
    if not near(cross(v, w)):
        p, q = lineareq2(v.real, -w.real, (m[0] - l[0]).real, v.imag, -w.imag, (m[0] - l[0]).imag)
        if ext or 0. <= p <= 1. and 0. <= q <= 1.: return linterp(l[0], l[1], p)
    return ()

# Then circles.
def intersect_cl(c, l):
    z = perpdist(c.centre, l)
    if z > c.r: return ()
    f = footperp(c.centre, l)
    d = sqrt(c.r * c.r - z * z)
    return (lenvec(l[1] - l[0], d) + f, lenvec(l[0] - l[1], d) + f)

def intersect_cc(c, d):
    """A common problem in 2D video gaming."""
    z, plus, minus = sqdist(c.centre, d.centre), c.r + d.r, c.r - d.r
    if z > plus * plus or z <= minus * minus: return ()
    s = abs(d.centre - c.centre)
    # Now projecct the radius of the first circle onto the inter-centre line to obtain the central point.
    a = (c.r * c.r - d.r * d.r + z) / (2 * s)
    h = sqrt(c.r * c.r - a * a)
    y = lenvec(d.centre, a, c.centre)
    bar = lenvec(lturn(d.centre - c.centre), h)
    return (y + h, y - h)
    # TODO

# Then ellipses (though they can always be transformed to the cases below or above).
def intersect_ee(e, f):
    """Finds the intersections of two ellipses via a transformation that maps the first one to a unit circle and aligns the second's axes with the coordinate axes.
    This leads to a quartic equation which is solved numerically to obtain the actual intersections."""
    m = e.unitcircletf()
    fp = f.tf(m)
    fpp = fp.tf(rotmat(-fp.tilt))
    # rotmat(-fp.tilt) > m > f
    # The transform to get back is inversemat(composetf(rotmat(-fp.tilt), m)).
    # fpp's centre is now (p, q) and its x- and y-aligned axes are of length r and s.
    # Then ((x - p) / r) ^ 2 + ((y - q) / s) ^ 2 = 1 and x ^ 2 + y ^ 2 = 1;
    # this is a quartic in either variable and the roots are cranked out with the Durand/Kerner method.
    pass # TODO

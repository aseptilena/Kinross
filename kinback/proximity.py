#!/usr/bin/env python3.4
# Helper functions for Kinross: proximities (intersections and nearest distance)
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import *
from .ellipse import *

# The names of intersection-finding functions here are named intersect_ + two letters for the objects it handles.
# l = line, c = circle, e = ellipse, r = rhythm; non-trivial solutions are returned as a tuple.
# Categorising the different solutions in order of "hardness", lines come first.
def intersect_ll(l, m, ext = False):
    """Finds the intersection of two lines. The ext parameter, if true, allows intersections not falling on both line segments."""
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
    sep = d.centre - c.centre
    z, plus, minus = sqabs(sep), c.r + d.r, c.r - d.r
    if z > plus * plus or z <= minus * minus: return ()
    k = (plus * minus + sqabs(d.centre) - sqabs(c.centre)) / 2
    # x * sep.real + y * sep.imag = k is the radical line of c and d, through which both intersections pass.
    # Since at least one of sep.real and sep.imag is non-zero, we can take two points, one where x = y and another where one is zero.
    s = k / (sep.real + sep.imag)
    p1 = point(s, s)
    p2 = point(k / sep.real, 0.) if sep.real != 0 else (0., k / sep.imag)
    return intersect_cl(c, (p1, p2))

# Then ellipses (though they can always be transformed to the cases below or above).
def intersect_el(e, l):
    """Transform the ellipse to a unit circle and work from there."""
    ll = tuple(affine(e.unitcircletf(), p) for p in l)
    ii = intersect_cl(circle(), ll)
    return tuple(affine(e.unitcircleinvtf(), i) for i in ii)

def intersect_ee(e, f):
    """Transform the first ellipse to a unit circle, align the second's axes to coordinate axes and crunch numbers."""
    # TODO there must be a better way
    from .polynomial import polynomroot, D
    fp = f.tf(e.unitcircletf())
    fpp = fp.tf(rotation(-fp.tilt))
    # The transform to get back is composition(e.unitcircleinvtf(), rotation(fp.tilt)).
    # fpp's centre is now (p, q) and its x- and y-aligned axes are of length r and s respectively.
    # Then ((x - p) / r) ^ 2 + ((y - q) / s) ^ 2 = 1 and x ^ 2 + y ^ 2 = 1; this is a quartic in either variable.
    p, q, r, s = fpp.centre.real, fpp.centre.imag, fpp.rx, fpp.ry
    u = s / r
    T = u * u
    X, Y, Z = 1 - T, 2 * p * T, p * p * T + q * q - s * s + 1
    # X^2 * x^4 - 2XY * x^3 + (Y^2 - 2XZ + 2q^2) * x^2 - 2YZ * x + (Z^2 - 4q^2) = 0
    xvals = polynomroot((Z * Z - 4 * q * q, -2 * Y * Z, Y * Y - 2 * X * Z + 4 * q * q, -2 * X * Y, X * X))[0]
    res = []
    for x in xvals:
        circycomp = 1 - x * x
        ellycomp = 1 - (x - p) * (x - p) / (r * r)
        if circycomp < 0 or ellycomp < 0: continue
        yc = sqrt(circycomp)
        ye1, ye2 = -sqrt(ellycomp) * s + q, sqrt(ellycomp) * s + q
        res.append(point(x, ye1 if abs(abs(ye1) - yc) < abs(abs(ye2) - yc) else ye2))
    return tuple(affine(composition(e.unitcircleinvtf(), rotation(fp.tilt)), s) for s in res)

def intersect_ec(e, c):
    """Once the two-ellipse problem is solved, this becomes trivial to implement."""
    ce = c.toellipse()
    return intersect_ee(e, ce)

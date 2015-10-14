# Helper functions for Kinross: vector functions, affine transformations and miscellaneous numeric
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sin, cos, tan, acos, degrees
from cmath import phase, rect, isclose

# Points in Kinross are complex numbers, but for the purposes of SVG +y is downwards and +angle is clockwise.
# For modulus, argument and polar constructors use abs, phase and rect respectively.

# Single-vector operations
def sqabs(p, q = 0j): return (p.real - q.real) * (p.real - q.real) + (p.imag - q.imag) * (p.imag - q.imag)
def hat(p, o = 0j): return o if isclose(p, o) else (p - o) / abs(p - o) + o
def lenvec(p, l, o = 0j):
    """Scales p to length l relative to o."""
    return o if isclose(p, o) else (p - o) / abs(p - o) * l + o
def turn(p, th, o = 0j): return (p - o) * complex(cos(th), sin(th)) + o
def lturn(p, o = 0j): return (o - p) * 1j + o
def rturn(p, o = 0j): return (p - o) * 1j + o
def reflect(p, o = 0j): return 2 * o - p
# Dot and cross products
# Unsigned angles, in [0, pi]; dot product maximum if OAB/OBA collinear, 0 if AOB perpendicular, minimum if AOB collinear
def dot(a, b, o = 0j): return (a.real - o.real) * (b.real - o.real) + (a.imag - o.imag) * (b.imag - o.imag)
def angle(a, b, o = 0j): return acos(dot(a, b, o) / (abs(a - o) * abs(b - o)))
def vecproject(p, base, o = 0j): return (p - o).real if isclose(base, o) else dot(p, base, o) / dot(base, base, o) * (base - o) + o 
# Signed angles, in [-pi, pi]; planar cross product maximum if A>O>B = +90 degs, minimum if = -90 degs and 0 if points collinear
def cross(a, b, o = 0j): return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
def signedangle(p, base, o = 0j): return phase((p - o) / (base - o)) # from base to o to p
def collinear(a, b, c): return isclose(cross(a, b, c), 0)
# Line functions; lines are 2-tuples of points
def between(p, q): return (p + q) / 2
def linterp(p, q, t): return t * (q - p) + p
def footperp(p, l): return vecproject(p, l[1], l[0])
def perpdist(p, l): return abs(cross(p, l[1], l[0]) / (l[1] - l[0]))
def perpbisect(a, b):
    m = between(a, b)
    return (lturn(a, m), rturn(a, m))
# Pretty printing of points and lines
def printpoint(p): return "({}, {})".format(p.real, p.imag)
def printline(l): return "Line from {} to {}".format(l[0], l[1])

# INTERMISSION: 2-variable linear equation solver and line/line intersection
def lineareq2(a, b, p, c, d, q):
    """ax + by = p; cx + dy = q; returns (x, y)."""
    det = a * d - b * c
    if isclose(det, 0.): return (None, None)
    return ((p * d - q * b) / det, (a * q - c * p) / det)
def intersect_ll(l, m, real = True):
    """Finds the intersection of two lines. real restricts to "real" intersections on both line segments that define the lines."""
    v, w = l[1] - l[0], m[1] - m[0]
    if not isclose(cross(v, w), 0):
        p, q = lineareq2(v.real, -w.real, (m[0] - l[0]).real, v.imag, -w.imag, (m[0] - l[0]).imag)
        if not real or 0. <= p <= 1. and 0. <= q <= 1.: return linterp(l[0], l[1], p)
    return None

# Affine transformations are 6-tuples of floats corresponding to the following matrix (if the name is c):
# [c0 c2 c4]
# [c1 c3 c5]
# [0  0  1 ]
# Compositions are stored last-to-first, corresponding to the SVG transformation syntax and mathematical notation.
def affine(mat, p): return complex(mat[0] * p.real + mat[2] * p.imag + mat[4], mat[1] * p.real + mat[3] * p.imag + mat[5])
def composition(s, *q):
    p = s
    for m in q:
        p = (p[0] * m[0] + p[2] * m[1],
             p[1] * m[0] + p[3] * m[1],
             p[0] * m[2] + p[2] * m[3],
             p[1] * m[2] + p[3] * m[3],
             p[0] * m[4] + p[2] * m[5] + p[4],
             p[1] * m[4] + p[3] * m[5] + p[5])
    return p
def inverting(mat):
    det = mat[0] * mat[3] - mat[1] * mat[2]
    return (mat[3] / det, -mat[1] / det, -mat[2] / det, mat[0] / det,
           (mat[2] * mat[5] - mat[3] * mat[4]) / det,
           (mat[1] * mat[4] - mat[0] * mat[5]) / det)
def backaffine(mat, p): return affine(inverting(mat), p) # inverse transform
def translation(o): return (1., 0., 0., 1., o.real, o.imag)
def rotation(th, o = None):
    if o == None: return (cos(th), sin(th), -sin(th), cos(th), 0., 0.)
    else: return composition(translation(o), rotation(th), translation(-o))
def scaling(x, y = None): return (float(x), 0., 0., float(x if y == None else y), 0., 0.)
def skewing(x, y): return (1., tan(x), tan(y), 1., 0., 0.)
def squeezing(a): return (float(a), 0., 0., 1 / a, 0., 0.)

# Transformations are separated into the following components applied in sequence:
# 1. Scaling only in the y-axis
# 2. Shearing in the x-axis
# 3. Uniform scaling and flipping
# 4. Combined rotation/translation (three-argument rotation)
# The first two cannot be factored ("collapsed") into SVG elements without much more computation; the following function determines if the transformation doesn't contain them.
# Equivalent to preservesAngles() in dgeom (https://github.com/vector-d/dgeom/blob/master/source/geom/affine.d#L448).
def collapsibility(t):
    """Returns 1 if the function is a scaling + rotation + translation, -1 for the same but with flipping and 0 otherwise."""
    if isclose(t[0], t[3]) and isclose(t[1], -t[2]): return 1
    if isclose(t[0], -t[3]) and isclose(t[1], t[2]): return -1
    return 0

def collapsedtransform(t):
    """If the transform is collapsible, returns ((z, flip), (th, o)) <=> scaling(z, flip * z) rotation(th, o), otherwise None. flip = 1 or -1 and th is in degrees.
    If the first tuple is empty, this indicates that no scaling/flipping is present. For the second:
    * (None, o) indicates translate(o)
    * (th, None) indicates rotate(th)
    * (None, None) indicates pure scaling
    The function will put as much of the transformation as possible into the second tuple, so z is normally positive.
    However, the case of ((z, 1), (pi / 2, None)) - a pure negative scaling - is coerced to ((-z, 1), (None, None))."""
    flip = collapsibility(t)
    if not flip: return None
    # The reverse of the second component aligns the x-axis correctly.
    # If the original "masonic square" has origin (0, 0) at O, x-axis (1, 0) at X and y-axis (0, 1) at Y,
    # while the transformed "square" has origin at O', hatted x-axis at X' and hatted y-axis at Y',
    # the centre for the second component is the intersection of the perpendicular bisector of OO' and the perpendicular bisector of XX'.
    # The angle rotated by is simply the signed angle from O to the intersection to O'.
    o, z = complex(t[4], t[5]), hat(complex(t[0], t[1]))
    x = o + z
    if isclose(o, 0): second = (None if isclose(x, 1) else degrees(phase(x)), None)
    else:
        g = 1. if isclose(x, 1) else intersect_ll(perpbisect(o, 0), perpbisect(x, 1), False)
        second = (None, o) if g == None else (degrees(signedangle(o, 0, g)), g)
    l = abs(z) # The first component is the absolute value of z
    first = () if isclose(l, 1) and flip == 1 else (l, flip)
    if second[1] == None and second[0] != None and flip == 1 and isclose(180, abs(second[0])): first, second = (-l, 1), (None, None)
    return (first, second)

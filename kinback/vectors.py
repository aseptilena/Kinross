# Helper functions for Kinross: vector functions and affine transformations
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sin, cos, tan, acos
from cmath import phase, rect

# This file (and especially this function) underpins the ENTIRE Kinback library. Yet it is so plain and simple...
def near(a, b, e = 1e-5):
    """Checks if the difference between two numbers is within the given epsilon. For complex numbers this implements an L2 norm.
    a and b must be either both decimals or both ints/floats/complexes.
    When Python 3.5 becomes widely available this will be replaced by the cmath.isclose() function."""
    return abs(a - b) <= e

# ...except for what follows.
# Points in Kinross are complex numbers, but for the purposes of SVG +y is downwards and +angle is clockwise.
# For modulus, argument and polar constructors use abs, phase and rect respectively.
point = complex
# Single-vector operations
def sqabs(p, q = 0j): return (p.real - q.real) * (p.real - q.real) + (p.imag - q.imag) * (p.imag - q.imag)
# hat and lenvec are quite unusual. If p is near o, the functions return o and are just a longer check for nearness.
def hat(p, o = 0j): return o if near(p, o) else (p - o) / abs(p - o) + o
def lenvec(p, l, o = 0j):
    """Scales p to length l relative to o."""
    return o if near(p, o) else (p - o) / abs(p - o) * l + o
def turn(p, th, o = 0j): return (p - o) * complex(cos(th), sin(th)) + o
def lturn(p, o = 0j): return (o - p) * 1j + o
def rturn(p, o = 0j): return (p - o) * 1j + o
def reflect(p, o = 0j): return 2 * o - p

# Dot and cross products
# Unsigned angles, in [0, pi]; dot product maximum if OAB/OBA collinear, 0 if AOB perpendicular, minimum if AOB collinear
def dot(a, b, o = 0j): return (a.real - o.real) * (b.real - o.real) + (a.imag - o.imag) * (b.imag - o.imag)
def angle(a, b, o = 0j): return acos(dot(a, b, o) / (abs(a - o) * abs(b - o)))
def vecproject(p, base, o = 0j): return (p - o).real if near(base, o) else dot(p, base, o) / dot(base, base, o) * (base - o) + o 
# Signed angles, in [-pi, pi]; planar cross product maximum if A>O>B = +90 degs, minimum if = -90 degs and 0 if points collinear
def cross(a, b, o = 0j): return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
def signedangle(p, base, o = 0j): return phase((p - o) / (base - o))
def collinear(a, b, c): return near(cross(a, b, c), 0.)

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
    if near(det, 0.): return (None, None)
    return ((p * d - q * b) / det, (a * q - c * p) / det)
def intersect_ll(l, m, real = True):
    """Finds the intersection of two lines. real restricts to "real" intersections on both line segments that define the lines."""
    v, w = l[1] - l[0], m[1] - m[0]
    if not near(cross(v, w), 0.):
        p, q = lineareq2(v.real, -w.real, (m[0] - l[0]).real, v.imag, -w.imag, (m[0] - l[0]).imag)
        if not real or 0. <= p <= 1. and 0. <= q <= 1.: return linterp(l[0], l[1], p)
    return None

# Affine transformations are 6-tuples of floats corresponding to the following matrix (if the name is c):
# [c0 c2 c4]
# [c1 c3 c5]
# [0  0  1 ]
# Compositions are stored last-to-first, corresponding to the SVG transformation syntax and mathematical notation.
def affine(mat, p): return point(mat[0] * p.real + mat[2] * p.imag + mat[4], mat[1] * p.real + mat[3] * p.imag + mat[5])
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
def translation(x, y = 0.): return (1., 0., 0., 1., float(x), float(y))
def rotation(th, o = None):
    if o == None: return (cos(th), sin(th), -sin(th), cos(th), 0., 0.)
    else: return composition(translation(o.real, o.imag), rotation(th), translation(-o.real, -o.imag))
def scaling(x, y = None): return (float(x), 0., 0., float(x if y == None else y), 0., 0.)
def skewing(x, y): return (1., tan(x), tan(y), 1., 0., 0.)

# Transformations are separated into the following components applied in sequence:
# 1. Scaling only in the y-axis
# 2. Shearing in the x-axis
# 3. Uniform scaling and flipping
# 4. Combined rotation/translation (three-argument rotation)
# The first two cannot be factored ("collapsed") into SVG elements without much more computation; the following function determines if the transformation doesn't contain them.
# Equivalent to preservesAngles() in dgeom (https://github.com/vector-d/dgeom/blob/master/source/geom/affine.d#L448).
def collapsibility(t):
    """Returns 1 if the function is a scaling + rotation + translation, -1 for the same but with flipping and 0 otherwise."""
    if near(t[0], t[3]) and near(t[1], -t[2]): return 1
    if near(t[0], -t[3]) and near(t[1], t[2]): return -1
    return 0

def collapsetransform(t):
    """If the transform is collapsible, returns the tuple-tuple ((float z, int flip) (float th, complex o))
    corresponding to scale(z, flip * z) rotate(th, o), otherwise None. z is any non-zero number; flip = 1 or -1.
    
    If the first tuple is empty, this indicates that no scaling/flipping is present. For the second:
    * (complex l) indicates translate(l) (i.e. no rotation)
    * (float th) indicates rotate(th) (i.e. rotation around origin)
    * () indicates no rotation or translation (i.e. pure scaling)
    Normally the function will put as much of the transformation as possible into the second tuple.
    However, the case of ((float z, 1), (float pi / 2)) - a pure negative scaling - is coerced to ((float -z, 1), ())."""
    flip = collapsibility(t)
    if not flip: return t
    return 774 # TODO

# The Bareiss determinant algorithm as given in http://cs.nyu.edu/~yap/book/alge/ftpSite/l10.ps.gz (section 2).
# Note that this gives exact results for integer matrices, so an exact option is there if needed.
def matdeterm(m, exact = False):
    import operator
    divf = operator.floordiv if exact else operator.truediv
    a, N = [list(r[:]) for r in m], len(m)
    # Add rows until the main diagonal is all non-zero; this does not change the determinant
    counter = 0
    while counter < N:
        if not near(a[counter][counter], 0, 1e-9):
            counter += 1
            continue
        nadded = True
        for z in range(N):
            if not near(a[z][counter], 0, 1e-9) and z != counter:
                a[counter] = [sum(pair) for pair in zip(a[counter], a[z])]
                nadded = False
                break
        if nadded: return 0 # The determinant of a matrix with a row or column of 0's is 0
        counter += 1
    for k in range(1, N):
        kk = k - 1
        for i in range(k, N):
            for j in range(k, N): a[i][j] = divf(a[i][j] * a[kk][kk] - a[i][kk] * a[kk][j], 1 if not kk else a[k - 2][k - 2])
    return a[-1][-1]

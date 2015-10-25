# Helper functions for Kinross: affine transformations
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import hat, intersect_ll, perpbisect, signedangle
from math import sin, cos, tan, degrees, radians
from cmath import isclose
from .regexes import tokenisetransform, floatinkrep, numbercrunch

# Affine transformations are 6-tuples of floats corresponding to the following matrix. Compositions are stored last-to-first-applied.
# [c0 c2 c4]
# [c1 c3 c5]
# [0  0  1 ]
def affine(mat, p): return complex(mat[0] * p.real + mat[2] * p.imag + mat[4], mat[1] * p.real + mat[3] * p.imag + mat[5])
def composition(*mats): # if the matrices are in last-to-first order
    p = mats[0]
    for m in mats[1:]:
        p = (p[0] * m[0] + p[2] * m[1],
             p[1] * m[0] + p[3] * m[1],
             p[0] * m[2] + p[2] * m[3],
             p[1] * m[2] + p[3] * m[3],
             p[0] * m[4] + p[2] * m[5] + p[4],
             p[1] * m[4] + p[3] * m[5] + p[5])
    return p
def inversemat(mat):
    det = mat[0] * mat[3] - mat[1] * mat[2]
    return tuple(map(lambda x: x / det, (mat[3], -mat[1], -mat[2], mat[0], mat[2] * mat[5] - mat[3] * mat[4], mat[1] * mat[4] - mat[0] * mat[5])))
def backaffine(mat, p): return affine(inversemat(mat), p)
def translation(o): return (1, 0, 0, 1, o.real, o.imag)
def rotation(th, o = None):
    if o == None: return (cos(th), sin(th), -sin(th), cos(th), 0., 0.)
    else: return composition(translation(o), rotation(th), translation(-o))
def scaling(x, y = None): return (float(x), 0, 0, float(x if y == None else y), 0, 0)
def skewing(x, y): return (1, tan(y), tan(x), 1, 0, 0)
def squeezing(a): return (float(a), 0, 0, 1 / a, 0, 0) # Not in the SVG specifications, but here to help the elliptical arc constructor

# Transformations are separated into the following components applied in sequence:
# scaling only in the y-axis, shearing in the x-axis, uniform scaling and flipping, combined rotation/translation (three-argument rotation).
# The first two cannot be factored ("collapsed") into SVG elements without much more computation; the following function determines if the transformation doesn't contain them.
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
    z will normally be positive, but ((z, 1), (pi / 2, None)) is coerced to ((-z, 1), (None, None)) or scale(-z)."""
    flip = collapsibility(t)
    if not flip: return None
    # If the original ell has O = (0, 0), X = (1, 0) and Y = (0, 1) while the transformed ell has origin at O', hatted x-axis at X' and hatted y-axis at Y',
    # the centre for the second component is the intersection of the perpendicular bisector of OO' and the perpendicular bisector of XX'.
    # The angle rotated by is simply the signed angle from O to the intersection to O'.
    v1 = complex(t[0], t[1])
    o, z, l = complex(t[4], t[5]), hat(v1), abs(v1)
    x = o + z
    if isclose(o, 0): second = [None if isclose(x, 1) else degrees(phase(x)), None]
    else:
        g = 1 if isclose(x, 1) else intersect_ll(perpbisect(o, 0), perpbisect(x, 1), False)
        second = [None, o] if g == None else [degrees(signedangle(o, 0, g)), g]
    first = [] if isclose(l, 1) and flip == 1 else [l, flip]
    if second[0] != None:
        if second[0] < 0: second[0] += 360
        if second[1] == None and flip == 1 and isclose(180, abs(second[0])): first, second = [-l, 1], [None, None]
    return [first, second]

def minimisetransform(tfs):
    """If the transform is collapsible, returns its minimal representation according to collapsibility, otherwise returns tfs itself."""
    tmats = []
    for pair in tokenisetransform(tfs):
        if   pair[0] == "matrix": tmats.append(pair[1])
        elif pair[0] == "translate": tmats.append(translation(complex(pair[1][0], 0 if len(pair[1]) == 1 else pair[1][1])))
        elif pair[0] == "scale": tmats.append(scaling(*pair[1]))
        elif pair[0] == "rotate": tmats.append(rotation(radians(pair[1][0]), None if len(pair[1]) == 1 else complex(pair[1][1], pair[1][2])))
        elif pair[0] == "skewX": tmats.append(skewing(radians(pair[1][0]), 0))
        elif pair[0] == "skewY": tmats.append(skewing(0, radians(pair[1][0])))
    ctm = composition(*tmats)
    a0, b0, c0, d0, e0, f0 = [isclose(n, 0) for n in ctm]
    if b0 and c0 and e0 and f0: # Scaling check
        if isclose(a0, d0): return "scale({})".format(floatinkrep(ctm[0], True))
        else: return "scale({},{})".format(floatinkrep(ctm[0], True), floatinkrep(ctm[3], True))
    if isclose(ctm[0], 1) and isclose(ctm[3], 1) and b0 and c0: # Translation check
        if f0: return "translate({})".format(floatinkrep(ctm[4], True))
        else: return "translate({},{})".format(floatinkrep(ctm[4], True), floatinkrep(ctm[5], True))
    ctf = collapsedtransform(ctm)
    if ctf == None: return tfs
    sc, rt = ctf
    first = "" if not sc else ("scale({})".format(floatinkrep(sc[0], True) if sc[1] == 1 else numbercrunch(floatinkrep(sc[0], True), floatinkrep(-sc[0], True))))
    if rt[1] != None:
        rl, im = floatinkrep(rt[1].real, True), floatinkrep(rt[1].imag, True)
        if rt[0] == None: second = "translate({})".format(rl if im == "0" else numbercrunch(rl, im))
        else: second = "rotate({})".format(numbercrunch(floatinkrep(rt[0], True), rl, im))
    else: second = "" if rt[0] == None else "rotate({})".format(floatinkrep(rt[0], True))
    return second + first

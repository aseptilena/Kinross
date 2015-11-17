# Helper functions for Kinross: affine transformations
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import saltire, perpbisect, signedangle
from math import sin, cos, tan, copysign, degrees, radians, nan
from cmath import isclose, phase
from .regexes import tokenisetransform, floatinkrep, numbercrunch

# Affine transformations are 6-tuples of floats corresponding to the following matrix. Compositions are stored last-to-first-applied.
#  x  y  o  <- identity transformation: 1, i and 0
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

def collapsibility(t):
    """1 if the affinity is a scaling + rotation + translation, -1 for the same but with flipping and 0 otherwise."""
    if isclose(t[0], t[3]) and isclose(t[1], -t[2]): return 1
    if isclose(t[0], -t[3]) and isclose(t[1], t[2]): return -1
    return 0

def floataffrep(x): return floatinkrep(x, True)
def collapsedtransform(t):
    """If the transform is collapsible, returns the [rotation, scaling] components, else None. The second component (scaling) is [f, z] where f = 1 (no flip) / -1 (flip) and z is the scaling factor.
    The first component (rotation/translation) is [th, or, oi]: th is the rotation angle in degrees (NaN for translation), or and oi the rotation centre's components (Δx, Δy for translation)."""
    f = collapsibility(t)
    if not f: return None
    x = complex(t[0], t[1])
    if isclose(t[1], 0): return [[nan, t[4], t[5]], [f, copysign(abs(x), t[0])]] # This handles the upright and upside-down cases, all at the same time!
    o, sp = complex(t[4], t[5]), [f, abs(x)]
    if isclose(o, 0): return [[degrees(phase(x)), 0, 0], sp]
    if isclose(o + x, sp[1]): return [[degrees(phase(x)), sp[1], 0], sp]
    rc = saltire(perpbisect(o, 0), perpbisect(o + x, sp[1]))
    return [[degrees(signedangle(o, 0, rc)) % 360, rc.real, rc.imag], sp]

def parsetransform(tfs):
    """Parses a transform string and returns the overall transformation matrix."""
    tmats = []
    for pair in tokenisetransform(tfs):
        if   pair[0] == "matrix": tmats.append(pair[1])
        elif pair[0] == "translate": tmats.append(translation(complex(pair[1][0], 0 if len(pair[1]) == 1 else pair[1][1])))
        elif pair[0] == "scale": tmats.append(scaling(*pair[1]))
        elif pair[0] == "rotate": tmats.append(rotation(radians(pair[1][0]), None if len(pair[1]) == 1 else complex(pair[1][1], pair[1][2])))
        elif pair[0] == "skewX": tmats.append(skewing(radians(pair[1][0]), 0))
        elif pair[0] == "skewY": tmats.append(skewing(0, radians(pair[1][0])))
    return composition(*tmats)

def lingradcollapse(lg):
    """Given a linear gradient with a transformation, collapses the transformation."""
    p1, p2, mat = complex(float(lg.get("x1")), float(lg.get("y1"))), complex(float(lg.get("x2")), float(lg.get("y2"))), parsetransform(lg.get("gradientTransform"))
    p1, p2 = affine(mat, p1), affine(mat, p2)
    del lg.attrib["gradientTransform"]
    lg.attrib.update({"x1": floataffrep(p1.real), "y1": floataffrep(p1.imag), "x2": floataffrep(p2.real), "y2": floataffrep(p2.imag)})

def minimisetransform(tfs):
    """If the transform string is collapsible, returns its minimal representation, otherwise returns input."""
    ctm = parsetransform(tfs)
    h = collapsedtransform(ctm)
    if h == None: return "matrix({})".format(numbercrunch(*[floataffrep(v) for v in ctm]))
    rt, sc = h
    # Translation/rotation (left) part
    dx, dy = floataffrep(rt[1]), floataffrep(rt[2])
    if rt[0] is nan: rtstr = ("" if dx == "0" else "translate({})".format(dx)) if dy == "0" else "translate({})".format(numbercrunch(dx, dy))
    else:
        thet = floataffrep(rt[0])
        rtstr = "rotate({})".format(thet if dx == dy == "0" else numbercrunch(thet, dx, dy))
    # Scaling (right) part
    z = floataffrep(sc[1])
    scstr = ("" if z == "1" else "scale({})".format(z)) if sc[0] == 1 else "scale({})".format(numbercrunch(z, floataffrep(-sc[1])))
    return rtstr + scstr

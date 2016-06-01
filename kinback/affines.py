# Helper functions for Kinross: affine transformations
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import sin, cos, tan, copysign, degrees, radians, nan
from cmath import isclose, phase, rect
from .vectors import saltire, perpbisect, signedangle
from .regexes import tokenisetransform, floatinkrep, numbercrunch

import re
tf_re = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\((.*?)\)")
num_re = re.compile(r"[-+]?(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.?))(?:[eE][-+]?[0-9]+)?")

# [a c e] Affine matrix structure,
# [b d f] implemented in the
# [0 0 1] class below
class tf:
    def __init__(self, a, b, c, d, e, f): self.v = (a, b, c, d, e, f)
    def __str__(self): return "/{:f} {:f} {:f} {:f} {:f} {:f}/".format(*self.v)
    def __repr__(self): return "tf({} {} {} {} {} {})".format(*self.v)
    
    def I(): return tf(1, 0, 0, 1, 0, 0)
    def tr(dx, dy = 0): return tf(1, 0, 0, 1, dx, dy)
    def sc(sx, sy = None): return tf(sx, 0, 0, sx if sy == None else sy, 0, 0)
    def ro(th, cx = 0, cy = 0):
        cs = rect(1, radians(th))
        return tf(cs.real, cs.imag, -cs.imag, cs.real, (1 - cs.real) * cx + cs.imag * cy,
                                                       (1 - cs.real) * cy - cs.imag * cx)
    def skx(z): return tf(1, 0, tan(radians(z)), 1, 0, 0)
    def sky(z): return tf(1, tan(radians(z)), 0, 1, 0, 0)
    tfmap = {"matrix": __init__, "translate": tr, "scale": sc, "rotate": ro, "skewX": skx, "skewY": sky}
    def fromsvg(s):
        """Converts an SVG transform string into its equivalent matrix."""
        out = tf.I()
        for cmd in tf_re.finditer(s):
            head, load = cmd.groups()
            load = num_re.findall(load)
            out @= tf.tfmap[head](*(float(n) for n in load))
        return out
    
    def __matmul__(self, z):
        """Application of this matrix M @ z, where z is a point or another matrix."""
        p = self.v
        if type(z) == tf:
            q = z.v
            return tf(p[0] * q[0] + p[2] * q[1],        p[1] * q[0] + p[3] * q[1],
                      p[0] * q[2] + p[2] * q[3],        p[1] * q[2] + p[3] * q[3],
                      p[0] * q[4] + p[2] * q[5] + p[4], p[1] * q[4] + p[3] * q[5] + p[5])
        elif type(z) == complex:
            return complex(p[0] * z.real + p[2] * z.imag + p[4],
                           p[1] * z.real + p[3] * z.imag + p[5])
        else: return NotImplemented # rmatmul on desired object
    def __invert__(self):
        """Inverse of this matrix, ~M."""
        p = self.v
        det = p[0] * p[3] - p[1] * p[2]
        out = (p[3], -p[1], -p[2], p[0],
               p[2] * p[5] - p[3] * p[4],
               p[1] * p[4] - p[0] * p[5])
        return tf(*(a / det for a in out))
    
    def minstr(self):
        """Shortest representation of this matrix in SVG."""
        p = self.v
        if   isclose(p[0], p[3]) and isclose(p[1], -p[2]): reflected = False
        elif isclose(p[0], -p[3]) and isclose(p[1], p[2]): reflected = True
        else: # matrix not conformal, default output
            pass
        pass

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

def collapsibility(t):
    """1 if the affinity is a scaling + rotation + translation, -1 for the same but with flipping and 0 otherwise."""
    if isclose(t[0], t[3]) and isclose(t[1], -t[2]): return 1
    if isclose(t[0], -t[3]) and isclose(t[1], t[2]): return -1
    return 0
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
def minimisetransform(tfs):
    """If the transform string is collapsible, returns its minimal representation, otherwise returns input."""
    ctm = parsetransform(tfs)
    h = collapsedtransform(ctm)
    if h == None: return "matrix({})".format(numbercrunch(*[floatinkrep(v) for v in ctm]))
    rt, sc = h
    # Translation/rotation (left) part
    dx, dy = floatinkrep(rt[1]), floatinkrep(rt[2])
    if rt[0] is nan: rtstr = ("" if dx == "0" else "translate({})".format(dx)) if dy == "0" else "translate({})".format(numbercrunch(dx, dy))
    else:
        thet = floatinkrep(rt[0])
        rtstr = "rotate({})".format(thet if dx == dy == "0" else numbercrunch(thet, dx, dy))
    # Scaling (right) part
    z = floatinkrep(sc[1])
    scstr = ("" if z == "1" else "scale({})".format(z)) if sc[0] == 1 else "scale({})".format(numbercrunch(z, floatinkrep(-sc[1])))
    return rtstr + scstr

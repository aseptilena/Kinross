# Helper functions for Kinross: affine transformations
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import sin, cos, tan, copysign, degrees, radians, nan
from cmath import isclose, phase, rect, polar
from .regexes import fsmn, catn, tf_re, num_re
from numbers import Number

# [a c e] Affine matrix structure,
# [b d f] implemented in the
# [0 0 1] class below
class tf:
    def __init__(self, a, b, c, d, e, f): self.v = (a, b, c, d, e, f)
    def __str__(self): return "/{:f} {:f} {:f} {:f} {:f} {:f}/".format(*self.v)
    def __repr__(self): return "tf({} {} {} {} {} {})".format(*self.v)
    
    def mx(a, b, c, d, e, f): return tf(a, b, c, d, e, f)
    def tr(dx, dy = 0): return tf(1, 0, 0, 1, dx, dy)
    def sc(sx, sy = None): return tf(sx, 0, 0, sx if sy == None else sy, 0, 0)
    def ro(th, cx = 0, cy = 0):
        cs = rect(1, radians(th))
        return tf(cs.real, cs.imag, -cs.imag, cs.real, (1 - cs.real) * cx + cs.imag * cy,
                                                       (1 - cs.real) * cy - cs.imag * cx)
    def skx(z): return tf(1, 0, tan(radians(z)), 1, 0, 0)
    def sky(z): return tf(1, tan(radians(z)), 0, 1, 0, 0)
    tfmap = {"matrix": mx, "translate": tr, "scale": sc, "rotate": ro, "skewX": skx, "skewY": sky}
    def fromsvg(s):
        """Converts an SVG transform string into its equivalent matrix."""
        out = tf(1, 0, 0, 1, 0, 0)
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
        elif isinstance(z, Number):
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
    
    def isconformal(self):
        a, b, c, d = self.v[:4]
        return isclose(a, d) and isclose(b, -c) or isclose(a, -d) and isclose(b, c) # TODO legacy function, used in spallator
    def tosvg(self):
        """Shortest representation of this matrix in SVG. An empty string returned represents the identity matrix."""
        a, b, c, d, e, f = self.v
        if   isclose(a, d) and isclose(b, -c): reflected = False
        elif isclose(a, -d) and isclose(b, c): reflected = True
        else: return "matrix({})".format(catn(*(fsmn(x) for x in self.v))) # matrix not conformal, default output
        z = complex(a, b)
        r, th = polar(z)
        mr, mth = fsmn(r), fsmn(degrees(th) % 360)
        if reflected: sc_cmd = "scale({0}-{0})".format(mr)
        else: sc_cmd = "scale({})".format(mr) * (mr != "1")
        if isclose(th, 0): # translation
            dx, dy = fsmn(e), fsmn(f)
            if dy == "0": tr_cmd = "translate({})".format(dx) * (dx != "0")
            else: tr_cmd = "translate({})".format(catn(dx, dy))
            return tr_cmd + sc_cmd
        elif isclose(e, 0) and isclose(f, 0): ro_cmd = "rotate({})".format(mth) # rotation about origin
        else:
            z /= r # z.real = cos(th), z.imag = sin(th)
            k, l = 1 - z.real, z.imag
            mx, my = fsmn((e * k - f * l) / (2 * k)), fsmn((e * l + f * k) / (2 * k))
            ro_cmd = "rotate({})".format(catn(mth, mx, my))
        return ro_cmd + sc_cmd
    def minstr(s): return tf.fromsvg(s).tosvg() # convenience function to compress an SVG transformation string

# Helper functions for Kinross: Bézier curve and elliptical arc segments (includes whole ellipses!)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import pi, sqrt, hypot, tan, atan, radians, degrees, floor, ceil
from cmath import polar, isclose
from itertools import product
from .vectors import *
from .affines import tf
from .algebra import rombergquad, pn
from .regexes import fsmn

T, H = pi * 2, pi / 2

# A simple ellipse is considered a special case of the elliptical arc class, the arc spanning the four quadrants.
# Inputs left-to-right are centre, radii, angle of r1 to +x and endpoint params; th normalised to [0, pi).
class ellipt:
    def __init__(self, c = 0j, r1 = 1, r2 = 1, th = None, t0 = 0, t1 = T):
        self.c, self.r2, self.t0, self.t1 = c, abs(r2), t0, t1
        self.r1, self.th = polar(r1) if th == None else (r1, th)
        self.th %= pi
    def __str__(self):
        out = "({:.4f} {:.4f}/{:.4f}@{:.4f}".format(self.c, self.r1, self.r2, self.th)
        if not self.O(): out += " {:.4f}:{:.4f}".format(self.t0, self.t1)
        return out + ")"
    def __repr__(self): return "ellipt({}, {}, {}, {}, {}, {})".format(self.c, self.r1, self.r2, self.th, self.t0, self.t1)
    
    def fromsvg_path(start, rx, ry, theta, large, sweep, end):
        """Given the data in an SVG elliptical arc command, construct the equivalent elliptical object.
        This follows the SVG specs as closely as possible. Endpoints are complex numbers, large and sweep are bools and the rest are floats."""
        if start == end: return None
        if rx == 0 or ry == 0: return bezier(start, end)
        r1, r2 = abs(rx), abs(ry)
        # We now take the start as the origin and transform the end, so that the ellipse required becomes a unit circle.
        disc = tf.sc(1 / r1, 1 / r2) @ tf.ro(-theta) @ (end - start)
        m = disc / 2
        ma, mp = polar(m)
        if ma >= 1:
            res = ellipt(m, ma, ma, 0, None, mp)
            res.t0 = res.t1 + (-1) ** sweep * pi
        else:
            ct = rect(1, mp + (-1) ** (large == sweep) * acos(ma))
            res = ellipt(ct, 1, 1, 0)
            z0, z1 = phase(-ct), phase(disc - ct)
            if z0 < z1 and not sweep: z0 += T
            if z0 > z1 and     sweep: z1 += T
            res.t0, res.t1 = z0, z1
        res = tf.ro(theta) @ tf.sc(r1, r2) @ res
        res.c += start
        return res
    def fromsvg_node(ov):
        """Given an SVG circle or ellipse, returns (ellipse, transform, dictionary of other attributes)."""
        others = ov.attrib.copy()
        cx, cy = float(others.pop("cx", "0")), float(others.pop("cy", "0"))
        if ov.tag.endswith("circle"): rx = ry = float(others.pop("r"))
        elif ov.tag.endswith("ellipse"): rx, ry = float(others.pop("rx")), float(others.pop("ry"))
        r0 = ellipt(complex(cx, cy), rx, ry)
        r1 = tf.fromsvg(others.pop("transform", ""))
        return (r0, r1, others)
    def tosvg_node(self):
        """Returns the SVG representation of this ellipse as a (tag, attribute dictionary). Endpoints are ignored."""
        rx, ry = fsmn(self.r1), fsmn(self.r2)
        if rx == ry: tag, attrib, o = "circle", {"r": rx}, self.c
        else:
            tag, tt = "ellipse", self.th % pi
            if tt >= H: rx, ry, tt = ry, rx, tt - H
            attrib, o, tts = {"rx": rx, "ry": ry}, self.c * rect(1, -tt), fsmn(degrees(tt))
            if tts != "0": attrib["transform"] = "rotate({})".format(tts)
        cx, cy = fsmn(o.real), fsmn(o.imag)
        if cx != "0": attrib["cx"] = cx
        if cy != "0": attrib["cy"] = cy
        return (tag, attrib)
    
    def O(self): return self.t0 == 0 and self.t1 == T # tests whether the ellipse is complete, hence O
    def at(self, t): return self.c + complex(self.r1 * cos(t), self.r2 * sin(t)) * rect(1, self.th) # param t of complete ellipse
    def __call__(self, t): return self.at(linterp(self.t0, self.t1, t)) # param t of arc
    def __getitem__(self, z):
        if type(z) == slice: # segments of arc
            begin = self.t0 if z.start == None else linterp(self.t0, self.t1, z.start)
            end   = self.t1 if z.stop  == None else linterp(self.t0, self.t1, z.stop)
            reverse = -1 if z.step == -1 else 1
            return ellipt(self.c, self.r1, self.r2, self.th, *(begin, end)[::reverse])
        return self(z) # calling a number aliases to value call
    def __neg__(self, t): return ellipt(self.c, self.r1, self.r2, self.th, self.t1, self.t0) # reverse arc; faster alternative to ellipt[::-1]
    def d(self, t): # derivative at param t of arc
        on = linterp(self.t0, self.t1, t)
        return (-1) ** (self.t0 > self.t1) * complex(-sin(on) * self.r1, cos(on) * self.r2) * rect(1, self.th)
    
    def __rmatmul__(self, m): # Rytz's construction used here
        d = m @ self.c
        u_, v = m @ self.at(0) - d, m @ self.at(H) - d
        if isclose(angle(u_, v), H): res = ellipt(d, u_, v)
        u = u_ * 1j
        s, w = (u + v) / 2, (u - v) / 2
        sa, wa = abs(s), abs(w)
        res = ellipt(d, sa + wa, sa - wa, phase(s - rect(sa, phase(w))))
        if not self.O():
            z = lambda p: phase(tf.sc(1 / res.r1, 1 / res.r2) @ ((m @ p - d) * rect(1, -res.th)))
            z0, z1 = z(self(0)), z(self(1))
            if (self.t0 > self.t1) ^ (m.v[0] * m.v[3] - m.v[1] * m.v[2] < 0) != (z0 > z1): # is the arc flow correct?
                if   z0 < z1: z0 += T
                elif z0 > z1: z1 += T
            res.t0, res.t1 = z0, z1
        return res
    
    def perim(self):
        """Perimeter of whole ellipse. Iterative formula for elliptic integral from Semjon Adlaj (http://www.ams.org/notices/201208/rtx120801094p.pdf)."""
        if self.r1 == self.r2: return T * self.r1
        beta = (self.r2 / self.r1) ** (-1) ** (self.r2 > self.r1)
        nx, ny, nz = 1, beta * beta, 0
        while not isclose(nx, ny, abs_tol=1e-14):
            rd = sqrt((nx - nz) * (ny - nz))
            nx, ny, nz = (nx + ny) / 2, nz + rd, nz - rd
        mx, my = 1, beta
        while not isclose(mx, my, abs_tol=1e-14): mx, my = (mx + my) / 2, sqrt(mx * my)
        return (nx + ny) / (mx + my) * T * max(self.r1, self.r2)

class bezier:
    def __init__(self, *w):
        if not 1 < len(w) < 5: raise TypeError("bezier only takes two to four points")
        self.p, self.deg = w, len(w) - 1
        if   self.deg == 3: l = (w[0], 3 * (w[1] - w[0]), 3 * (w[2] - 2 * w[1] + w[0]), w[3] - 3 * w[2] + 3 * w[1] - w[0])
        elif self.deg == 2: l = (w[0], 2 * (w[1] - w[0]), w[2] - 2 * w[1] + w[0])
        elif self.deg == 1: l = (w[0], w[1] - w[0])
        self.xypn = pn(*(n.real for n in l)), pn(*(n.imag for n in l)) # polynomials in the x and y directions
    def __str__(self): return "<{}>".format(" ".join("{:.4f}".format(n) for n in self.p))
    def __repr__(self): return "bezier({})".format(", ".join([str(n) for n in self.p]))
    
    def __call__(self, t):
        if t == 0: return self.p[0]
        if t == 1: return self.p[-1]
        q = self.p[:]
        while len(q) > 1: q = [linterp(q[i], q[i + 1], t) for i in range(len(q) - 1)]
        return q[0]
    def start(self): return self.p[0]
    def end(self): return self.p[-1]
    def split(self, t):
        """Splits the curve at parameter t, returning a list that can then be inserted."""
        bef, aft, q = [self.p[0]], [self.p[-1]], self.p[:]
        while len(q) > 1:
            q = [linterp(q[i], q[i + 1], t) for i in range(len(q) - 1)]
            bef.append(q[0])
            aft.append(q[-1])
        return [bezier(*bef), bezier(*aft[::-1])]
    def __neg__(self): return bezier(*self.p[::-1])
    
    def deriv(self):
        """The derivative of this Bézier curve."""
        return bezier(*[self.deg * (self.p[i + 1] - self.p[i]) for i in range(self.deg)])
    def velocity(self, t):
        """The velocity (derivative) of this curve at parameter t."""
        return self.deriv()(t)
    
    def __rmatmul__(self, m): return bezier(*(m @ s for s in self.p))
    
    def bounds(self): # orthogonal bounding box, represented as two opposite points
        if self.deg == 1: return pointbounds(self.p)
        xb, yb = ([self(t) for t in z.d().reals() if 0 < t < 1] for z in self.xypn)
        return pointbounds(xb + yb + [self(0), self(1)])
    
    def kind(self):
        """Returns the kind of this Bézier curve according to https://pomax.github.io/bezierinfo/#canonical with any significant points.
        N = 0 to 2 for loopless curves with inflection parameters (may fall outside (0, 1)); -1 for loops with self-intersection parameters."""
        nothing = (0, []) # What is returned when there are no inflections or loops
        if self.deg < 3: return nothing
        if collinear(*self.p[:3]):
            if collinear(*self.p[1:]): return nothing
            p11, p01, p00 = self.p[1:]
            p4 = self.p[0]
        else:
            p00, p01, p11 = self.p[:3]
            p4 = self.p[3]
        xv, yv = p11 - p01, p01 - p00
        clue = ~tf(xv.real, xv.imag, yv.real, yv.imag, p00.real, p00.imag) @ p4
        x, y = clue.real, clue.imag
        if y >= 1 and x < 1 or y > 1 and x >= 1: num = 1
        elif x * (x - 2) + 4 * y >= 3 and x < 1: num = 2
        else:
            K = x * (3 - x)
            if K < 3 * y and x < 0 or K < y * (x + y) and x < 1 and y > 0: num = -1
            else: return nothing
        if num > 0:
            xp, yp = (z.d() for z in self.xypn)
            xpp, ypp = xp.d(), yp.d()
            return (num, (xp * ypp - yp * xpp).reals())
        else:
            # Because the curve is cubic the equations are conic sections and solving is quite simple.
            [c, b, a], [f, e, d] = [s[1:] for s in self.xypn]
            # These conics are {a, a, a, b, b, c} and {d, d, d, e, e, f} (powers from left to right are x², xy, y², x, y, 1).
            # The degenerate conic between them is (b + ez)(x + y) + (c + fz) = 0 where z = -a / d, so the sum of solutions (x + y) is:
            J = (a * f - c * d) / (b * d - a * e)
            # Adding axy on both sides of the x-coordinate equation yields ax² + 2axy + ay² + bx + by + c = axy,
            # which reduces to aJ² + bJ + c = axy. The product of solutions (xy) is thus:
            K = pn(c / a, b / a, 1)(J)
            # A polynomial with x and y as its roots can then be constructed and the self-intersection parameters found.
            return (num, pn(K, -J, 1).reals())
    def lenf(self):
        """Like the elliptical arc class, returns the integrand of the arc length integral for this curve."""
        def z(t): return abs(self.velocity(t))
        return z
    def length(self, end = 1, start = 0):
        """The length of this curve between the specified endpoint parameters."""
        if self.deg == 1: return abs(self.p[1] - self.p[0])
        knots = [start] + [t for t in self.kind()[1] if start < t < end] + [end]
        return sum([rombergquad(self.lenf(), knots[i], knots[i + 1]) for i in range(len(knots) - 1)])
    def invlength(self, frac):
        """Computes the t value where self.length(t) / self.length() = frac. This and the corresponding elliptical arc function use the Illinois algorithm."""
        if frac <= 0: return 0
        if frac >= 1: return 1
        if self.deg == 1: return frac
        whole = self.length()
        target, fa = frac * whole, self.length(frac)
        lower, higher = (frac, 1) if fa < target else (0, frac)
        flower, fire, status = self.length(lower), self.length(higher), 0
        for q in range(64):
            if not isclose(lower, higher, rel_tol=1e-15):
                mt = (target - flower) / (fire - flower)
                if status == 2: mt, status = mt / 2, 0
                elif status == -2: mt, status = (1 + mt) / 2, 0
                mid = linterp(lower, higher, mt)
                fmid = self.length(mid)
                if fmid < target: lower, flower, status = mid, fmid, min(-1, status - 1)
                elif fmid > target: higher, fire, status = mid, fmid, max(1, status + 1)
                else: break
            else: break
        return round(mid, 12)
    def projection(self, z):
        """The parameter t corresponding to the projection of z onto the curve; the smallest t is returned if two or more parameters tie for shortest distance."""
        def dist(t): return abs(self(t) - z)
        x, y = self.polyns()
        dx, dy = self.deriv().polyns()
        x[0], y[0] = x[0] - z.real, y[0] - z.imag
        return sorted([0] + [t for t in (x * dx + y * dy).rroots() if 0 < t < 1] + [1], key=dist)[0]

class elliparc: # functions not yet migrated are here
    def boundingbox(self):
        """The elliptical arc's orthogonal bounding box."""
        if isclose(self.ell.tilt, 0) or isclose(abs(self.ell.tilt), H): tbnds = (0, H)
        else:
            r = self.ell.ry / self.ell.rx
            tbnds = (atan(-r * tan(self.ell.tilt)), atan(r / tan(self.ell.tilt)))
        tl, tm = sorted([self.tstart, self.tend])
        tangs = [[self.ell.parampoint(pi * i + c) for i in range(ceil((tl - c) / pi), floor((tm - c) / pi) + 1)] for c in tbnds]
        return pointbounds(tangs[0] + tangs[1] + [self.start(), self.end()])
    
    def lenf(self):
        """The function that is integrated to obtain the length of this arc."""
        def z(t): return hypot(sin(t) * self.ell.rx, cos(t) * self.ell.ry)
        return z
    def length(self, end = None, start = None):
        """The length of this arc between the specified parameters. None signifies that the length extends to the respective end (0 or 1)."""
        if end != None or start != None:
            if start == None: return self.split(end)[0].length()
            elif end == None: return self.split(start)[1].length()
            else: return self.split(end)[0].split(start / end)[1].length()
        if isclose(self.tstart, self.tend): return 0
        lf = self.lenf()
        if (self.tend - self.tstart) * (self.ef - self.sf) < 0: return abs(rombergquad(lf, self.tstart, self.tend))
        sl = rombergquad(lf, self.tstart, self.sf * H) + self.ell.quartrarc() * (self.ef - self.sf) + rombergquad(lf, self.ef * H, self.tend)
        return -sl if self.tend < self.tstart else sl
    def invlength(self, frac):
        """Computes the t value where self.length(t) / self.length() = frac."""
        if frac <= 0: return 0
        if frac >= 1: return 1
        whole = self.length()
        target, fa = frac * whole, self.length(frac)
        lower, higher = (frac, 1) if fa < target else (0, frac)
        flower, fire, status = self.length(lower), self.length(higher), 0
        for q in range(64):
            if not isclose(lower, higher, rel_tol=1e-15):
                mt = (target - flower) / (fire - flower)
                if status == 2: mt, status = mt / 2, 0
                elif status == -2: mt, status = (1 + mt) / 2, 0
                mid = linterp(lower, higher, mt)
                fmid = self.length(mid)
                if fmid < target: lower, flower, status = mid, fmid, min(-1, status - 1)
                elif fmid > target: higher, fire, status = mid, fmid, max(1, status + 1)
                else: break
            else: break
        return round(mid, 12)

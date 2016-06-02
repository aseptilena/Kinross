# Helper functions for Kinross: Bézier curve and elliptical arc segments (includes whole ellipses!)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import pi, sqrt, hypot, tan, atan, radians, floor, ceil
from cmath import polar, isclose
from itertools import product
from .vectors import *
from .affines import affine, backaffine
from .algebra import rombergquad, polyn
from .regexes import floatinkrep
from .ellipse import oval

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
    
    def O(self): return self.t0 == 0 and self.t1 == T # tests whether the ellipse is complete, hence O
    def at(self, t): return self.c + complex(self.r1 * cos(t), self.r2 * sin(t)) * rect(1, self.th) # param t of complete ellipse
    def __call__(self, t): return self.at(linterp(self.t0, self.t1, t)) # param t of arc
    def __neg__(self, t): return ellipt(self.c, self.r1, self.r2, self.th, self.t1, self.t0) # reverse arc
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
            pass # TODO
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
    def __init__(self, *p):
        self.p = list(p)[:min(4, len(p))] # cull to cubic curves, since they are the highest degree used in SVG
        self.deg = len(self.p) - 1
    def __str__(self): return "<{}>".format(" ".join(["{:.4f}".format(n) for n in self.p]))
    def __repr__(self): return "bezier({})".format(", ".join([str(n) for n in self.p]))
    
    def __call__(self, t):
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
    def reverse(self):
        """Returns the curve reversed."""
        return bezier(*self.p[::-1])
    def isdegenerate(self):
        """True if all control points are coincident."""
        return min([isclose(self.p[-1], self.p[i]) for i in range(len(self.p) - 1)])
    
    def deriv(self):
        """The derivative of this Bézier curve."""
        return bezier(*[self.deg * (self.p[i + 1] - self.p[i]) for i in range(self.deg)])
    def velocity(self, t):
        """The velocity (derivative) of this curve at parameter t."""
        return self.deriv()(t)
    def startdirc(self):
        N = 1
        while N <= self.deg:
            if not isclose(self.p[N], self.p[0]): return self.p[N] - self.p[0]
            N += 1
        return 1
    def enddirc(self):
        N = self.deg - 1
        while N >= 0:
            if not isclose(self.p[N], self.p[-1]): return self.p[N] - self.p[-1]
            N -= 1
        return -1
    
    def affine(self, mat):
        """Transforms the curve by the given matrix."""
        return bezier(*[affine(mat, n) for n in self.p])
    def xypolyns(self):
        """Returns the (x-component, y-component) polynomials of this curve."""
        cp = self.p
        if   self.deg == 3: l = (cp[0], 3 * (cp[1] - cp[0]), 3 * (cp[2] - 2 * cp[1] + cp[0]), cp[3] - 3 * cp[2] + 3 * cp[1] - cp[0])
        elif self.deg == 2: l = (cp[0], 2 * (cp[1] - cp[0]), cp[2] - 2 * cp[1] + cp[0])
        elif self.deg == 1: l = (cp[0], cp[1] - cp[0])
        return (polyn(*[n.real for n in l]), polyn(*[n.imag for n in l]))
    def boundingbox(self):
        """The orthogonal bounding box of this curve as a tuple of two opposite points."""
        if self.deg == 1: return pointbounds(self.p)
        xb, yb = [[self(t) for t in pn.deriv().rroots() if 0 < t < 1] for pn in self.xypolyns()]
        return pointbounds(xb + yb + [self.start(), self.end()])
    
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
        clue = backaffine((xv.real, xv.imag, yv.real, yv.imag, p00.real, p00.imag), p4)
        x, y = clue.real, clue.imag
        if y >= 1 and x < 1 or y > 1 and x >= 1: num = 1
        elif x * (x - 2) + 4 * y >= 3 and x < 1: num = 2
        else:
            K = x * (3 - x)
            if K < 3 * y and x < 0 or K < y * (x + y) and x < 1 and y > 0: num = -1
            else: return nothing
        if num > 0:
            d1 = self.deriv()
            xp, yp = d1.xypolyns()
            xpp, ypp = d1.deriv().xypolyns()
            return (num, (xp * ypp - yp * xpp).rroots())
        else:
            # Because the curve is cubic the equations are conic sections and solving is quite simple.
            [c, b, a], [f, e, d] = [f.a[1:] for f in self.xypolyns()]
            # These conics are {a, a, a, b, b, c} and {d, d, d, e, e, f} (powers from left to right are x², xy, y², x, y, 1).
            # The degenerate conic between them is (b + ez)(x + y) + (c + fz) = 0 where z = -a / d, so the sum of solutions (x + y) is:
            J = (a * f - c * d) / (b * d - a * e)
            # Adding axy on both sides of the x-coordinate equation yields ax² + 2axy + ay² + bx + by + c = axy,
            # which reduces to aJ² + bJ + c = axy. The product of solutions (xy) is thus:
            K = polyn(c / a, b / a, 1)(J)
            # A polynomial with x and y as its roots can then be constructed and the self-intersection parameters found.
            return (num, polyn(K, -J, 1).rroots())
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
        x, y = self.xypolyns()
        dx, dy = self.deriv().xypolyns()
        x[0], y[0] = x[0] - z.real, y[0] - z.imag
        return sorted([0] + [t for t in (x * dx + y * dy).rroots() if 0 < t < 1] + [1], key=dist)[0]

class elliparc:
    def __init__(self, *data):
        """Initialises the Kinross arc. tstart to tend is increasing if the arc turns clockwise; phi is in degrees."""
        self.deg = -1
        if len(data) == 3: # tstart, ell, tend (Kinross representation)
            self.tstart, self.ell, self.tend = data
        elif len(data) == 7: # start, rx, ry, phi, large, sweep, end (SVG representation)
            start, rx, ry, phi, large, sweep, end = data
            if isclose(start, end): self.tstart, self.tend, self.ell = 7, 7, [start, end]
            else:
                rx, ry, phi = abs(rx), abs(ry), radians(phi)
                if rx < 1e-8 or ry < 1e-8: self.tstart, self.tend, self.ell = 8, 8, [start, end]
                else:
                    z1, z2, mid = turn(rx, phi), turn(ry * 1j, phi), between(start, end)
                    uc2e = (z1.real, z1.imag, z2.real, z2.imag, mid.real, mid.imag)
                    astt, aend = backaffine(uc2e, start), backaffine(uc2e, end)
                    large, sweep = large != 0, sweep != 0 # True = 1, False = 0
                    if abs(astt - aend) >= 2: # There is only one ellipse or the ellipse is too small
                        c, self.tstart, self.tend = mid, phase(astt), phase(aend)
                    else:
                        l = abs(astt)
                        rac = sqrt(1 - l * l)
                        ac = rect(rac, phase(astt) + H * (1 if large == sweep else -1))
                        c, self.tstart, self.tend = affine(uc2e, ac), phase(astt - ac), phase(aend - ac)
                    self.ell = oval(c, rx, ry, phi)
                    if self.tstart > self.tend and     sweep: self.tend += 2 * pi
                    if self.tstart < self.tend and not sweep: self.tend -= 2 * pi
        if type(self.ell) == oval: # These values aid the arc length computation
            sr, er = (floor, ceil) if self.tend < self.tstart else (ceil, floor)
            self.sf, self.ef = sr(self.tstart / H), er(self.tend / H)
    def __str__(self): #
        return "{{{} {} {} {} {}:{}}}".format(floatinkrep(self.ell.centre.real) + "," + floatinkrep(self.ell.centre.imag),
                                              floatinkrep(self.ell.rx), floatinkrep(self.ell.ry), floatinkrep(self.ell.tilt), self.tstart, self.tend)
    def __repr__(self): #
        return "elliparc({}, {}, {})".format(self.tstart, repr(self.ell), self.tend)
    
    def __call__(self, t): #
        """See? This is why the endpoint parameters are allowed to go outside the principal range here."""
        return self.ell.parampoint(linterp(self.tstart, self.tend, t))
    def start(self): return self.ell.parampoint(self.tstart) # arc(0)
    def end(self): return self.ell.parampoint(self.tend) # arc(1)
    def split(self, t):
        """Splits the arc at parameter t, returning a list that can then be inserted."""
        mv = linterp(self.tstart, self.tend, t)
        return [elliparc(self.tstart, self.ell, mv), elliparc(mv, self.ell, self.tend)]
    def reverse(self): # -arc
        """Returns the arc reversed."""
        return elliparc(self.tend, oval(self.ell.centre, self.ell.rx, self.ell.ry, self.ell.tilt), self.tstart)
    
    def velocity(self, t): # arc.d
        """Returns the velocity (first derivative) of the curve at parameter t."""
        et = linterp(self.tstart, self.tend, t)
        return turn(complex(-sin(et) * self.ell.rx, cos(et) * self.ell.ry) * (1 if tstart < tend else -1), self.ell.tilt)
    def startdirc(self): return self.velocity(0) # arc.d(0)
    def enddirc(self): return -self.velocity(1) # -arc.d(1)
    
    def affine(self, mat):
        """Transforms the arc by the given matrix."""
        nell, pst, pen = self.ell.affine(mat), affine(mat, self.start()), affine(mat, self.end())
        z = nell.uc_affine()
        start, end = phase(affine(z, pst)), phase(affine(z, pen))
        if self.tstart < self.tend and start > end: end += 2 * pi
        if self.tstart > self.tend and start < end: start += 2 * pi
        return elliparc(start, nell, end)
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

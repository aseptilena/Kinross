# Helper functions for Kinross: linear, quadratic and cubic Bézier curves
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from cmath import isclose
from itertools import product
from .vectors import linterp, pointbounds, collinear
from .affines import affine, backaffine
from .algebra import rombergquad, polyn
from .regexes import floatinkrep

class bezier:
    def __init__(self, *p):
        self.p = list(p)[:min(4, len(p))] # cull to cubic curves, since they are the highest degree used in SVG
        self.deg = len(self.p) - 1
    def __str__(self): return "<{}>".format(" ".join([floatinkrep(n.real) + "," + floatinkrep(n.imag) for n in self.p]))
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
    
    def derivative(self):
        """The derivative of this Bézier curve."""
        return bezier(*[self.deg * (self.p[i + 1] - self.p[i]) for i in range(self.deg)])
    def velocity(self, t):
        """The velocity (derivative) of this curve at parameter t."""
        return self.derivative()(t)
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
        p10 = p00 + p11 - p01
        xv, yv = p10 - p00, p01 - p00
        clue = backaffine((xv.real, xv.imag, yv.real, yv.imag, p00.real, p00.imag), p4)
        x, y = clue.real, clue.imag
        if y >= 1 and x < 1 or y > 1 and x >= 1: num = 1
        elif x * (x - 2) + 4 * y >= 3 and x < 1: num = 2
        else:
            K = -x * (x - 3)
            if K < 3 * y and x < 0 or K < y * (x + y) and x < 1 and y > 0: num = -1
            else: return nothing
        if num > 0:
            d1 = self.derivative()
            xp, yp = d1.xypolyns()
            xpp, ypp = d1.derivative().xypolyns()
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

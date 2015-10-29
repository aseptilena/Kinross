# Helper functions for Kinross: linear, quadratic and cubic Bézier curves
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from cmath import isclose
from .vectors import linterp, pointbounds
from .affines import affine
from .algebra import rombergquad, polynomroot
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
        """The derivative Bézier curve of this Bézier curve."""
        return bezier(*[self.deg * (self.p[i + 1] - self.p[i]) for i in range(self.deg)])
    def velocity(self, t):
        """The velocity (first derivative) of this curve at parameter t."""
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
    
    def coordpolynoms(self):
        """Returns the (x-component, y-component) polynomial coefficients of this curve."""
        cp = self.p
        if   self.deg == 3: pp = (cp[0], 3 * (cp[1] - cp[0]), 3 * (cp[2] - 2 * cp[1] + cp[0]), cp[3] - 3 * cp[2] + 3 * cp[1] - cp[0])
        elif self.deg == 2: pp = (cp[0], 2 * (cp[1] - cp[0]), cp[2] - 2 * cp[1] + cp[0])
        elif self.deg == 1: pp = (cp[0], cp[1] - cp[0])
        return (tuple(map(lambda p: p.real, pp)), tuple(map(lambda p: p.imag, pp)))
    def inflections(self):
        """Returns the inflection points of this curve."""
        # For a cubic curve:
        # x = A, B, C, D; y = E, F, G, H
        # x' = A', B', C'; y' = E', F', G' (t from 0 to 1)
        # x'' = A'', B''; y'' = E'', F''
        # Then numerator of signed curvature = x'y'' - y''x'
        # =   E'' F''      A'' B''
        #  A' 3   2     E' 3   2
        # 2B' 2   1  - 2F' 2   1
        #  C' 1   0     G' 1   0 (numbers denote powers of 1 - t in term)
        if self.deg == 3:
            d1 = self.derivative()
            d2 = d1.derivative()
            xp, yp = tuple(zip(*((c.real, c.imag) for c in d1.p)))
            xpp, ypp = tuple(zip(*((c.real, c.imag) for c in d2.p)))
            first  = xp[0] * ypp[0] - yp[0] * xpp[0]
            second = 2 * xp[1] * ypp[0] + xp[0] * ypp[1] - (2 * yp[1] * xpp[0] + yp[0] * xpp[1])
            third  = xp[2] * ypp[0] + 2 * xp[1] * ypp[1] - (yp[2] * xpp[0] + 2 * yp[1] * xpp[1])
            fourth = xp[2] * ypp[1] - yp[2] * xpp[1]
            # p(t) coeffs:       3  2  1  0
            # first contributes -1 +3 -3 +1
            # second            +1 -2 +1
            # third             -1 +1
            # fourth            +1
            # Roots of p(t) between 0 and 1 = inflection points
            tentinflect = polynomroot([first, second - 3 * first, 3 * first - 2 * second + third, fourth - third + second - first])[0]
            return [t for t in tentinflect if 0 <= t <= 1]
        return []
    
    def lenf(self):
        """Like the elliptical arc class, returns the integrand of the arc length integral for this curve."""
        def z(t): return abs(self.velocity(t))
        return z
    def length(self, end = None, start = None):
        """The length of this curve between the specified endpoint parameters (omitted start and end values correspond to 0 and 1 respectively)."""
        if end != None or start != None:
            if start == None: return self.split(end)[0].length()
            elif end == None: return self.split(start)[1].length()
            else: return self.split(end)[0].split(start / end)[1].length()
        knots = [0] + sorted(self.inflections()) + [1]
        return sum([rombergquad(self.lenf(), knots[i], knots[i + 1]) for i in range(len(knots) - 1)])
    
    def affine(self, mat):
        """Transforms the curve by the given matrix."""
        return bezier(*[affine(mat, n) for n in self.p])
    def boundingbox(self):
        """The orthogonal bounding box of this curve as a tuple of two opposite points."""
        if self.deg == 1: return pointbounds(self.p)
        xtremat, ytremat = tuple(map(lambda l: [t for t in polynomroot([i * l[i] for i in range(1, len(l))])[0] if 0 < t < 1], self.coordpolynoms()))
        return pointbounds([self(t) for t in xtremat] + [self(t) for t in ytremat] + [self.start(), self.end()])

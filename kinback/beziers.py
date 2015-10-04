# Helper functions for Kinross: linear, quadratic and cubic Bézier curves
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import linterp, affine
from .algebra import simpquad
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
    
    def velocity(self, t):
        """The velocity (first derivative) of this curve at parameter t."""
        return bezier(*[self.deg * (self.p[i + 1] - self.p[i]) for i in range(self.deg)])(t)
    def startdirc(self): return self.p[1] - self.p[0]
    def enddirc(self): return self.p[-2] - self.p[-1] # Defining the end direction as such makes the mitre angle simply the angle between the tangents
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
        lf = self.lenf()
        return simpquad(lf, 0, 1)
    def affine(self, mat):
        """Transforms the curve by the given matrix."""
        return bezier(*[affine(mat, n) for n in self.p])

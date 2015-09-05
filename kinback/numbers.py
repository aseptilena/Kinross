#!/usr/bin/env python3.4
# Helper functions for Kinross: numeric functions and classical algebra
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sqrt, copysign

def near(a, b = 0., e = 1e-5):
    """Checks if the difference between two numbers is within the given tolerance (using the L2 metric for a more natural treatment of complex numbers).
    The second argument can be left out to represent zero."""
    return abs(b - a) <= e
def lineareq2(a, b, p, c, d, q):
    """ax + by = p; cx + dy = q; returns (x, y)."""
    det = a * d - b * c
    if near(det): return (None, None)
    return ((p * d - q * b) / det, (a * q - c * p) / det)

# Polynomial class; includes root-finding algorithms
class polynomial:
    """A polynomial stores a list of coefficients [a0, a1, a2, ...]
    where a0 is the constant term, a1 is the x term and so on."""
    def __init__(self, coeffs = [0.]):
        if type(coeffs) in (int, float, complex): self.a = [coeffs]
        else: self.a = list(coeffs[:])
    def __str__(self): return " + ".join([str(self.a[i]) + "*x^" + str(i) for i in self.poweriter()])
    def __repr__(self): return "polynomial([" + ",".join([str(c) for c in self.a]) + "])"
    def __getitem__(self, n): return self.a[n] # The coefficient associated with the n-th power; leading coefficient is self[-1]
    def __len__(self): return len(self.a)
    def deg(self): return len(self) - 1
    def poweriter(self, up = False):
        """An iterator over the powers of the polynomial; defaults to counting towards the constant term but can be reversed."""
        return range(len(self)) if up else range(len(self) - 1, -1, -1)
    def at(self, x):
        """The Horner scheme for polynomial evaluation."""
        res = 0.
        for i in self.poweriter(): res = self[i] + res * x
        return res
    
    def __add__(self, q):
        pp = [c for c in self.a] + [0.] * max(len(q) - len(self), 0)
        for k in q.poweriter(True): pp[k] += q[k]
        return polynomial(pp)
    def __sub__(self, q):
        pp = [c for c in self.a] + [0.] * max(len(q) - len(self), 0)
        for k in q.poweriter(True): pp[k] -= q[k]
        return polynomial(pp)
    def __neg__(self): return polynomial([-c for c in self.a])
    def addzeroroots(self, n = 1):
        """The polynomial is multiplied by x^n, thereby introducing n roots of zero."""
        return polynomial([0.] * n + self.a)
    def __mul__(self, q): # Lists, complex numbers and other things get equal treatment
        if type(q) in (float, int, complex): return polynomial([c * q for c in self.a])
        else:
            r = polynomial()
            for i in q.poweriter(True): r += (self * q[i]).addzeroroots(i)
            return r
    def __rmul__(self, q): return self * q
    def __divmod__(self, b):
        # Euclidean algorithm for polynomials
        q, r, d, c = polynomial(), polynomial(self.a), b.deg(), b[-1]
        while r.deg() >= d:
            s = polynomial(r[-1] / c).addzeroroots(r.deg() - d)
            q += s
            r -= s * b
            r.a.pop()
        return (q, r)
    def __floordiv__(self, b): return divmod(self, b)[0]
    def __mod__(self, b): return divmod(self, b)[1]
    def __truediv__(self, b): return self // b
    def ruffini(self, r):
        """Divides the polynomial by x - r using the Ruffini scheme, ignoring remainder."""
        res = []
        for i in self.poweriter():
            if i == self.deg(): res.append(self[i])
            else: res = [res[0] * r + self[i]] + res
        return polynomial(res[1:])
    def deriv(self): return polynomial([i * self[i] for i in range(1, len(self))])
    def antideriv(self): return polynomial([0.] + [self[i] / (i + 1) for i in self.poweriter(True)])
    def striplead(self, prec = 1e-10):
        """Strips leading zeros of the polynomial in-place to the specified precision."""
        while near(self[-1], 0., prec): self.a.pop()
        
    def roots(self, prec = 1e-10):
        """Finds all the roots of the polynomial, returning the list of [[real roots], [complex roots]]. Leading zeros are stripped first.
        The quadratic evaluation is numerically stable; see https://people.csail.mit.edu/bkph/articles/Quadratics.pdf for the derivation.
        Higher polynomials are handled by bisecting on odd degrees and Bairstow's method on even degrees."""
        self.striplead(prec)
        if self.deg() == 0: return [[], []]
        elif self.deg() == 1: return [[-self[0] / self[1]], []]
        elif self.deg() == 2:
            a, b, c = self[2], self[1], self[0]
            d = b * b - 4 * a * c
            e = sqrt(abs(d))
            if d < 0:
                r, i = -b / (2 * a), e / (2 * a)
                return [[], [complex(r, -i), complex(r, i)]]
            if b < 0: return [[2 * c / (-b + e), (-b + e) / 2 / a], []]
            return [[(-b - e) / 2 / a, 2 * c / (-b - e)], []]
        elif self.deg() % 2:
            d = self[0]
            if near(d, 0., prec):
                q = self.ruffini(0.).roots()
                q[0].append(0.)
                return q
            else:
                a = self[-1]
                z, fz = -copysign(0.5, d * a), copysign(1, d)
                while d * fz > 0:
                    z *= 2
                    fz = self.at(z)
                    if near(fz, 0., prec):
                        q = self.ruffini(z).roots()
                        q[0].append(z)
                        return q
                lower, higher = (z, 0.) if d * a > 0 else (0., z)
                flower, fire = self.at(lower), self.at(higher)
                N = 0
                while not near(lower, higher, prec) and N < 100:
                    mid = (lower + higher) / 2
                    fmid = self.at(mid)
                    if abs(fmid) == 0.:
                        q = self.ruffini(mid).roots()
                        q[0].append(mid)
                        return q
                    if fmid * flower > 0: lower, flower = mid, fmid
                    else: higher, fire = mid, fmid
                    N += 1
                res = (higher + lower) / 2
                q = self.ruffini(res).roots()
                q[0].append(res)
                return q
        else:
            # TODO
            return "???"

def bairstowconstants(p, u, v):
    """Calculates the constants c, d, g and h for Bairstow's method from u and v with respect to a polynomial p.
    divmod(p, polynomial(v, u, 1)) = (q, polynomial(d, c));
    divmod(q, polynomial(v, u, 1)) = (r, polynomial(h, g))."""
    pass # TODO

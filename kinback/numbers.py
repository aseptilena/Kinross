#!/usr/bin/env python3.4
# Helper functions for Kinross: numeric functions and classical algebra
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

# Exact decimal arithmetic is used in the polynomial class to mitigate floating-point follies. This is precision, you know.
from decimal import Decimal as D, getcontext
getcontext().prec = 60
zero = D(0)

def near(a, b = 0., e = 1e-5):
    """Checks if the difference between two numbers is within the given tolerance (using the L2 metric for a more natural treatment of complex numbers).
    The second argument can be left out to represent zero."""
    if type(a) == D or type(b) == D: return abs(D(a) - D(b)) <= e
    return abs(b - a) <= e
def lineareq2(a, b, p, c, d, q):
    """ax + by = p; cx + dy = q; returns (x, y)."""
    det = a * d - b * c
    if near(det): return (None, None)
    return ((p * d - q * b) / det, (a * q - c * p) / det)

# Polynomial class; includes root-finding algorithms
class polynomial:
    """A polynomial stores a list of Decimal coefficients [a0, a1, a2, ...] where a0 is the constant term, a1 is the x term and so on.
    Note that because of this only real coefficients are supported."""
    def __init__(self, coeffs = 0):
        if type(coeffs) in (int, float, D): self.a = [D(coeffs)]
        else: self.a = [D(c) for c in coeffs]
    def __getitem__(self, n): return self.a[n] # The coefficient associated with the nth power; leading coefficient is self[-1]
    def __setitem__(self, n, v): self.a[n] = D(v)
    def __len__(self): return len(self.a)
    def deg(self): return len(self) - 1
    def powers(self):
        """An iterator over the powers of the polynomial, counting towards the constant term."""
        return range(len(self) - 1, -1, -1)
    def __str__(self): return " + ".join([str(self.a[i]) + "*x^" + str(i) for i in self.powers()])
    def __repr__(self): return "polynomial([" + ",".join([repr(c) for c in self.a]) + "])"
    def __call__(self, x):
        """The Horner scheme for polynomial evaluation. Since this is what polynomials are all about it seemed natural to assign this method as such."""
        res = zero
        for i in self.powers(): res = res.fma(x, self[i])
        return res
    def __add__(self, q):
        res = []
        for p in range(max(len(self), len(q))):
            if p >= len(self): res.append(q[p])
            elif p >= len(q): res.append(self[p])
            else: res.append(self[p] + q[p])
        return polynomial(res)
    def __sub__(self, q):
        res = []
        for p in range(max(len(self), len(q))):
            if p >= len(self): res.append(-q[p])
            elif p >= len(q): res.append(self[p])
            else: res.append(self[p] - q[p])
        return polynomial(res)
    def __neg__(self): return polynomial([-c for c in self.a])
    def addzeroroots(self, n = 1):
        """The polynomial is multiplied by x^n, thereby introducing n roots of zero."""
        return polynomial([0] * n + self.a)
    def __mul__(self, q):
        if type(q) in (int, float, D): return polynomial([c * D(q) for c in self.a])
        else:
            res = polynomial()
            for i in range(len(q)): res += (self * q[i]).addzeroroots(i)
            return res
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
        for i in self.powers():
            if i == self.deg(): res.append(self[i])
            else: res.insert(0, res[0].fma(r, self[i]))
        return polynomial(res[1:])
    def deriv(self): return polynomial([i * self[i] for i in range(1, len(self))])
    def antideriv(self): return polynomial([0.] + [self[i] / (i + 1) for i in range(len(self))])
    def striplead(self, prec = 1e-10):
        """Strips leading zeros of the polynomial in-place to the specified precision."""
        while near(self[-1], 0, prec): self.a.pop()
        
    def roots(self, prec = 1e-10):
        """Finds all the roots of the polynomial, returning a list of [[real roots] and [complex roots]] to the specified precision.
        The quadratic evaluation is numerically stable; see https://people.csail.mit.edu/bkph/articles/Quadratics.pdf for the derivation.
        Higher polynomials are handled by bisecting/Newton's method on odd degrees and Bairstow's method on even degrees."""
        self.striplead(prec)
        if self.deg() == 0: return [[], []]
        elif self.deg() == 1: return [[-self[0] / self[1]], []]
        elif self.deg() == 2:
            a, b, c = self[2], self[1], self[0]
            d = b * b - 4 * a * c
            e = abs(d).sqrt()
            if d < 0:
                r, i = -b / (2 * a), e / (2 * a)
                return [[], [complex(r, -i), complex(r, i)]]
            if b < 0: return [[(2 * c) / (-b + e), (-b + e) / (2 * a)], []]
            return [[(-b - e) / (2 * a), (2 * c) / (-b - e)], []]
        elif self.deg() % 2: # Odd-degree polynomials always have at least one real root by the intermediate value theorem
            d = self[0]
            if near(d, 0, prec):
                q = self.ruffini(0.).roots()
                q[0].append(0.)
                return q
            else:
                a = self[-1]
                z, fz = D(0.5).copy_sign(-d * a), D(1).copy_sign(d)
                while d * fz > 0:
                    z *= 2
                    fz = self(z)
                    if near(fz, 0, prec):
                        q = self.ruffini(z).roots()
                        q[0].append(z)
                        return q
                lower, higher = (z, zero) if d * a > 0 else (zero, z)
                flower, fire = self(lower), self(higher)
                N, bprec, nprec = 0, D(prec).sqrt(), D(prec * prec)
                # Bisect until half the desired precision...
                while not near(lower, higher, bprec) and N < 64:
                    mid = (lower + higher) / 2
                    fmid = self(mid)
                    if abs(fmid) == zero: break
                    if fmid * flower > 0: lower, flower = mid, fmid
                    else: higher, fire = mid, fmid
                    N += 1
                N = 0
                # ...then proceed with Newton's method to twice the precision
                val, step, dp = mid, 1, self.deriv()
                try:
                    while not near(step, 0, nprec) and N < 64:
                        step = self(val) / dp(val)
                        val -= step
                        N += 1
                except ZeroDivisionError:
                    pass
                q = self.ruffini(val).roots()
                q[0].append(val)
                return q
        else:
            # TODO
            return "???"

def bairstowconstants(p, u, v):
    """Calculates the constants c, d, g and h for Bairstow's method from u and v with respect to a polynomial p.
    divmod(p, polynomial(v, u, 1)) = (q, polynomial(d, c));
    divmod(q, polynomial(v, u, 1)) = (r, polynomial(h, g))."""
    pass # TODO

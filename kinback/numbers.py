#!/usr/bin/env python3.4
# Helper functions for Kinross: numeric functions and classical algebra
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
# Exact decimal arithmetic is used in the polynomial class to mitigate floating-point follies.
import decimal
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
    """A polynomial stores a list of decimal coefficients [a0, a1, a2, ...] where a0 is the constant term, a1 is the x term and so on.
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
    def dup(self):
        """Returns an independent duplicate of the polynomial."""
        return polynomial(self.a)
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
        q, r, d, c = polynomial(), self.dup(), b.deg(), b[-1]
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
    def quadruffini(self, u, v):
        """Divides the polynomial by x^2 + ux + v with a Ruffini-like scheme, returning a tuple (quotient, c, d) where the remainder is cx + d."""
        q = [zero, zero]
        for i in range(self.deg(), 1, -1): q.append(self[i] - u * q[-1] - v * q[-2])
        return (polynomial(q[:1:-1]), self[1] - u * q[-1] - v * q[-2], self[0] - v * q[-1])
    def deriv(self): return polynomial([i * self[i] for i in range(1, len(self))])
    def antideriv(self): return polynomial([0.] + [self[i] / (i + 1) for i in range(len(self))])
    def minusendzeros(self, prec = 1e-10):
        """Returns the polynomial with leading and trailing zeros to the specified precision stripped along with the number of trailing zeros (or equivalently zero roots)."""
        p = self.dup()
        while near(p[-1], 0, prec): p.a.pop()
        N = 0
        while near(p[0], 0, prec):
            p.a.pop(0)
            N += 1
        return (p, N)
        
    def roots(self, prec = 1e-10):
        """Finds all roots of the polynomial to the specified precision, returning the [[real roots] and [complex roots as [real part, complex part]]].
        The quadratic evaluation is numerically stable; see https://people.csail.mit.edu/bkph/articles/Quadratics.pdf for the derivation.
        Higher polynomials are handled by bisecting/Newton's method on odd degrees and Bairstow's method on even degrees.
        In practice this method would be used as part of the coercing function polynomroot()."""
        p, nz = self.minusendzeros(prec)
        if p.deg() == 0: res = [[], []]
        elif p.deg() == 1: res = [[-p[0] / p[1]], []]
        elif p.deg() == 2:
            a, b, c = p[2], p[1], p[0]
            d = b * b - 4 * a * c
            e = abs(d).sqrt()
            if d < 0:
                r, i = -b / (2 * a), e / (2 * a)
                res = [[], [[r, -i], [r, i]]]
            else:
                if b < 0: res = [[(2 * c) / (-b + e), (-b + e) / (2 * a)], []]
                else: res = [[(-b - e) / (2 * a), (2 * c) / (-b - e)], []]
        elif p.deg() % 2: # Odd-degree polynomials always have at least one real root by the intermediate value theorem
            d, a = p[0], p[-1]
            z, fz = D(0.5).copy_sign(-d * a), D(1).copy_sign(d)
            while d * fz >= 0:
                z *= 2
                fz = p(z)
            lower, higher = (z, zero) if d * a > 0 else (zero, z)
            flower, fire = p(lower), p(higher)
            N, bprec, nprec = 0, D(prec).sqrt(), D(prec * prec)
            # Bisect until half the desired precision
            while not near(lower, higher, bprec) and N < 64:
                mid = (lower + higher) / 2
                fmid = p(mid)
                if abs(fmid) == zero: break
                if fmid * flower > 0: lower, flower = mid, fmid
                else: higher, fire = mid, fmid
                N += 1
            N = 0
            # Then proceed with Newton's method to twice the precision
            val, step, dp = mid, 1, p.deriv()
            try:
                while not near(step, 0, prec * prec) and N < 64:
                    step = p(val) / dp(val)
                    val -= step
                    N += 1
            except decimal.InvalidOperation: pass # val has encountered a stationary root
            res = p.ruffini(val).roots()
            res[0].append(val)
        else:
            res = [[], []]
            while p.deg() > 2:
                u, v = self[-2] / self[-1], self[-3] / self[-1]
                x, y, N, bairprec = D(3), D(4), 0, D(prec * prec * prec)
                while not near((x * x + y * y).sqrt(), 0, bairprec) and N < 24:
                    x, y = bairstowstep(p, u, v)
                    u, v = u + x, v + y
                    N += 1
                p = p.quadruffini(u, v)[0]
                load = polynomial((v, u, 1)).roots()
                res[0].extend(load[0])
                res[1].extend(load[1])
            last = p.roots()
            res[0].extend(last[0])
            res[1].extend(last[1])
        # At the end the previously found number of "trivial" zeros are appended to res.
        res[0].extend([zero for i in range(nz)])
        return res

def bairstowstep(p, u, v):
    """Calculates one step of Bairstow's method for the given polynomial and constants (divisor is x^2 + ux + v); this is to be added to the current guess rather than subtracted."""
    q, c, d = p.quadruffini(u, v)
    g, h = q.quadruffini(u, v)[1:]
    K, L = -g * v, g.fma(u, -h)
    frac = g * K + h * L
    x, y = (d * g - c * h) / frac, (c * K + d * L) / frac
    return (x, y)

def polynomroot(coeffs, precdigits = 10):
    """Finds all the roots of the polynomial determined by coeffs to the given number of decimal places, coercing to floats.
    The first element of coeffs is the constant term as in the polynomial class;
    the returned list is also identical but complex numbers are reconstituted."""
    prec = D("1e-{}".format(precdigits))
    raw = polynomial(coeffs).roots(prec)
    out = [[], []]
    for rn in raw[0]: out[0].append(float(round(rn, precdigits)))
    for cn in raw[1]: out[1].append(complex(round(cn[0], precdigits), round(cn[1], precdigits)))
    return out

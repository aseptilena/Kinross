# Helper functions for Kinross: numerical algebra and methods
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sqrt, hypot
from cmath import isclose
from itertools import product
from decimal import Decimal as D, getcontext
import time
getcontext().prec = 60
zero = D(0)

class polyn:
    """A polyn(omial) stores a list of (real) coefficients [a0, a1, a2, ...] where a0 is the constant term, a1 is the x term and so on."""
    def __init__(self, *coeffs): self.a = list(coeffs)
    def __getitem__(self, n): return self.a[n] # The coefficient associated with the nth power; leading coefficient is self[-1]
    def __setitem__(self, n, v): self.a[n] = v
    def __len__(self): return len(self.a)
    def deg(self): return len(self) - 1
    def powers(self): return range(len(self) - 1, -1, -1) # High-to-low iterator over the polynomial's powers
    def __str__(self): return " + ".join(["{}*x^{}".format(self[i], i) for i in self.powers()])
    def __repr__(self): return "polyn(" + ", ".join([str(c) for c in self.a]) + ")"
    def __call__(self, x): # Horner scheme
        res = 0
        for i in self.powers(): res = res * x + self[i]
        return res
    def dup(self):
        """Returns an independent duplicate of the polynomial."""
        return polyn(self.a)
    
    def __add__(self, q):
        res = self.a + [0] * max(0, len(q) - len(self))
        for i in range(len(q)): res[i] += q[i]
        return polyn(*res)
    def __sub__(self, q):
        res = self.a + [0] * max(0, len(q) - len(self))
        for i in range(len(q)): res[i] -= q[i]
        return polyn(*res)
    def __neg__(self): return polyn(*[-c for c in self.a])
    def __mul__(self, q):
        if type(q) != polyn: return polyn(*[c * q for c in self.a])
        res = [0] * (len(self) + len(q) - 1)
        for p in product(range(len(self)), range(len(q))): res[sum(p)] += self[p[0]] * q[p[1]]
        return polyn(*res)
    def __rmul__(self, q): return self * q
    def __divmod__(self, b):
        if type(b) != polyn: return (polyn(*[c / b for c in self.a]), polyn(0))
        r, d, q = self.a[:], b.a, [] # d is the divisor
        while len(r) >= len(d):
            q.append(r[-1] / d[-1])
            for i in range(-1, -len(d) - 1, -1): r[i] -= q[-1] * d[i]
            r.pop()
        return (polyn(*q[::-1]), polyn(*r))
    def __floordiv__(self, b): return divmod(self, b)[0]
    def __truediv__(self, b): return self // b
    def __mod__(self, b): return divmod(self, b)[1]
    def deriv(self): return polyn(*[i * self[i] for i in range(1, len(self))])
    def antideriv(self): return polyn(*([0] + [self[i] / (i + 1) for i in range(len(self))]))
    
    def quadruffini(self, u, v):
        """Divides the polynomial by x^2 + ux + v with a Ruffini-like scheme, returning (quotient, c, d) where the remainder is cx + d."""
        q = [0, 0]
        for i in range(self.deg(), 1, -1): q.append(self[i] - u * q[-1] - v * q[-2])
        return (polyn(*q[:1:-1]), self[1] - u * q[-1] - v * q[-2], self[0] - v * q[-1])
    def bairstowstep(self, u, v):
        """Calculates one step of Bairstow's method for the given constants (divisor is x^2 + ux + v) to be added to the current guess."""
        q, c, d = self.quadruffini(u, v)
        g, h = q.quadruffini(u, v)[1:]
        K, L = -g * v, g * u - h
        frac = g * K + h * L
        return ((d * g - c * h) / frac, (c * K + d * L) / frac)
    def roots(self):
        """Finds all ([real], [complex]) roots of the polynomial; cubic and higher degrees are handled by Bairstow's method."""
        cfs, out = self.a[:], ([], [])
        while isclose(cfs[-1], 0, abs_tol=1e-15) and len(cfs) > 1: cfs.pop() # scrub high and low zeros to make things easier
        while isclose(cfs[0], 0, abs_tol=1e-15) and len(cfs) > 1:
            cfs.pop(0)
            out[0].append(0)
        p = polyn(*cfs)
        if p.deg() == 0: pass
        elif p.deg() == 1: out[0].append(-p[0] / p[1])
        elif p.deg() == 2: # derivation from https://people.csail.mit.edu/bkph/articles/Quadratics.pdf
            a, b, c = p[2], p[1], p[0]
            d = b * b - 4 * a * c
            e = sqrt(abs(d))
            if d < 0:
                r, i = -b / a / 2, e / a / 2
                out[1].extend([complex(r, -i), complex(r, i)])
            else:
                if b < 0: out[0].extend([c / (-b + e) * 2, (-b + e) / a / 2])
                else: out[0].extend([-(b + e) / a / 2, -c / (b + e) * 2])
        else:
            odd = p.deg() % 2 # Bairstow's method is ill-behaved on odd-degree polynomials
            if odd: p *= polyn(-1, 1) # ∴ salt with x - 1 and catch later
            while p.deg() > 2:
                u, v, x, y = p[-2] / p[-1], p[-3] / p[-1], None, None
                while x == None and y == None:
                    try: x, y = p.bairstowstep(u, v)
                    except ZeroDivisionError: u, v = u + 0.1, v + 0.1
                for q in range(256):
                    if not isclose(hypot(x, y), 0, abs_tol=1e-15):
                        x, y = p.bairstowstep(u, v)
                        u, v = u + x, v + y
                    else: break
                p = p.quadruffini(u, v)[0]
                new = polyn(v, u, 1).roots()
                out[0].extend(new[0])
                out[1].extend(new[1])
            last = p.roots()
            out[0].extend(last[0])
            out[1].extend(last[1])
            if odd:
                for i in range(len(out[0])):
                    if isclose(out[0][i], 1, abs_tol=1e-15):
                        out[0].pop(i)
                        break
        return out

def polynomroot(coeffs, precdigits = 15):
    """Finds all the roots of polynomial(coeffs) to [precdigits] decimal places.
    This function not only saves the need for creating a new instance, it also coerces to floats/complexes and suppresses small complex components."""
    prec = D("1e-" + str(precdigits))
    raw = polynomial(coeffs).roots(prec)
    out = [[], []]
    for rn in raw[0]: out[0].append(float(round(rn, precdigits)))
    for cn in raw[1]:
        if isclose(cn[1], zero, abs_tol=prec): out[0].append(float(round(cn[0], precdigits)))
        else: out[1].append(complex(round(cn[0], precdigits), round(cn[1], precdigits)))
    return out

def matdeterm(m, exact = False):
    """Bareiss's determinant algorithm as given in http://cs.nyu.edu/~yap/book/alge/ftpSite/l10.ps.gz (section 2).
    This gives exact results for integer matrices when exact is True."""
    import operator
    divf = operator.floordiv if exact else operator.truediv
    a, N = [list(r[:]) for r in m], len(m)
    # Elementary row operations do not change the determinant
    counter = 0
    while counter < N:
        if not isclose(a[counter][counter], 0):
            counter += 1
            continue
        nadded = True
        for z in range(N):
            if not isclose(a[z][counter], 0) and z != counter:
                a[counter] = [sum(pair) for pair in zip(a[counter], a[z])]
                nadded = False
                break
        if nadded: return 0 # The determinant of a matrix with a row or column of zeros is 0
        counter += 1
    for k in range(1, N):
        kk = k - 1
        for i in range(k, N):
            for j in range(k, N): a[i][j] = divf(a[i][j] * a[kk][kk] - a[i][kk] * a[kk][j], 1 if not kk else a[k - 2][k - 2])
    return a[-1][-1]

def rombergquad(f, a, b, e = 1e-18):
    """∫(a, b) f(x) dx by Romberg's method."""
    fa, fm, fb, h = f(a), f((a + b) / 2), f(b), (b - a) / 2
    one = (fa + 2 * fm + fb) * h / 2
    two = (4 * one - (fa + fb) * h) / 3
    v = [one, two]
    while abs(v[-1] - v[-2]) > e:
        h /= 2
        v.insert(0, v[0] / 2 + h * sum([f(a + i * h) for i in range(1, 1 << len(v), 2)]))
        for i in range(1, len(v)): v[i] = v[i - 1] + (v[i - 1] - v[i]) / (4 ** i - 1)
    return v[-1]

# Helper functions for Kinross: numerical algebra and methods
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sqrt, isclose, copysign
from cmath import sqrt as csqrt
from itertools import product

class polyn:
    """A polyn stores a list of (real) coefficients [a0, a1, a2, ...] where a0 is the constant term, a1 is the x term and so on."""
    def __init__(self, *coeffs): self.a = list(coeffs)
    def __getitem__(self, n): return self.a[n]
    def __setitem__(self, n, v): self.a[n] = v
    def __len__(self): return len(self.a)
    def deg(self): return len(self) - 1
    def powers(self): return range(len(self) - 1, -1, -1) # High-to-low iterator over the polynomial's powers
    def __str__(self): return " + ".join(["{}*x^{}".format(self[i], i) for i in self.powers()])
    def __repr__(self): return "polyn(" + ", ".join([str(c) for c in self.a]) + ")"
    def ruffini(self, r):
        """Divides the polynomial by x - r with Ruffini's rule, returning (quotient, remainder/p(r)). If r is a root, this amounts to deflation."""
        res = [0]
        for i in self.powers(): res.append(res[-1] * r + self[i])
        return (polyn(*res[-2:0:-1]), res[-1])
    def __call__(self, x): return self.ruffini(x)[1]
    
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
        r, d, q = self.a[:], b.a, []
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
    def norm(self): return self / self[-1]
    
    def quadruffini(self, u, v):
        """Divides the polynomial by x^2 + ux + v with a Ruffini-like scheme, returning (quotient, c, d) where the remainder is cx + d."""
        q = [0, 0]
        for i in range(self.deg(), 1, -1): q.append(self[i] - u * q[-1] - v * q[-2])
        return (polyn(*q[:1:-1]), self[1] - u * q[-1] - v * q[-2], self[0] - v * q[-1])
    def laguerrestep(self, x):
        """Calculates one step of Laguerre's method for the given iterate."""
        r = self(x)
        if abs(r) < 1e-15: return 0
        dp = self.deriv()
        s, t, n = dp(x), dp.deriv()(x), self.deg()
        u = s / r
        v = u * u - t / r
        rooty = csqrt((n - 1) * (n * v - u * u))
        d0, d1 = u + rooty, u - rooty
        return n / d0 if abs(d0) >= abs(d1) else n / d1
    def roots(self):
        """Finds all ([real], [complex]) roots of the polynomial."""
        cfs, out = self.a[:], ([], [])
        while abs(cfs[-1]) <= 1e-15 and len(cfs) > 1: cfs.pop() # scrub high and low zeros to make things easier
        while abs(cfs[0]) <= 1e-15 and len(cfs) > 1:
            cfs.pop(0)
            out[0].append(0)
        p = polyn(*cfs)
        if p.deg() == 0: pass
        elif p.deg() == 1: out[0].append(-p[0] / p[1])
        elif p.deg() == 2: # Derivation from https://people.csail.mit.edu/bkph/articles/Quadratics.pdf
            a, b, c = p[2], p[1], p[0]
            d = b * b - 4 * a * c
            e = sqrt(abs(d))
            if d < 0:
                r, i = -b / (2 * a), e / (2 * a)
                out[1].extend([complex(r, -i), complex(r, i)])
            else: out[0].extend([2 * c / (-b + e), (-b + e) / (2 * a)] if b < 0 else [-(b + e) / (2 * a), -2 * c / (b + e)])
        elif p.deg() == 3: # Halley-based numerical method for solving a cubic from http://derpy.me/samuelsoncubic
            d, c, b = [v / p[3] for v in p[:3]]
            fl = -b / 3
            fv = p(fl)
            if abs(fv) <= 1e-15:
                j = fl + b
                k = j * fl + c
                last = polyn(k, j, 1).roots()
                last[0].append(fl)
                out[0].extend(last[0])
                out[1].extend(last[1])
            else:
                Z = b * b - 3 * c
                if abs(Z) <= 1e-15: out[0].extend([fl - fv ** (1 / 3)] * 3)
                else:
                    iterate = fl if Z < 0 else fl - copysign(sqrt(Z) * 2 / 3, fv)
                    num = polyn(c * d, c * c + 2 * b * d, 3 * (b * c + d), 2 * (2 * c + b * b), 5 * b, 3)
                    denom = polyn(c * c - b * d, 3 * (b * c - d), 3 * (b * b + c), 8 * b, 6)
                    delta = 1
                    for q in range(16):
                        if abs(delta) > 1e-15:
                            delta = num(iterate) / denom(iterate)
                            iterate -= delta
                        else: break
                    j = iterate + b
                    k = j * iterate + c
                    last = polyn(k, j, 1).roots()
                    last[0].append(iterate)
                    out[0].extend(last[0])
                    out[1].extend(last[1])
        else: # Laguerre's method
            p = p.norm()
            while p.deg() > 2:
                iterate, delta = 0, 1
                for q in range(64):
                    if abs(delta) > 1e-15:
                        delta = p.laguerrestep(iterate)
                        iterate -= delta
                    else: break
                if abs(iterate.imag) < 1e-14:
                    out[0].append(iterate.real)
                    p = p.ruffini(iterate.real)[0]
                else:
                    out[1].extend([iterate, iterate.conjugate()])
                    p = p.quadruffini(-2 * iterate.real, iterate.real * iterate.real + iterate.imag + iterate.imag)[0]
            last = p.roots()
            out[0].extend(last[0])
            out[1].extend(last[1])
        for i in range(len(out[1]) - 1, 0, -2):
            if abs(out[1][i].imag) <= 1e-14:
                out[0].extend([out[1][i].real] * 2)
                del out[1][i:i + 2]
        return out
    def rroots(self):
        """Like roots() but only returns the real ones, sorted ascending."""
        return sorted(self.roots()[0])

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

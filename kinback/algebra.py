# Helper functions for Kinross: numerical algebra and methods
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import sqrt, copysign
from cmath import sqrt as csqrt
from numbers import Number
from itertools import product, zip_longest

def ruff(p, r): # p / [-r, 1], returns (p(r), quotient)
    res = [p[-1]]
    for a in p[-2::-1]: res.append(res[-1] * r + a)
    return (res[-1], res[-2::-1])
def deriv(p): return [p[i] * i for i in range(1, len(p))] # derivative
def qruff(p, v, u): # p / [v, u, 1], ignoring remainder
    res = [0, 0]
    for i in range(len(p) - 1, 1, -1): res.append(p[i] - (u * q[-1] + v * q[-2]))
    return res[:1:-1]

# Separate functions for solving quadratic and cubic polynomials.
# The returned roots are in a dictionary {0: [real roots], 1: [complex roots]}.
def qdroot(c, b, a): # from https://people.csail.mit.edu/bkph/articles/Quadratics.pdf
    d = b * b - 4 * a * c
    e = sqrt(abs(d))
    if d < 0:
        z = complex(-b, e) / (2 * a)
        return {0: [], 1: [z.conjugate(), z]}
    else:
        be = -b + e if b < 0 else -(b + e)
        return {0: [2 * c / be, be / a / 2], 1: []}

def cbroot(ad, ac, ab, a):
    b, c, d = ab / a, ac / a, ad / a
    fl = -b / 3
    fv, qp = ruff((d, c, b, 1), fl)
    if abs(fv) <= 1e-15:
        res = qdroot(*qp)
        res[0] += [fl]
        return res
    Z = b * b - 3 * c
    if abs(Z) <= 1e-15:
        r = fl - fv ** (1 / 3)
        return {0: [r, r, r], 1: []}
    iterate = fl if Z < 0 else fl - copysign(sqrt(Z) * 2 / 3, fv)
    num = (c * d, c * c + 2 * b * d, 3 * (b * c + d), 2 * (2 * c + b * b), 5 * b, 3)
    denom = (c * c - b * d, 3 * (b * c - d), 3 * (b * b + c), 8 * b, 6)
    delta = 1
    for q in range(16):
        if abs(delta) > 1e-15:
            delta = ruff(num, iterate)[0] / ruff(denom, iterate)[0]
            iterate -= delta
        else: break
    j = iterate + b
    res = qdroot(j * iterate + c, j, 1)
    res[0] += [iterate]
    return res

def polroots(pp):
    p = pp[:]
    res = {0: [], 1: []}
    try:
        while abs(p[-1]) < 1e-15: p.pop()
    except IndexError: return res # zero polynomial
    while abs(p[0]) < 1e-15:
        p.pop(0)
        res[0] += [0]
    if len(p) == 1: return res
    if len(p) == 2:
        res[0] += [-p[0] / p[1]]
        return res
    while len(p) > 4: # use Laguerre's method
        n, x, delta = len(p) - 1, 0, 1
        f = lambda z: ruff(p, z)[0]
        p_ = deriv(p)
        df = lambda z: ruff(p_, z)[0]
        p__ = deriv(p_)
        d2f = lambda z: ruff(p__, z)[0]
        for q in range(64):
            at = f(x)
            if abs(delta) < 1e-15 or abs(at) < 1e-15: break
            G = df(x) / at
            H = G * G - d2f(x) / at
            surd = csqrt((n - 1) * (n * H - G * G))
            d0, d1 = G + surd, G - surd
            delta = n / d0 if abs(d0) >= abs(d1) else n / d1
            x -= delta
        if abs(x.imag) < 1e-14:
            res[0] += [x.real]
            p = ruff(p, x.real)[1]
        else:
            res[1] += [x, x.conjugate()]
            p = qruff(x.real * x.real + x.imag * x.imag, -2 * x.real)
    if len(p) == 3: last = qdroot(*p)
    if len(p) == 4: last = cbroot(*p)
    res[0] += last[0]
    res[1] += last[1]
    return res

class polyn:
    def __init__(self, coeffs): self.a = list(coeffs)
    def __getitem__(self, n): return self.a[n]
    def __setitem__(self, n, v): self.a[n] = v
    def __len__(self): return len(self.a)
    def __call__(self, x): return ruff(self, x)[0]
    
    def __add__(self, q): return polyn(a + b for a, b in zip_longest(self, q, fillvalue=0))
    def __sub__(self, q): return polyn(a - b for a, b in zip_longest(self, q, fillvalue=0))
    def __mul__(self, q):
        if isinstance(q, Number): return polyn(c * q for c in self.a)
        res = [0] * (len(self) + len(q) - 1)
        for p in product(range(len(self)), range(len(q))): res[sum(p)] += self[p[0]] * q[p[1]]
        return polyn(res)
    def __rmul__(self, q): return self * q
    def d(self): return polyn(deriv(self))
    
    def roots(self): return polroots(self)
    def rroots(self): return sorted(self.roots()[0])

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

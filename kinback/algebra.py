# Helper functions for Kinross: numerical algebra and methods
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import sqrt, copysign
from cmath import phase, rect, sqrt as csqrt, isclose
from itertools import zip_longest

def linterp(p, q, t): return (1 - t) * p + t * q

def cross(a, b, o = 0j): return (a.real - o.real) * (b.imag - o.imag) - (a.imag - o.imag) * (b.real - o.real)
def collinear(a, b, c): return isclose(cross(a, b, c), 0)

def pointbounds(pts): # orthogonal bounding box of an array of points, represented as a tuple of opposing corners
    xs, ys = [p.real for p in pts], [p.imag for p in pts]
    return complex(min(xs), min(ys)), complex(max(xs), max(ys))

# Polynomial classes and functions, including root extraction; the Pol and polroots names come from PARI/GP.
# Roots returned are in a dictionary {0: [real roots], 1: [complex roots]}.
def quadraticroots(c, b, a): # from https://people.csail.mit.edu/bkph/articles/Quadratics.pdf
    d = b * b - 4 * a * c
    e = sqrt(abs(d))
    if d < 0:
        z = complex(-b, e) / (2 * a)
        return {0: [], 1: [z.conjugate(), z]}
    else:
        be = -b + e if b < 0 else -(b + e)
        return {0: [2 * c / be, be / a / 2], 1: []}

def cubicroots(ad, ac, ab, a):
    b, c, d = ab / a, ac / a, ad / a
    fl = -b / 3
    fv, qp = Pol([d, c, b, 1]).ruff(fl)
    if abs(fv) <= 1e-15:
        res = quadraticroots(*qp)
        res[0] += [fl]
        return res
    Z = b * b - 3 * c
    if abs(Z) <= 1e-15:
        r = fl - fv ** (1 / 3)
        return {0: [r, r, r], 1: []}
    iterate = fl if Z < 0 else fl - copysign(sqrt(Z) * 2 / 3, fv)
    num = Pol([c * d, c * c + 2 * b * d, 3 * (b * c + d), 2 * (2 * c + b * b), 5 * b, 3])
    denom = Pol([c * c - b * d, 3 * (b * c - d), 3 * (b * b + c), 8 * b, 6])
    delta = 1
    for q in range(16):
        if abs(delta) > 1e-15:
            delta = num(iterate) / denom(iterate)
            iterate -= delta
        else: break
    j = iterate + b
    res = quadraticroots(j * iterate + c, j, 1)
    res[0] += [iterate]
    return res

def polroots(p_in):
    p = p_in[:]
    res = {0: [], 1: []}
    try:
        while abs(p[-1]) < 1e-15: p.pop()
    except IndexError: return res # zero polynomial
    while abs(p[0]) < 1e-15:
        p.pop(0)
        res[0] += [0]
    p = Pol(p)
    if len(p) == 1: return res
    if len(p) == 2:
        res[0] += [-p[0] / p[1]]
        return res
    while len(p) > 4: # use Laguerre's method
        n, x, delta = len(p) - 1, 0, 1
        p1 = p_in.d()
        p2 = p1.d()
        for q in range(64):
            at = p(x)
            if abs(delta) < 1e-15 or abs(at) < 1e-15: break
            g = p1(x) / at
            h = g * g - p2(x) / at
            surd = csqrt((n - 1) * (n * h - g * g))
            d0, d1 = g + surd, g - surd
            delta = n / d0 if abs(d0) >= abs(d1) else n / d1
            x -= delta
        if abs(x.imag) < 1e-14:
            res[0] += [x.real]
            p = p.ruff(x.real)[1]
        else:
            res[1] += [x, x.conjugate()]
            p = p.qruff(x.real * x.real + x.imag * x.imag, -2 * x.real)
    if len(p) == 3: last = quadraticroots(*p)
    if len(p) == 4: last = cubicroots(*p)
    res[0] += last[0]
    res[1] += last[1]
    return res

class Pol:
    def __init__(self, cfs): self.a = list(cfs)
    def __getitem__(self, n): return self.a[n]
    def __len__(self): return len(self.a)
    def ruff(self, r): # p / [-r, 1], returns (p(r), quotient)
        res = [self[-1]]
        for m in self[-2::-1]: res.append(res[-1] * r + m)
        return res[-1], Pol(res[-2::-1])
    def __call__(self, x): return self.ruff(x)[0]
    def __add__(self, q): return Pol(a + b for a, b in zip_longest(self, q, fillvalue=0))
    def __sub__(self, q): return Pol(a - b for a, b in zip_longest(self, q, fillvalue=0))
    def __mul__(self, q):
        res = [0] * (len(self) + len(q) - 1)
        for i, a in enumerate(self):
            for j, b in enumerate(q): res[i + j] += a * b
        return Pol(res)
    def d(self): return Pol((self[i] * i for i in range(1, len(self))))
    def qruff(self, v, u): # p / [v, u, 1], ignoring remainder
        res = [0, 0]
        for i in range(len(self) - 1, 1, -1): res.append(self[i] - (u * res[-1] + v * res[-2]))
        return Pol(res[:1:-1])
    def roots(self): return polroots(self)
    def reals(self): return sorted(polroots(self)[0])

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

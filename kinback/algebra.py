# Helper functions for Kinross: numerical algebra with a decimal floating-point basis
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from decimal import Decimal as D, getcontext, localcontext
getcontext().prec = 60
zero, one = D(0), D(1)
from .vectors import near

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
        """Divides the polynomial by x - r using the Ruffini scheme, returning the remainder in a tuple."""
        res = []
        for i in self.powers():
            if i == self.deg(): res.append(self[i])
            else: res.insert(0, res[0].fma(r, self[i]))
        return (polynomial(res[1:]), res[0])
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
        while near(p[-1], zero, prec): p.a.pop()
        N = 0
        while near(p[0], zero, prec):
            p.a.pop(0)
            N += 1
        return (p, N)
    def bairstowstep(self, u, v):
        """Calculates one step of Bairstow's method for the given constants (divisor is x^2 + ux + v) to be added to the current guess."""
        q, c, d = self.quadruffini(u, v)
        g, h = q.quadruffini(u, v)[1:]
        K, L = -g * v, g.fma(u, -h)
        frac = g * K + h * L
        x, y = (d * g - c * h) / frac, (c * K + d * L) / frac
        return (x, y)
    def roots(self, prec = 1e-10):
        """Finds all roots to the specified precision, returning the [[real roots] and [complex roots as [real part, complex part]]].
        Cubic and higher polynomials are handled by Bairstow's method; in practice this function would be used as part of polynomroot()."""
        p, nz = self.minusendzeros(prec)
        if p.deg() == 0: res = [[], []]
        elif p.deg() == 1: res = [[-p[0] / p[1]], []]
        elif p.deg() == 2:
            # See https://people.csail.mit.edu/bkph/articles/Quadratics.pdf for the derivation.
            a, b, c = p[2], p[1], p[0]
            d = b * b - 4 * a * c
            e = abs(d).sqrt()
            if d < 0:
                r, i = -b / (2 * a), e / (2 * a)
                res = [[], [[r, -i], [r, i]]]
            else:
                if b < 0: res = [[(2 * c) / (-b + e), (-b + e) / (2 * a)], []]
                else: res = [[(-b - e) / (2 * a), (2 * c) / (-b - e)], []]
        else:
            odd = p.deg() % 2
             # Bairstow's method is ill-behaved on odd-degree polynomials; "salt" with a factor of x - 1 and catch later
            if odd: p *= polynomial((-1, 1))
            res = [[], []]
            while p.deg() > 2:
                u, v = self[-2] / self[-1], self[-3] / self[-1]
                x, y, N, bairprec = D(3), D(4), 0, D(prec * prec * prec)
                while not near((x * x + y * y).sqrt(), zero, bairprec) and N < 256:
                    x, y = p.bairstowstep(u, v)
                    u, v = u + x, v + y
                    N += 1
                p = p.quadruffini(u, v)[0]
                load = polynomial((v, u, 1)).roots()
                res[0].extend(load[0])
                res[1].extend(load[1])
            last = p.roots()
            res[0].extend(last[0])
            res[1].extend(last[1])
            if odd:
                notr = True
                for r in res[0]:
                    if near(r, one, prec):
                        res[0].remove(r)
                        notr = False
                        break
                if notr:
                    for c in res[1]:
                        if near(c[0], one, prec):
                            res[1].remove(c)
                            break
        # At the end the previously found number of "trivial" zeros are appended to res.
        res[0].extend([zero for i in range(nz)])
        return res

def polynomroot(coeffs, precdigits = 20):
    """Finds all the roots of polynomial(coeffs) to [precdigits] decimal places.
    This function not only saves the need for creating a new instance, it also coerces to floats/complexes and suppresses small complex components."""
    prec = D("1e-{}".format(precdigits))
    raw = polynomial(coeffs).roots(prec)
    out = [[], []]
    for rn in raw[0]: out[0].append(float(round(rn, precdigits)))
    for cn in raw[1]:
        if near(cn[1], zero, prec): out[0].append(float(round(cn[0], precdigits)))
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
        if not near(a[counter][counter], 0, 1e-9):
            counter += 1
            continue
        nadded = True
        for z in range(N):
            if not near(a[z][counter], 0, 1e-9) and z != counter:
                a[counter] = [sum(pair) for pair in zip(a[counter], a[z])]
                nadded = False
                break
        if nadded: return 0 # The determinant of a matrix with a row or column of 0's is 0
        counter += 1
    for k in range(1, N):
        kk = k - 1
        for i in range(k, N):
            for j in range(k, N): a[i][j] = divf(a[i][j] * a[kk][kk] - a[i][kk] * a[kk][j], 1 if not kk else a[k - 2][k - 2])
    return a[-1][-1]

def cosandsin(t):
    """Computes the (cosine, sine of t) at the same time."""
    with localcontext() as scc:
        scc.prec = 80
        cres, sres, x, cstep, sstep, err = D(1), D(t), D(t), D(1), D(1), D("1e-70")
        px, i = x * x / 2, 2
        while (max(abs(cstep), abs(sstep))) > err:
            cstep, sstep = D(0), D(0)
            cstep -= px           # Twelve straight assignments,
            px = px * x / (i + 1) # eleven in the darkness,
            i += 1                # ten-base computing,
            sstep -= px           # nine-point* typefacing,
            px = px * x / (i + 1) # eight background changes,
            i += 1                # seven stellar sisters**,
            cstep += px           # six friendly ponies,
            px = px * x / (i + 1) # five boron stars!
            i += 1                # Four different kinds,
            sstep += px           # three simple steps,
            px = px * x / (i + 1) # two trig functions
            i += 1                # and Princess Parcly in a yew tree.
            # * gedit by default uses the system's monospace font at 9 pt.
            # ** Pleiades.
            cres, sres = cres + cstep, sres + sstep
    return (+cres, +sres)

def adaptivesimpson(f, a, b, e = 1e-12):
    """Computes the definite integral of f from a to b by an adaptive Simpson's rule, where e is an error parameter.
    The naive implementation would be recursive, which is frowned upon, so instead this uses a list of 2-tuples storing function evaluations."""
    c, res = (D(a) + D(b)) / 2, D(0)
    v = [(D(a), f(D(a))), (c, f(c)), (D(b), f(D(b)))]
    while len(v) > 2:
        # Evaluate Simpson's rule on the first three points...
        ab = (v[2][0] - v[0][0]) * (v[0][1] + 4 * v[1][1] + v[2][1]) / 6
        # ...then insert the "second midpoints"
        acm, cbm = (v[0][0] + v[1][0]) / 2, (v[1][0] + v[2][0]) / 2
        v.insert(2, (cbm, f(cbm)))
        v.insert(1, (acm, f(acm)))
        ac = (v[2][0] - v[0][0]) * (v[0][1] + 4 * v[1][1] + v[2][1]) / 6
        cb = (v[4][0] - v[2][0]) * (v[2][1] + 4 * v[3][1] + v[4][1]) / 6
        corr = (ac + cb - ab) / 15
        if abs(corr) < e:
            del v[:4]
            res += ac + cb + corr
    return res
# Helper functions for Kinross: random point and structure generation (and a nod to MLPFIM's Discord)
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
import random
from math import sqrt, log, ceil, exp
from cmath import rect
from .vectors import linterp

# SystemRandom is good enough for simulation and pretty pictures, but here I add a few more useful functions, especially discrete distributions.
# Page numbers below refer to Luc Devroye's book on Non-Uniform Random Variate Generation (http://luc.devroye.org/rnbookindex.html).
class KinrossRandom(random.SystemRandom):
    def geometricvariate(self, p = 0):
        """Geometric distribution with probability of success p. Here we use the number of trials before first failure;
        this is equivalent to flooring the exponential distribution with parameter -ln(1 - p). p defaults to 0.5."""
        return int(self.expovariate(log(2) if not 0 < p < 1 else -log(1 - p)))
    def binomialvariate(self, num = 0, prob = 2):
        """Binomial distribution with the specified number of trials and probability of success; parameters default to 16 and 0.5."""
        n, p = ceil(abs(num)) if num else 16, prob if 0 < prob < 1 else 0.5
        if p == 0.5: return bin(self.getrandbits(n)).count('1')
        res = 0 # TAOCP recursive method
        while n > 10:
            left, right = (n >> 1) + 1, n + 1 >> 1
            if n & 1: # left = right, beta variate shortcut on p. 437
                z = 2
                while z > 1:
                    u, v = self.random(), 2 * self.random() - 1
                    z = u * u + v * v
                bv = u * v * sqrt(1 - z ** (2 / (2 * left - 1))) / z + 0.5
            else: # left = right + 1, Cheng's 1978 algorithm BB
                n1, huard = n + 1, sqrt((2 * n - 2) / (n * n - 2))
                rc = right + 1 / huard
                while True:
                    u1, u2 = self.random(), self.random()
                    ld = huard * log(u1 / (1 - u1))
                    w = right * exp(ld)
                    cb = u1 * u1 * u2
                    rr = rc * ld - 1.3862944
                    sm = right + rr - w
                    if sm + 2.609438 >= 5 * cb: break
                    lcb = log(cb)
                    if sm > lcb or rr + n1 * log(n1 / (left + w)) >= lcb: break
                bv = left / (left + w)
            if bv >= p: n, p = left - 1, p / bv
            else: n, p, res = right - 1, (p - bv) / (1 - bv), res + left
        q, x, s = -log(1 - p), 0, 0 # Second waiting-time method, p. 525
        try:
            while s <= q:
                s += self.expovariate(1) / (n - x)
                x += 1
        except ZeroDivisionError: x += 1
        return res + x - 1
    def poissonvariate(self, mean = 0):
        """Poisson distribution with the specified mean, which defaults to 1."""
        m, r = mean if mean > 0 else 1, 0 # Ahrens/Dieter recursive method, p. 518
        while m > 12:
            n = int(0.875 * m)
            g = self.gammavariate(n, 1)
            if g > m: return r + self.binomialvariate(n - 1, m / g)
            r, m = r + n, m - g
        s, k = 0, -1
        while s < m:
            s += self.expovariate(1)
            k += 1
        return r + k

# The following functions rely on an instance of the Kinross generator, here named rng.
rng = KinrossRandom()
def rectpointpick(c2 = 1+1j, c1 = 0):
    """Picks a point in the rectangle with c1 and c2 as opposite corners."""
    return complex(linterp(c1.real, c2.real, rng.random()), linterp(c1.imag, c2.imag, rng.random()))
def roundpointpick(r = 1, c = 0, ri = 0):
    """Picks a point in the circle/annulus with centre c, outer radius r and inner radius ri."""
    return c + rect(sqrt(rng.uniform(ri * ri, r * r)), 6.283185307179586 * rng.random())
def trianglepointpick(v1 = 1, v2 = 1j, o = 0):
    """Picks a point within the triangle with vertices at o, o + v1 and o + v2."""
    t1, t2 = rng.random(), rng.random()
    if t1 + t2 > 1: t1, t2 = 1 - t1, 1 - t2
    return o + v1 * t1 + v2 * t2

def bridsondisc(c2 = 64+64j, r = 1, c1 = 0):
    """Poisson-samples the given rectangular region with all distances between points at least r using Bridson's algorithm.
    My empirical tests show the number of circles generated as approximately 0.679 * area / radius^2; since this balloons very fast, the procedure here is a generator."""
    rvec, msh, r2 = c2 - c1, r * 0.7071067811865476, r * r # http://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
    sense_x, sense_y, w, h = -1 if rvec.real < 0 else 1, -1 if rvec.imag < 0 else 1, abs(rvec.real), abs(rvec.imag)
    NX, NY = ceil(w / msh), ceil(h / msh)
    grid = [[None for q in range(NX)] for q in range(ceil(NY))]
    p0 = complex(w * rng.random(), h * rng.random())
    g0 = (int(p0.imag / msh), int(p0.real / msh))
    active = [p0]
    yield c1 + complex(p0.real * sense_x, p0.imag * sense_y)
    grid[g0[0]][g0[1]] = p0
    def faraway(b, dy, dx):
        fy, fx = b[1][0] + dy, b[1][1] + dx
        if 0 <= fy < NY and 0 <= fx < NX:
            op = grid[fy][fx]
            if op != None:
                ov = op - b[0]
                if ov.real * ov.real + ov.imag * ov.imag < r2: return False
        return True
    while active:
        sel, cup = rng.randrange(len(active)), None
        pivot = active[sel]
        for q in range(32):
            cand = roundpointpick(2 * r, pivot, r)
            if 0 <= cand.real < w and 0 <= cand.imag < h:
                cb, notclose = (cand, (int(cand.imag / msh), int(cand.real / msh))), True
                for m in ((0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)):
                    if not faraway(cb, *m):
                        notclose = False
                        break
                if notclose:
                    sx, sy, tsqs = cand.real % msh / msh, cand.imag % msh / msh, []
                    if sx > 0.585786437626905: tsqs += ((-1, 2), (0, 2), (1, 2))
                    if sy > 0.585786437626905: tsqs += ((2, -1), (2, 0), (2, 1))
                    if sx < 0.41421356237309503: tsqs += ((-1, -2), (0, -2), (1, -2))
                    if sy < 0.41421356237309503: tsqs += ((-2, -1), (-2, 0), (-2, 1))
                    for m in tsqs:
                        if not faraway(cb, *m):
                            notclose = False
                            break
                    if notclose:
                        cup = cb
                        break
        if cup:
            active.append(cup[0])
            yield c1 + complex(cup[0].real * sense_x, cup[0].imag * sense_y)
            grid[cup[1][0]][cup[1][1]] = cup[0]
        else: del active[sel]
    return

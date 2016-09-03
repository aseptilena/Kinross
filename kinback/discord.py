# Helper functions for Kinross: random point and structure generation (and a nod to MLPFIM's Discord)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
import random
from math import sqrt, log, ceil, pi
from cmath import rect
from .algebra import linterp
T = 2 * pi
BDG, BDL, BDU = sqrt(2) / 2, sqrt(2) - 1, 2 - sqrt(2) # constants for the Bridson-disc algorithm

# SystemRandom is good enough for simulation and pretty pictures, but here I add a few more useful functions, especially discrete distributions.
# Page numbers below refer to Luc Devroye's book on Non-Uniform Random Variate Generation (http://luc.devroye.org/rnbookindex.html).
class KinrossRandom(random.SystemRandom):
    def geometricvariate(self, p = 0):
        """Geometric distribution with probability of success p. Here we use the number of trials before first failure;
        this is equivalent to flooring the exponential distribution with parameter -ln(1 - p). p defaults to 0.5."""
        return int(self.expovariate(log(2) if not 0 < p < 1 else -log(1 - p)))
    def gammavariate(self, k, theta):
        """Gamma distribution using Marsaglia and Tsang's method. Parameters and operation follow the GSL code for this same distribution."""
        if k < 1: return self.gammavariate(k + 1, theta) * (1 - self.random()) ** (1 / k)
        d = k - 1 / 3
        c = 1 / 3 / sqrt(d)
        while 1:
            v = 0
            while v <= 0:
                x = self.gauss(0, 1)
                v = 1 + c * x
            v, u = v ** 3, 1 - self.random()
            if u < 1 - 0.0331 * x ** 4: break
            if log(u) < 0.5 * x * x + d * (1 - v + log(v)): break
        return d * v * theta
    def kumaraswamyvariate(self, a, b):
        """Kumaraswamy distribution, an easy-to-sample approximation of the beta distribution. CDF is 1 - (1 - x ** a) ** b."""
        return (1 - (1 - self.random()) ** (1 / b)) ** (1 / a)
    def binomialvariate(self, num, prob):
        """Binomial distribution with num trials and probability prob of success."""
        if prob == 0.5: return bin(self.getrandbits(num)).count('1')
        n, p = num, prob
        res = 0 # Relles's recursive method (1972, hinted on p. 538)
        while n > 16:
            if not n & 1:
                n -= 1
                res += self.random() < p
            n >>= 1
            z = 2 # Beta variate shortcut on p. 437
            while z > 1:
                u, v = self.random(), 2 * self.random() - 1
                z = u * u + v * v
            bv = u * v * sqrt(1 - z ** (2 / (2 * n + 1))) / z + 0.5
            if bv < p: res, p = res + n + 1, (p - bv) / (1 - bv)
            else: p /= bv
        q, x, s = -log(1 - p), 0, 0 # Second waiting-time method, p. 525
        try:
            while s <= q:
                s += self.expovariate(1) / (n - x)
                x += 1
        except ZeroDivisionError: x += 1
        return res + x - 1
    def poissonvariate(self, mean):
        """Poisson distribution with the given mean."""
        m, r = mean, 0 # Ahrens/Dieter recursive method, p. 518
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
    return c + rect(sqrt(rng.uniform(ri * ri, r * r)), T * rng.random())
def trianglepointpick(v1 = 1, v2 = 1j, o = 0):
    """Picks a point within the triangle with vertices at o, o + v1 and o + v2."""
    t1, t2 = rng.random(), rng.random()
    if t1 + t2 > 1: t1, t2 = 1 - t1, 1 - t2
    return o + v1 * t1 + v2 * t2

def bridsondisc(c2 = 64+64j, r = 1, c1 = 0):
    """Poisson-samples the given rectangular region with all distances between points at least r using Bridson's algorithm.
    My empirical tests show the number of circles generated as approximately 0.679 * area / radius^2; since this balloons very fast, the procedure here is a generator."""
    rvec, msh, r2 = c2 - c1, r * BDG, r * r # http://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
    sense_x, sense_y, w, h = -1 if rvec.real < 0 else 1, -1 if rvec.imag < 0 else 1, abs(rvec.real), abs(rvec.imag)
    nx, ny = ceil(w / msh), ceil(h / msh)
    grid = [[None for q in range(nx)] for q in range(ceil(ny))]
    p0 = complex(w * rng.random(), h * rng.random())
    g0 = (int(p0.imag / msh), int(p0.real / msh))
    active = [p0]
    yield c1 + complex(p0.real * sense_x, p0.imag * sense_y)
    grid[g0[0]][g0[1]] = p0
    def faraway(b, dy, dx):
        fy, fx = b[1][0] + dy, b[1][1] + dx
        if 0 <= fy < ny and 0 <= fx < nx:
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
                    if sx > BDU: tsqs += ((-1, 2), (0, 2), (1, 2))
                    if sy > BDU: tsqs += ((2, -1), (2, 0), (2, 1))
                    if sx < BDL: tsqs += ((-1, -2), (0, -2), (1, -2))
                    if sy < BDL: tsqs += ((-2, -1), (-2, 0), (-2, 1))
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

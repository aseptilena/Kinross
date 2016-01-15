# Helper functions for Kinross: random point and structure generation (and a nod to MLPFIM's Discord)
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
import random
from math import sqrt, log, ceil
from cmath import rect
from .vectors import linterp
# SystemRandom is good enough for simulation and pretty pictures, but here I add a few more useful functions, especially discrete distributions.
# The specifications of the binomial and Poisson algorithms are from Luc Devroye's book (http://luc.devroye.org/chapter_ten.pdf).
class KinrossRandom(random.SystemRandom):
    def geometricvariate(self, p = 0):
        """Geometric distribution with probability of success p. Here we use the number of trials before first failure;
        this is equivalent to flooring the exponential distribution with parameter -ln(1 - p). p defaults to 0.5."""
        return int(self.expovariate(log(2) if not 0 < p < 1 else -log(1 - p)))
    def binomialvariate(self, num = 0, prob = 2):
        """Binomial distribution with the specified number of trials and probability of success; parameters default to 16 and 0.5."""
        n, p = 16 if num == 0 else ceil(abs(num)), 0.5 if not 0 <= prob <= 1 else prob # Waiting-time method, page 525
        if p == 0: return 0
        if p == 1: return n
        if p > 0.5: return n - self.binomialvariate(n, 1 - p)
        t = 0
        for res in range(n + 1):
            t += self.geometricvariate(p) + 1
            if t > n: return res
    def poissonvariate(self, mean = 0):
        """Poisson distribution with the specified mean, which defaults to 1."""
        m, r = mean if mean > 0 else 1, 0 # Ahrens/Dieter recursive method, page 518
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
    """Picks a point in the annulus/circle with centre c, outer radius r and inner radius ri."""
    return c + rect(sqrt(rng.uniform(ri * ri, r * r)), 6.283185307179586 * rng.random())
def trianglepointpick(v1 = 1, v2 = 1j, o = 0):
    """Picks a point within the triangle with vertices at o, o + v1 and o + v2."""
    t1, t2 = rng.random(), rng.random()
    if t1 + t2 > 1: t1, t2 = 1 - t1, 1 - t2
    return o + v1 * t1 + v2 * t2

def bridsondisc(c2 = 64+64j, c1 = 0, r = 1):
    """Poisson-samples the given rectangular region with all distances between points at least r using Bridson's algorithm; returns the points sampled."""
    # http://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
    pass # TODO

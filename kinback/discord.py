# Helper functions for Kinross: random point and structure generation (and a nod to MLPFIM's Discord)
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
import random
from math import log, ceil
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

# Helper functions for Kinross: random point and structure generation (and a nod to MLPFIM's Discord)
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
import random
from math import log
# The operating system random number generator is good enough for simulation and making pretty pictures.
# However, here I subclass it with a few more useful functions.
class KinrossRandom(random.SystemRandom):
    def geometricvariate(self, p = 0):
        """Geometric distribution with probability of success p. Here we use the number of trials before first failure;
        this is equivalent to flooring the exponential distribution with parameter -ln(1 - p). p defaults to 0.5."""
        return int(self.expovariate(log(2) if not 0 < p < 1 else -log(1 - p)))
    def poissonvariate(self, mean = 1):
        """Poisson distribution with the specified mean; defaults to 1."""
        pass # TODO

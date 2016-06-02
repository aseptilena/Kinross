# Helper functions for Kinross: ellipses (part of Rarify phase 4)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import pi, sqrt, hypot, degrees
from .vectors import *
from .regexes import fsmn
from .algebra import polyn, matdeterm
from .affines import affine
hpi = pi / 2

class oval:
    def __init__(self, centre = 0j, rx = 1, ry = 1, tilt = 0):
        self.centre, self.rx, self.ry = centre, abs(rx), abs(ry)
        self.tilt = tilt - pi * int(tilt / pi) # (-pi, pi)
        if self.tilt <= -hpi: self.tilt += pi
        if self.tilt > hpi: self.tilt -= pi
    def __str__(self): return "Ellipse centred on {} with axes {} and {}, the first axis tilted by {}".format(self.centre, self.rx, self.ry, self.tilt)
    def __repr__(self): return "oval({}, {}, {}, {})".format(self.centre, self.rx, self.ry, self.tilt)
    def svgrepr(self):
        """Returns the minimal SVG representation of the oval: tag, {attributes}."""
        a, b = fsmn(self.rx), fsmn(self.ry)
        if a == b: tag, resd = "circle", {"cx": fsmn(self.centre.real), "cy": fsmn(self.centre.imag), "r": a} # circle
        else:
            oc, theta = turn(self.centre, -self.tilt), fsmn(degrees(self.tilt))
            tag, resd = "ellipse", {"cx": fsmn(oc.real), "cy": fsmn(oc.imag), "rx": a, "ry": b}
            if theta != "0": resd["transform"] = "rotate({})".format(theta)
        if resd["cx"] == "0": del resd["cx"]
        if resd["cy"] == "0": del resd["cy"]
        return tag, resd
    
    def a(self): return max(self.rx, self.ry)
    def b(self): return min(self.rx, self.ry)
    def a_vect(self): return rect(self.a(), self.tilt + hpi * (self.rx <  self.ry))
    def b_vect(self): return rect(self.b(), self.tilt + hpi * (self.rx >= self.ry))
    def f(self): return sqrt(abs(self.rx * self.rx - self.ry * self.ry)) # Distance of foci from centre
    def e(self): return self.f() / self.a()
    def foci(self):
        fv = rect(self.f(), self.tilt + hpi * (self.rx < self.ry))
        return (self.centre + fv, self.centre - fv)
    
    def parampoint(self, th):
        """The point on this ellipse with eccentric anomaly (or parameter of the classic parametric form) th relative to the zero vertex."""
        return self.centre + turn(complex(self.rx * cos(th), self.ry * sin(th)), self.tilt)
    # The two functions below give perpendicular vertices of the ellipse, one at 0 and the other at +pi/2
    def v0(self): return self.centre + rect(self.rx, self.tilt)
    def v1(self): return self.centre + rect(self.ry, self.tilt + hpi)
    def anglepoint(self, th = 0.):
        """The point on this ellipse at an actual angle of th to the zero vertex."""
        r = self.rx * self.ry / hypot(self.ry * cos(a), self.rx * sin(a))
        return self.centre + turn(rect(r, th), self.tilt)
    def raypoint(self, p):
        """Intersection of the ray from the centre to the specified point with the ellipse. The Kinross elliptical arc representation uses this to determine endpoints."""
        if isclose(p, self.centre): return self.v0()
        return self.anglepoint(signedangle(p, self.v0(), self.centre))
    def semiperimeter(self):
        """Iterative formula for the elliptic integral from http://www.ams.org/notices/201208/rtx120801094p.pdf (Semjon Adlaj, Notices of the AMS, 59 (8) p. 1094, September 2012)."""
        beta = self.b() / self.a()
        nx, ny, nz = 1, beta * beta, 0
        while not isclose(nx, ny, abs_tol=1e-14):
            rd = sqrt((nx - nz) * (ny - nz))
            nx, ny, nz = (nx + ny) / 2, nz + rd, nz - rd
        n = (nx + ny) / 2
        mx, my = 1, beta
        while not isclose(mx, my, abs_tol=1e-14): mx, my = (mx + my) / 2, sqrt(mx * my)
        m = (mx + my) / 2
        return float(n / m) * pi * self.a()
    def perimeter(self): return self.semiperimeter() * 2
    def quartrarc(self): return self.semiperimeter() / 2
    
    def affine(self, mat):
        """Transforms the ellipse by the given matrix; uses Rytz's construction."""
        tc, a, b = (affine(mat, p) for p in (self.centre, self.v0(), self.v1()))
        if isclose(angle(a, b, tc), hpi): return oval(tc, abs(a - tc), abs(b - tc), phase(a - tc))
        c = rturn(a, tc)
        m = between(b, c)
        d = abs(m - tc)
        mb, mc = lenvec(b, d, m), lenvec(c, d, m)
        z1, z2 = lenvec(mb, abs(mc - b), tc), lenvec(mc, abs(mb - b), tc)
        return oval(tc, abs(z1 - tc), abs(z2 - tc), phase(z1 - tc))
    def uc_affine(self):
        """The transformation that maps this ellipse to the centred unit circle, which has a nice closed form."""
        s, c = sin(self.tilt), cos(self.tilt)
        return (c / self.ry, s / self.ry, -s / self.rx, c / self.rx, -(s * self.centre.imag + c * self.centre.real) / self.rx,
                                                                      (s * self.centre.real - c * self.centre.imag) / self.ry)
    def uc_invaffine(self):
        """The inverse of uc_affine() (i.e. the transformation from the unit circle to this ellipse), whose form is even simpler."""
        s, c = sin(self.tilt), cos(self.tilt)
        return (c * self.rx, s * self.rx, -s * self.ry, c * self.ry, self.centre.real, self.centre.imag)

def ell5pts(q, r, s, t, u):
    """Constructs the ellipse passing through the five points. The algorithms are from the equivalent Pernsteiner extension (http://pernsteiner.org/inkscape/ellipse_5pts)."""
    pmat, coeffs = [[p.real * p.real, p.real * p.imag, p.imag * p.imag, p.real, p.imag, 1.] for p in (q, r, s, t, u)], []
    rmat = tuple(zip(*pmat))
    for i in range(6):
        sqmat = [rmat[j] for j in range(6) if i != j]
        coeffs.append(matdeterm(sqmat) * (-1 if i % 2 else 1))
    a, b, c, d, e, f = coeffs
    qd = 4 * a * c - b * b
    if isclose(matdeterm([[a * 2, b, d], [b, c * 2, e], [d, e, f * 2]]), 0) or qd <= 0: return None
    centre = complex((b * e - 2 * c * d) / qd, (b * d - 2 * a * e) / qd)
    cx, cy = centre.real, centre.imag
    axes = [1, 1j] if isclose(b, 0) else [hat(complex(b / 2, l - a)) for l in polyn(qd, -(a + c) * 4, 4).rroots()]
    lens = [0, 0]
    for i in (0, 1):
        dx, dy = axes[i].real, axes[i].imag
        qa = a * dx * dx + b * dx * dy + c * dy * dy
        qb = 2 * a * cx * dx + b * (cx * dy + cy * dx) + 2 * c * cy * dy + d * dx + e * dy
        qc = a * cx * cx + b * cx * cy + c * cy * cy + d * cx + e * cy + f
        lens[i] = max(polyn(qc, qb, qa).rroots())
    return oval(centre, lens[0], lens[1], phase(axes[0]))

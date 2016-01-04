# Helper functions for Kinross: ellipses (part of Rarify phase 4)
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
from math import pi, sqrt, hypot, degrees
from .vectors import *
from .regexes import floatinkrep, tokenisetransform
from .algebra import polyn, matdeterm
from .affines import affine, composition, translation, rotation, scaling, parsetransform
hpi = pi / 2

class oval:
    def __init__(self, centre = 0j, rx = 1, ry = 1, tilt = 0):
        self.centre, self.rx, self.ry = centre, abs(rx), abs(ry)
        self.tilt = tilt - pi * int(tilt / pi) # (-pi, pi)
        if self.tilt <= -hpi: self.tilt += pi
        if self.tilt > hpi: self.tilt -= pi
    def __str__(self): return "Ellipse centred on {} with axes {} and {}, the first axis tilted by {}".format(printpoint(self.centre), self.rx, self.ry, self.tilt)
    def __repr__(self): return "oval({}, {}, {}, {})".format(self.centre, self.rx, self.ry, self.tilt)
    def svgrepr(self):
        """Returns the minimal SVG representation of this ellipse {cx, cy, rx, ry, th}, where all items are string representations and th is applied as part of a transformation."""
        oc = turn(self.centre, -self.tilt)
        x, y, a, b = [floatinkrep(v) for v in (oc.real, oc.imag, self.rx, self.ry)]
        th = "rotate({})".format(floatinkrep(degrees(self.tilt)))
        return {"cx": x, "cy": y, "rx": a, "ry": b, "transform": th}
    
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
    # The two functions below give perpendicular vertices of the ellipse
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
        """Transforms the ellipse by the given matrix."""
        return rytz(affine(mat, self.centre), affine(mat, self.v0()), affine(mat, self.v1()))
    def uc_affine(self):
        """The transformation that maps this ellipse to the centred unit circle."""
        return composition(scaling(1 / self.rx, 1 / self.ry), rotation(-self.tilt), translation(-self.centre))
    def uc_invaffine(self):
        """The inverse of uc_affine() (i.e. the transformation from the unit circle to this ellipse). This is calculated separately to reduce floating-point error."""
        return composition(translation(self.centre), rotation(self.tilt), scaling(self.rx, self.ry))

def rytz(centre, a, b):
    """Rytz's construction for finding axes from conjugated diameters or equivalently a transformed rectangle.
    Used to remove the transformation matrix from SVG ellipses (and a lot of other things)."""
    if isclose(angle(a, b, centre), hpi): return oval(centre, abs(a - centre), abs(b - centre), phase(a - centre))
    else:
        c = rturn(a, centre)
        m = between(b, c)
        d = abs(m - centre)
        mb, mc = lenvec(b, d, m), lenvec(c, d, m)
        z1, z2 = lenvec(mb, abs(mc - b), centre), lenvec(mc, abs(mb - b), centre)
        return oval(centre, abs(z1 - centre), abs(z2 - centre), phase(z1 - centre))

def ellipsecollapse(w):
    """Given a transformed ellipse element, collapses the transform into the ellipse if it has no stroke."""
    sty = w.get("style", "")
    if w.get("stroke") == None and ";stroke:" not in sty and not sty.startswith("stroke:"):
        tkdtf = tokenisetransform(w.get("transform")) # The calling function must guarantee that the ellipse has a transform, so tkdtf is not empty
        if len(tkdtf) != 1 or tkdtf[0][0] != "rotate" or len(tkdtf[0][1]) > 1:
            outp = oval(complex(float(w.get("cx", "0")), float(w.get("cy", "0"))), float(w.get("rx")), float(w.get("ry"))).affine(parsetransform(w.get("transform"))).svgrepr()
            w.attrib.update(outp)
            if outp["cx"] == "0": del w.attrib["cx"]
            if outp["cy"] == "0": del w.attrib["cy"]
            if outp["transform"] == "rotate(0)": del w.attrib["transform"]

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

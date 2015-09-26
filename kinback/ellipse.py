# Helper functions for Kinross: circles, ellipses and arcs
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from .vectors import *
from .polynomial import polynomroot
from math import pi, sqrt, fabs, hypot, copysign, radians
hpi = pi / 2

# Ellipses have a centre, two axis lengths and the signed angle of +x relative to semi-first axis. This last angle is normalised to (-pi/2, pi/2].
class ellipse:
    def __init__(self, centre, rx, ry, tilt = 0.):
        self.centre, self.rx, self.ry = centre, fabs(rx), fabs(ry)
        self.tilt = tilt - pi * int(tilt / pi) # (-pi, pi)
        if self.tilt <= -hpi: self.tilt += pi
        if self.tilt > hpi: self.tilt -= pi
    def __str__(self): return "Ellipse centred on {} with axes {} and {}, the first axis tilted by {}".format(printpoint(self.centre), self.rx, self.ry, self.tilt)
    def __repr__(self): return "ellipse({}, {}, {}, {})".format(self.centre, self.rx, self.ry, self.tilt)
    def geogebrarepr(self):
        """Returns the GeoGebra representation of this ellipse."""
        ff = self.foci()
        return "Ellipse[({},{}),({},{}),{}]".format(ff[0].real, ff[0].imag, ff[1].real, ff[1].imag, self.a())
    
    def a(self): return max(self.rx, self.ry) # Semi-major axis length
    def b(self): return min(self.rx, self.ry) # Semi-minor axis length
    def a_vect(self): return rect(self.a(), self.tilt + hpi * (self.rx <  self.ry)) # Semi-major axis vector
    def b_vect(self): return rect(self.b(), self.tilt + hpi * (self.rx >= self.ry)) # Semi-minor axis vector
    def f(self): return sqrt(abs(self.rx * self.rx - self.ry * self.ry)) # Distance from centre to either focus
    def e(self): return self.f() / self.a() # Eccentricity
    def foci(self):
        fv = rect(self.f(), self.tilt + hpi * (self.rx < self.ry))
        return (self.centre + fv, self.centre - fv)
    
    def parampoint(self, th):
        """The point on this ellipse with eccentric anomaly (or parameter of the classic parametric form) th relative to the zero vertex."""
        return self.centre + turn(point(self.rx * cos(th), self.ry * sin(th)), self.tilt)
    def zerovertex(self): return self.centre + rect(self.rx, self.tilt) # This vertex is considered the zero point for angles
    def hpivertex(self): return self.centre + rect(self.ry, self.tilt + hpi) # The point at +90 degrees to the zero vertex
    def anglepoint(self, th = 0.):
        """The point on this ellipse at an actual angle of th to the zero vertex."""
        r = self.rx * self.ry / hypot(self.ry * cos(a), self.rx * sin(a))
        return self.centre + turn(rect(r, th), self.tilt)
    def raypoint(self, p):
        """Intersection of the ray from the centre to the specified point with the ellipse.
        The Kinross elliptical arc representation uses this to determine endpoints."""
        if near(p, self.centre): return self.zerovertex()
        return self.anglepoint(signedangle(p, self.zerovertex(), self.centre))
    def psideof(self, p):
        """-1 if p is inside the ellipse, 0 if on and 1 if outside."""
        pins = self.foci()
        z = abs(p - pins[0]) + abs(p - pins[1]) - 2 * self.a()
        if near(z, 0., 1e-12): return 0
        return copysign(1, z)
    def perimeter(self):
        """Iterative formula for calculating the required elliptic integral from
        http://www.ams.org/notices/201208/rtx120801094p.pdf (Semjon Adlaj, Notices of the AMS, September 2012).
        To ensure accuracy, decimal floating-point arithmetic is used."""
        from decimal import Decimal as D, localcontext
        with localcontext() as c:
            c.prec, err = 45, D("5e-21")
            beta = D(self.b()) / D(self.a())
            nx, ny, nz = D(1), beta * beta, D(0)
            while not near(nx, ny, err):
                rd = ((nx - nz) * (ny - nz)).sqrt()
                nx, ny, nz = (nx + ny) / 2, nz + rd, nz - rd
            n = (nx + ny) / 2
            mx, my = D(1), beta
            while not near(mx, my, err): mx, my = (mx + my) / 2, (mx * my).sqrt()
            m = (mx + my) / 2
        return 2 * float(n / m) * pi * self.a()
    def affine(self, mat):
        """Transforms the ellipse by the given matrix."""
        return rytz(affine(mat, self.centre), affine(mat, self.zerovertex()), affine(mat, self.hpivertex()))
    def uc_affine(self):
        """The transformation that maps this ellipse to the centred unit circle."""
        return composition(scaling(1 / self.rx, 1 / self.ry), rotation(-self.tilt), translation(-self.centre))
    def uc_invaffine(self):
        """The inverse of uc_affine() (i.e. the transformation from the unit circle to this ellipse). This is calculated separately to reduce floating-point error."""
        return composition(translation(self.centre), rotation(self.tilt), scaling(self.rx, self.ry))

class circle:
    """Circles are the same as ellipses, only with one radius and no tilt."""
    def __init__(self, centre = 0j, r = 1): self.centre, self.r = centre, fabs(r)
    def __str__(self): return "Circle with centre {} and radius {}".format(printpoint(self.centre), self.r)
    def __repr__(self): return "circle({}, {})".format(self.centre, self.r)
    def toellipse(self): return ellipse(self.centre, self.r, self.r) # A coercing function
    
    def raypoint(self, p): return lenvec(p, self.r, self.centre)
    def anglepoint(self, th = 0.): return self.centre + rect(self.r, th) # from the +x-axis
    def perimeter(self): return 2 * pi * self.r

def rytz(centre, a, b):
    """Rytz's construction for finding axes from conjugated diameters or equivalently a transformed rectangle.
    Used to remove the transformation matrix from SVG ellipses (and a lot of other things)."""
    if near(dot(a, b, centre), 0.): return ellipse(centre, abs(a - centre), abs(b - centre), phase(a - centre))
    else:
        c = rturn(a, centre)
        m = between(b, c)
        d = abs(m - centre)
        mb, mc = lenvec(b, d, m), lenvec(c, d, m)
        v1, v2 = lenvec(mb, abs(mc - b), centre), lenvec(mc, abs(mb - b), centre)
        return ellipse(centre, abs(v1 - centre), abs(v2 - centre), phase(v1 - centre))

def circ3pts(a, b, c):
    """Constructs the (circum)circle passing through the three points."""
    if collinear(a, b, c): return None
    centre = intersect_ll(perpbisect(a, b), perpbisect(a, c), False)
    return circle(centre, abs(a - centre))

def ell5pts(q, r, s, t, u):
    """Constructs the ellipse passing through the five points. The algorithms are from the equivalent Pernsteiner extension (http://pernsteiner.org/inkscape/ellipse_5pts)."""
    pmat, coeffs = [[p.real * p.real, p.real * p.imag, p.imag * p.imag, p.real, p.imag, 1.] for p in (q, r, s, t, u)], []
    rmat = tuple(zip(*pmat))
    for i in range(6):
        sqmat = [rmat[j] for j in range(6) if i != j]
        coeffs.append(matdeterm(sqmat) * (-1 if i % 2 else 1))
    a, b, c, d, e, f = coeffs
    qd = 4 * a * c - b * b
    if near(matdeterm([[a * 2, b, d], [b, c * 2, e], [d, e, f * 2]]), 0., 1e-9) or qd <= 0.: return None
    centre = point((b * e - 2 * c * d) / qd, (b * d - 2 * a * e) / qd)
    cx, cy = centre.real, centre.imag
    axes = [1., 1j] if near(b, 0., 1e-9) else [hat(point(b / 2, l - a)) for l in polynomroot((qd, -(a + c) * 4, 4))[0]]
    lens = [0., 0.]
    for i in (0, 1):
        dx, dy = axes[i].real, axes[i].imag
        qa = a * dx * dx + b * dx * dy + c * dy * dy
        qb = 2 * a * cx * dx + b * (cx * dy + cy * dx) + 2 * c * cy * dy + d * dx + e * dy
        qc = a * cx * cx + b * cx * cy + c * cy * cy + d * cx + e * cy + f
        lens[i] = max(polynomroot((qc, qb, qa))[0])
    return ellipse(centre, lens[0], lens[1], phase(axes[0]))

def intersect_cl(c, l):
    """Circle/line intersection. Intersection functions beyond line/line like this one always return a tuple due to multiple solutions."""
    z = perpdist(c.centre, l)
    if z > c.r: return ()
    f = footperp(c.centre, l)
    dv = lenvec(l[1] - l[0], sqrt(c.r * c.r - z * z))
    return (f + dv, f - dv)

def radicalline(c, d):
    """Radical line between two circles; if the circles intersect this line passes through both of them.
    This is a separate function to help with the problem of Apollonius."""
    d0 = d.centre - c.centre
    d1 = ((c.r * c.r - d.r * d.r) / abs(d0) + abs(d0)) / 2
    rc = c.centre + lenvec(d0, d1)
    return (rc + lturn(d0), rc + rturn(d0))

def intersect_cc(c, d):
    """Circle/circle intersection, a common problem in 2D video gaming."""
    z, plus, minus = sqabs(d.centre, c.centre), c.r + d.r, c.r - d.r
    if z > plus * plus or z <= minus * minus: return ()
    return intersect_cl(c, radicalline(c, d))

def intersect_el(e, l):
    """Ellipse/line intersection; transform the ellipse to a unit circle and work from there."""
    ll = tuple(affine(e.uc_affine(), p) for p in l)
    ii = intersect_cl(circle(), ll)
    return tuple(affine(e.uc_invaffine(), i) for i in ii)

def intersect_ee(e, f):
    """Ellipse/ellipse intersection; sample at many points and refine with bisection. See mathforum.org/library/drmath/view/66877.html for the derivation."""
    N, res = 256, []
    sides = [f.psideof(e.parampoint(2 * pi * i / N)) for i in range(N)]
    for i in range(N):
        if not sides[i]: res.append(e.parampoint(2 * pi * i / N))
        if sides[i] * sides[i - 1] == -1:
            lower, higher = 2 * pi * (i - 1) / N, 2 * pi * i / N
            nadded, lside, hside = True, sides[i - 1], sides[i]
            while higher - lower > 1e-12:
                mid = (lower + higher) / 2
                mside = f.psideof(e.parampoint(mid))
                if not mside:
                    res.append(e.parampoint(mid))
                    nadded = False
                    break
                if lside * mside == 1: lower = mid
                else: higher = mid
            if nadded: res.append(e.parampoint((lower + higher) / 2))
    return tuple(res)

def intersect_ec(e, c):
    """Once the two-ellipse problem is solved this becomes trivial to implement."""
    return intersect_ee(e, c.toellipse())

# With the ellipse functions settled elliptical arcs are now implementable.
# They have an ellipse with a starting and ending ray; the arc itself always moves positive-angle/clockwise from start to end.
# For compatibility with the Bezier class (in particular the parametrisation) this is also a class.
class elliparc:
    def __init__(self, start, in_rx, in_ry, in_phi = None, large = None, sweep = None, end = None):
        """Initialises with the arc's Kinross representation (tstart, ell, tend), where tstart < tend if the arc is positive-angle and vice versa.
        (Yes, the parameters can go beyond [-pi, pi] here; phi should be given in degrees, as will happen in SVG path parsing.)
        Cases where the ellipse is too small are handled as per the SVG specifications (i.e. scale until a fit is possible).
        Note that this can also be initalised with only the three internally stored parameters for repr()'s ease."""
        if in_phi == None: self.tstart, self.ell, self.tend = float(start), in_rx, float(in_ry) # The "grade-A" example of duck typing
        else:
            midarc, phi = between(start, end), radians(in_phi)
            startp = affine(composition(rotation(-phi), translation(-midarc)), start)
            # Compute the discriminant that tells whether the ellipse is too small
            rx, ry = fabs(in_rx), fabs(in_ry)
            delta = hypot(startp.real / rx, startp.imag / ry)
            if delta > 1: rx, ry, centrep = rx * delta, ry * delta, 0 # it is scaled
            else:
                spsqt = (rturn if bool(large) == bool(sweep) else lturn)(affine(squeezing(ry / rx), startp))
                centrep = spsqt * sqrt(1 / (delta * delta) - 1)
            centre = affine(composition(translation(midarc), rotation(phi)), centrep)
            self.ell = ellipse(centre, rx, ry, phi)
            taff = self.ell.uc_affine()
            tstart, tend = phase(affine(taff, start)), phase(affine(taff, end))
            if bool(sweep) and tstart > tend: tend += 2 * pi
            if not bool(sweep) and tstart < tend: tstart += 2 * pi
            self.tstart, self.tend = tstart, tend
    def __str__(self):
        return "{{{}, {}, {}, {}: {} -> {}}}".format(printpoint(self.ell.centre), self.ell.rx, self.ell.ry, self.ell.tilt, self.tstart, self.tend)
    def __repr__(self):
        return "elliparc({}, {}, {})".format(self.tstart, repr(self.ell), self.tend)
    def __call__(self, t):
        """See? This is why the endpoint parameters are allowed to go outside the principal range here."""
        return self.ell.parampoint(linterp(self.tstart, self.tend, t))
    def start(self): return self.ell.parampoint(self.tstart)
    def end(self): return self.ell.parampoint(self.tend)

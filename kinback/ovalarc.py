# Helper functions for Kinross: the elliptical arc class
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
from math import pi, sqrt, hypot, tan, atan, radians, floor, ceil
from .vectors import *
from .algebra import rombergquad
from .regexes import floatinkrep
from .affines import affine, backaffine
from .ellipse import oval
hpi = pi / 2

class elliparc:
    def __init__(self, *data):
        """Initialises the Kinross arc. tstart to tend is increasing if the arc turns clockwise; phi is in degrees."""
        self.deg = -1
        if len(data) == 3: # tstart, ell, tend (Kinross representation)
            self.tstart, self.ell, self.tend = data
        elif len(data) == 7: # start, rx, ry, phi, large, sweep, end (SVG representation)
            start, rx, ry, phi, large, sweep, end = data
            if isclose(start, end): self.tstart, self.tend, self.ell = 7, 7, [start, end]
            else:
                rx, ry, phi = abs(rx), abs(ry), radians(phi)
                if rx < 1e-8 or ry < 1e-8: self.tstart, self.tend, self.ell = 8, 8, [start, end]
                else:
                    z1, z2, mid = turn(rx, phi), turn(ry * 1j, phi), between(start, end)
                    uc2e = (z1.real, z1.imag, z2.real, z2.imag, mid.real, mid.imag)
                    astt, aend = backaffine(uc2e, start), backaffine(uc2e, end)
                    large, sweep = large != 0, sweep != 0 # True = 1, False = 0
                    if abs(astt - aend) >= 2: # There is only one ellipse or the ellipse is too small
                        c, self.tstart, self.tend = mid, phase(astt), phase(aend)
                    else:
                        l = abs(astt)
                        rac = sqrt(1 - l * l)
                        ac = rect(rac, phase(astt) + hpi * (1 if large == sweep else -1))
                        c, self.tstart, self.tend = affine(uc2e, ac), phase(astt - ac), phase(aend - ac)
                    self.ell = oval(c, rx, ry, phi)
                    if self.tstart > self.tend and     sweep: self.tend += 2 * pi
                    if self.tstart < self.tend and not sweep: self.tend -= 2 * pi
        if type(self.ell) == oval: # These values aid the arc length computation
            sr, er = (floor, ceil) if self.tend < self.tstart else (ceil, floor)
            self.sf, self.ef = sr(self.tstart / hpi), er(self.tend / hpi)
    def __str__(self):
        return "{{{} {} {} {} {}:{}}}".format(floatinkrep(self.ell.centre.real) + "," + floatinkrep(self.ell.centre.imag),
                                              floatinkrep(self.ell.rx), floatinkrep(self.ell.ry), floatinkrep(self.ell.tilt), self.tstart, self.tend)
    def __repr__(self):
        return "elliparc({}, {}, {})".format(self.tstart, repr(self.ell), self.tend)
    
    def __call__(self, t):
        """See? This is why the endpoint parameters are allowed to go outside the principal range here."""
        return self.ell.parampoint(linterp(self.tstart, self.tend, t))
    def start(self): return self.ell.parampoint(self.tstart)
    def end(self): return self.ell.parampoint(self.tend)
    def split(self, t):
        """Splits the arc at parameter t, returning a list that can then be inserted."""
        mv = linterp(self.tstart, self.tend, t)
        return [elliparc(self.tstart, self.ell, mv), elliparc(mv, self.ell, self.tend)]
    def reverse(self):
        """Returns the arc reversed."""
        return elliparc(self.tend, oval(self.ell.centre, self.ell.rx, self.ell.ry, self.ell.tilt), self.tstart)
    
    def velocity(self, t):
        """Returns the velocity (first derivative) of the curve at parameter t."""
        et = linterp(self.tstart, self.tend, t)
        return turn(complex(-sin(et) * self.ell.rx, cos(et) * self.ell.ry) * (1 if tstart < tend else -1), self.ell.tilt)
    def startdirc(self): return self.velocity(0)
    def enddirc(self): return -self.velocity(1)
    
    def affine(self, mat):
        """Transforms the arc by the given matrix."""
        nell, pst, pen = self.ell.affine(mat), affine(mat, self.start()), affine(mat, self.end())
        z = nell.uc_affine()
        start, end = phase(affine(z, pst)), phase(affine(z, pen))
        if self.tstart < self.tend and start > end: end += 2 * pi
        if self.tstart > self.tend and start < end: start += 2 * pi
        return elliparc(start, nell, end)
    def boundingbox(self):
        """The elliptical arc's orthogonal bounding box."""
        if isclose(self.ell.tilt, 0) or isclose(abs(self.ell.tilt), hpi): tbnds = (0, hpi)
        else:
            r = self.ell.ry / self.ell.rx
            tbnds = (atan(-r * tan(self.ell.tilt)), atan(r / tan(self.ell.tilt)))
        tl, tm = sorted([self.tstart, self.tend])
        tangs = [[self.ell.parampoint(pi * i + c) for i in range(ceil((tl - c) / pi), floor((tm - c) / pi) + 1)] for c in tbnds]
        return pointbounds(tangs[0] + tangs[1] + [self.start(), self.end()])
    
    def lenf(self):
        """The function that is integrated to obtain the length of this arc."""
        def z(t): return hypot(sin(t) * self.ell.rx, cos(t) * self.ell.ry)
        return z
    def length(self, end = None, start = None):
        """The length of this arc between the specified parameters. None signifies that the length extends to the respective end (0 or 1)."""
        if end != None or start != None:
            if start == None: return self.split(end)[0].length()
            elif end == None: return self.split(start)[1].length()
            else: return self.split(end)[0].split(start / end)[1].length()
        if isclose(self.tstart, self.tend): return 0
        lf = self.lenf()
        if (self.tend - self.tstart) * (self.ef - self.sf) < 0: return abs(rombergquad(lf, self.tstart, self.tend))
        sl = rombergquad(lf, self.tstart, self.sf * hpi) + self.ell.quartrarc() * (self.ef - self.sf) + rombergquad(lf, self.ef * hpi, self.tend)
        return -sl if self.tend < self.tstart else sl
    def invlength(self, frac):
        """Computes the t value where self.length(t) / self.length() = frac."""
        if frac <= 0: return 0
        if frac >= 1: return 1
        whole = self.length()
        target, fa = frac * whole, self.length(frac)
        lower, higher = (frac, 1) if fa < target else (0, frac)
        flower, fire, status = self.length(lower), self.length(higher), 0
        for q in range(64):
            if not isclose(lower, higher, rel_tol=1e-15):
                mt = (target - flower) / (fire - flower)
                if status == 2: mt, status = mt / 2, 0
                elif status == -2: mt, status = (1 + mt) / 2, 0
                mid = linterp(lower, higher, mt)
                fmid = self.length(mid)
                if fmid < target: lower, flower, status = mid, fmid, min(-1, status - 1)
                elif fmid > target: higher, fire, status = mid, fmid, max(1, status + 1)
                else: break
            else: break
        return round(mid, 12)

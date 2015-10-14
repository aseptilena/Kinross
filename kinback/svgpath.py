# Helper functions for Kinross: SVG path processing
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import sin
from cmath import isclose
from .vectors import angle, reflect
from .ellipse import elliparc
from .beziers import bezier
from .regexes import tokenisepath

def parsepath(p):
    """Converts SVG paths to Kinross paths; see the readme for specifications."""
    t, pos = tokenisepath(p), 0
    out, current = [], complex(0, 0)
    take, prevailing, params = 2, "M", []
    while pos < len(t):
        # Obtain the command and its parameters
        val = t[pos]
        if type(val) == str:
            if val in "Cc": take = 6
            elif val in "MmLlTt": take = 2
            elif val in "Zz": take = 0
            elif val in "HhVv": take = 1
            elif val in "SsQq": take = 4
            elif val in "Aa": take = 7
            prevailing, params = val, t[pos + 1:pos + take + 1]
            pos += take + 1
        else:
            params = t[pos:pos + take]
            pos += take
        # Absolutise coordinates
        if prevailing == "h": params[0] += current.real
        elif prevailing == "v": params[0] += current.imag
        elif prevailing == "a":
            params[5] += current.real
            params[6] += current.imag
        elif prevailing.islower():
            for i in range(take // 2):
                params[2 * i] += current.real
                params[2 * i + 1] += current.imag
        # Fill in blanks, pair coordinates and add current position
        rhtype = prevailing.lower()
        lastseg = out[-1][-1] if len(out) > 0 and len(out[-1]) > 0 else bezier(0, 1)
        if   rhtype == "h": params.append(current.imag)
        elif rhtype == "v": params.insert(0, current.real)
        elif rhtype in "st":
            r = reflect(lastseg.p[-2], current) if lastseg.deg == (3 if rhtype == "s" else 2) else current
            params[:0] = [r.real, r.imag]
        if rhtype == "a":
            params[5:] = [complex(params[5], params[6])]
            params.insert(0, current)
        else: params = [current] + [complex(params[2 * i], params[2 * i + 1]) for i in range(len(params) // 2)]
        # Construct the next segment
        if rhtype == "m":
            if type(t[pos - 3]) != str: out[-1].append(bezier(*params))
            else: out.append([])
            current = params[1]
        elif rhtype == "z":
            spstart, spend = out[-1][0].start(), out[-1][-1].end()
            if not isclose(spstart, spend): out[-1].append(bezier(spend, spstart))
            out[-1].append(0)
            if pos < len(t) and t[pos].lower() != "m":
                out.append([])
                current = spstart
        else:
            nextseg = (elliparc if rhtype == "a" else bezier)(*params)
            out[-1].append(nextseg)
            current = nextseg.end()
    for sp in out:
        N = 0
        while N < len(sp):
            seg = sp[N]
            if seg == 0: break
            elif type(seg) == bezier:
                if min([isclose(seg.p[-1], seg.p[i]) for i in range(len(seg.p) - 1)]): del sp[N]
                else: N += 1
            elif type(seg) == elliparc:
                if seg.ell == None: del sp[N]
                else: N += 1
    return out

def prettypath(p):
    """Return a pretty string representation of a Kinross path, with <> for Bézier curves and {} for arcs rather than their class names."""
    return "\n".join([" ".join([str(seg) for seg in sp]) for sp in p])

def outputpath(r):
    """Converts Kinross paths into short SVG representations. It may not be the shortest, but it gets close."""
    pass # TODO

def reversepath(p):
    out = []
    for sp in p:
        if sp[-1] == 0: out.append([p.reverse() for p in sp[-2::-1]] + [0])
        else: out.append([p.reverse() for p in sp[::-1]])
    return out[::-1]

def minmitrelimit(p):
    """Determines the minimum integer mitre limit that will allow all middle nodes in the path to render with mitre and not bevel joins, with a minimum of 4 (the default value)."""
    mvals = []
    for sp in p:
        if sp[-1] == 0:
            sgs = sp[:-1]
            angles = [angle(sgs[i].startdirc(), sgs[i - 1].enddirc()) for i in range(len(sgs))]
    pass # TODO

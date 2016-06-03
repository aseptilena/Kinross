# Helper functions for Kinross: paths
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from math import sin, ceil, inf
from cmath import isclose
from .vectors import angle, reflect, pointbounds
from .regexes import tokenisepath
from .segment import bezier, elliparc

# TODO XXX FIXME the oval and elliparc classes have been merged into a single class, ellipt; REWRITE NECESSARY
'''def parsepath(p):
    """Converts SVG paths to Kinross paths; see the readme for specifications."""
    t, pos = tokenisepath(p), 0
    out, current = [], 0
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
        else: # pos landed on a float, command is unchanged
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
            if type(t[pos - 3]) != str: out[-1].append(bezier(*params)) # Implied moveto
            else: out.append([]) # Explicit moveto
            current = params[1]
        elif rhtype == "z":
            spstart, spend = out[-1][0].start(), out[-1][-1].end()
            if not isclose(spstart, spend): out[-1].append(bezier(spend, spstart)) # The bridging line need not be drawn if nothing is bridged
            out[-1].append(0)
            if pos < len(t) and t[pos].lower() != "m": # zC, zL, etc.
                out.append([])
                current = spstart
        else:
            if rhtype == "a":
                nextseg = elliparc(*params)
                if nextseg.tstart >= 7:
                    if nextseg.tstart == 8: nextseg = bezier(*nextseg.ell)
                    out[-1].append(nextseg)
            else:
                nextseg = bezier(*params)
                if not nextseg.isdegenerate():
                    out[-1].append(nextseg)
            current = params[-1]
    return out'''

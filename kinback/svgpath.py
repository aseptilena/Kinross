# Helper functions for Kinross: SVG path processing
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from copy import deepcopy as dup
from .ellipse import elliparc
from .beziers import bezier
from .regexes import tokenisepath

def parsepath(p):
    """Converts SVG paths to Kinross paths; see the readme for specifications."""
    t, pos = tokenisepath(p), 0
    out, current = [], point(0., 0.)
    take, prevailing, params, sonp = 2, "M", [], False # The last variable indicates "start of new path"
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
        # Convert to absolute coordinates
        if prevailing == "h": params[0] += current.real
        elif prevailing == "v": params[0] += current.imag
        elif prevailing == "a":
            params[5] += current.real
            params[6] += current.imag
        elif prevailing.islower():
            for i in range(take // 2):
                params[2 * i] += current.real
                params[2 * i + 1] += current.imag
        # Fill in blanks
        rhtype = prevailing.lower()
        if   rhtype == "h": params.append(current.imag)
        elif rhtype == "v": params.insert(0, current.real)
        elif rhtype == "s": params.insert(0, 1) # TODO
        elif rhtype == "t": params.insert(0, 1)
        # Construct the next segment
        if rhtype == "m":
            current = complex(params[0], params[1])
            out.append([])
        else:
            if rhtype == "a": nextseg = elliparc(current, params[0], params[1], params[2], params[3], params[4], complex(params[5], params[6])
            else: nextseg = bezier(*([current] + [complex(params[2 * i], params[2 * i + 1]) for i in range((take + 1) // 2)]))
            out[-1].append(nextseg)
        
        if rhtype == "s":   nextpts.insert(0, reflect(lastrh[1], lastrh[2]) if len(lastrh) == 3 else cursor)
        elif rhtype == "t": nextpts.insert(0, reflect(lastrh[0], lastrh[1]) if len(lastrh) == 2 else cursor)
        
        if rhtype != "z": current = nextseg.end()
    return out

def outputpath(r):
    """Converts Kinross paths into short SVG representations. It may not be the shortest, but it gets close."""
    # First work out the shortest number representations as strings
    pass # TODO

def reversepath(r):
    """Reverses a Kinross path. To make an independent copy, use dup(r)."""
    s = dup(r)[::-1]
    for sp in s:
        sp.reverse()
        for rh in sp: rh.reverse()
        cpen = bool(sp[0])
        if cpen: sp.insert(0, [])
        for i in range(len(sp) - 1):
            if len(sp[i + 1]) == 4: sp[i + 1].insert(1, sp[i + 1].pop())
            sp[i].append(sp[i + 1].pop(0))
        if cpen: sp.pop()
    return s

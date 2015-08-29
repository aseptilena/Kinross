#!/usr/bin/env python3.4
# Helper functions for Kinross: rhythms (SVG path processing)
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import re
from math import hypot, sqrt, pi
from .vectors import * # local
# There is pretty much only one way to write the real number regex; accordingly this is spliced from Scour
number = re.compile(r"([-+]?(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.?))(?:[eE][-+]?[0-9]+)?)")
spacing = re.compile(r"[ ,]*")

def parserhythm(p):
    out, pos, cursor = [], 0, point(0., 0.)
    take, prevailing, params = 2, "M", []
    t, tokens = [], [c for c in number.split(p) if not spacing.fullmatch(c)]
    for v in tokens:
        if " " in v or v.isalpha(): t.extend(v.replace(" ", ""))
        else: t.append(float(v))
    # The Kinross path format looks like this:
    # [
    #   [ [rhythm 1]
    #     [rhythm 2]
    #     ...
    #     [rhythm P] ] <- sub-path 1
    #   [ [rhythm 1]
    #     [rhythm 2]
    #     ...
    #     [rhythm Q] ] <- sub-path 2
    #   ...
    #   [ [rhythm 1]
    #     [rhythm 2]
    #     ...
    #     [rhythm Z] ] <- sub-path N
    #                  ]
    while pos < len(t):
        # Two phases. First obtain the command and its parameters...
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
        # ...then update out
        if prevailing == "h": params[0] += cursor.real
        elif prevailing == "v": params[0] += cursor.imag
        elif prevailing == "a":
            params[5] += cursor.real
            params[6] += cursor.imag
        elif prevailing.islower():
            for i in range(take // 2):
                params[2 * i] += cursor.real
                params[2 * i + 1] += cursor.imag
        rhtype = prevailing.lower()
        if rhtype == "h": params.append(cursor.imag)
        elif rhtype == "v": params.insert(0, cursor.real)
        if rhtype == "a": # This is taken from the implementation notes of the SVG specs. Not sure if there's a better way.
            rx, ry, phi = abs(params[0]), abs(params[1]), params[2] * pi / 180
            large, sweep = bool(params[3]), bool(params[4])
            endpoint = point(params[5], params[6])
            tfc = turn((cursor - endpoint) / 2, -phi)
            Lambda = hypot(tfc.real / rx, tfc.imag / ry)
            if Lambda > 1: rx, ry = rx * Lambda, ry * Lambda
            inter = point(rx * tfc.imag / ry, -ry * tfc.real / rx)
            centre = sqrt(rx * rx * ry * ry / (rx * rx * tfc.imag * tfc.imag + ry * ry * tfc.real * tfc.real) - 1) * inter * (-1 if large == sweep else 1)
            centre = turn(centre, phi) + midpoint(cursor, endpoint)
            xvec = centre + rect(rx, phi)
            yvec = centre + rect(ry, phi + (pi / 2 if sweep else -pi / 2))
            nextpts = [centre, xvec, yvec, endpoint]
        else: nextpts = [point(params[2 * i], params[2 * i + 1]) for i in range((take + 1) // 2)]
        if rhtype == "s":   nextpts.insert(0, reflect(lastrh[1], lastrh[2]) if len(lastrh) == 3 else cursor)
        elif rhtype == "t": nextpts.insert(0, reflect(lastrh[0], lastrh[1]) if len(lastrh) == 2 else cursor)
        if rhtype != "m" and not out[-1][-1]: out.append([[out[-1][0][0]]])
        if rhtype == "m": out.append([nextpts])
        else: out[-1].append(nextpts)
        if rhtype != "z": cursor = nextpts[-1]
    return out

# def outputrhythm(k):
#     pass TODO

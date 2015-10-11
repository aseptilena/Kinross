#!/usr/bin/env python3.5
# "Spallates" an input object on a canvas, generating a random pattern according to given variability data.
# (This is not Splatoon, mind you, it's the nuclear process)
# The circle and star templates included match the behaviour of the old circle-starfield and star-starfield scripts,
# being used to generate MLPFIM starry sky backgrounds and magic sparkles / Luna's mane stars respectively.
# This script consolidates them both and was written for generating Nightmare Rarity's mane stars, which are astroids.
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import random, sys
rgen = random.SystemRandom()
from math import log, pi
from kinback.miscellanea import xmlprettyprint, svgnms
import xml.etree.ElementTree as t
for n in svgnms: t.register_namespace(n, svgnms[n])
sdpns = "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}"

def baseisstar(): return base.tag == "path" and base.get(sdpns + "type") == "star"
def nextspall():
    dt = base.attrib.copy()
    if distro[0] == 'g':
        # Geometric distribution with p = 1 - 1 / distro[1] up to distro[2].
        # This is equivalent to flooring an exponential distribution with lambda = -ln(1 - p) and taking minimums.
        # distro[1] is called the decay rate (how less frequent stars of the next larger magnitude are) and distro[2] is the maximum magnitude.
        variate = min(int(rgen.expovariate(gparam)), int(distro[2]))
    if base.tag == "circle":
        dt["r"] = str(float(dt["r"]) + float(distro[-1]) * variate)
        dt["cx"], dt["cy"] = str(round(rgen.random() * width, 3)), str(round(rgen.random() * height, 3))
        return t.Element("circle", dt)
    elif baseisstar():
        outr, inr = float(dt[sdpns + "r1"]), float(dt[sdpns + "r2"])
        srat = inr / outr
        outr += float(distro[-1]) * variate
        inr = outr * srat
        dt[sdpns + "r1"], dt[sdpns + "r2"] = str(round(outr, 3)), str(round(inr, 3))
        if spins:
            delta = 2 * pi * rgen.random() / int(dt[sdpns + "sides"])
            dt[sdpns + "arg1"] = str(round(float(dt[sdpns + "arg1"]) + delta, 9))
            dt[sdpns + "arg2"] = str(round(float(dt[sdpns + "arg2"]) + delta, 9))
        dt[sdpns + "cx"], dt[sdpns + "cy"] = str(round(rgen.random() * width, 3)), str(round(rgen.random() * height, 3))
        return t.Element("path", dt)
    elif base.tag == "path": # TODO bounding box size?
        dt["transform"] = "translate({},{})scale({})".format(str(round(rgen.random() * width, 3)), str(round(rgen.random() * height, 3)), 1 + variate / 4)
        return t.Element("path", dt)

if len(sys.argv) != 3:
     print("Usage: {} [file] [params]\nSee the documentation for details.".format(sys.argv[0]))
     sys.exit(1)
rn, vard = t.parse(sys.argv[1]).getroot(), sys.argv[2].split(";")
base, width, height = rn[0], float(rn.get("width", "1000")), float(rn.get("height", "1000"))
distro, spins = vard[1].split(), bool(vard[2])
# Density is a relative measure of how many objects are put into a 1000-by-1000 square: 250 objects = 1, 500 = 2, etc.
# This corresponds to the old circle-starfield default behaviour; the aforementioned object count is width * height * ("effective radius") ^ 2 / 49000.
# The effective radius for circles and stars is the average of their two radii.
density = float(vard[0]) if vard[0] else 1
if base.tag == "circle": er = float(base.get("r"))
elif baseisstar(): er = (float(base.get(sdpns + "r1")) + float(base.get(sdpns + "r2"))) / 2
elif base.tag == "path": er = 8 # TODO this is for the astroid only
N = round(width * height * er * er * density / 49000)
try: gparam = log(float(distro[1]))
except ValueError: gparam = 1.0986123 # equivalent to a decay rate of 3

outrn = t.Element("svg")
for q in range(N): outrn.append(nextspall())
with open("spallated.svg", 'w') as out: out.write(xmlprettyprint(t.ElementTree(outrn)))

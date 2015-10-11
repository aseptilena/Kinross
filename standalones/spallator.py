#!/usr/bin/env python3.5
# "Spallates" an input object on a canvas, generating a random pattern according to given variability data.
# The circle and star templates included match the behaviour of the old circle-starfield and star-starfield scripts,
# being used to generate MLPFIM starry sky backgrounds and magic sparkles / Luna's mane stars respectively.
# This script consolidates them both and was written for generating Nightmare Rarity's mane stars, which are astroids.
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import random, sys
rgen = random.SystemRandom()
from math import log
from kinback.miscellanea import xmlprettyprint, svgnms
import xml.etree.ElementTree as t
for n in svgnms: t.register_namespace(n, svgnms[n])
sdpns = "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}"

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

if len(sys.argv) != 3: # The file should be like <svg height="" width="" ...><object/></svg>, dimensions defaulting to 1000.
     print("Usage: {} [file] [params]\nSee the documentation for details.".format(sys.argv[0]))
     sys.exit(1)
rn, vard = t.parse(sys.argv[1]).getroot(), sys.argv[2].split(";") # "0.777;g 2.5 4 5;y" matches star-starfield
base, width, height = rn[0], float(rn.get("width", "1000")), float(rn.get("height", "1000"))
distro, turn = vard[1].split(), bool(vard[2])
# The density is a relative measure of how many objects are put into a 1000-by-1000 square, with 250 objects as 1, 500 as 2 and so on.
# This corresponds to the old circle-starfield default behaviour; the aforementioned object count is width * height * ("effective radius") ^ 2 / 49000.
# The effective radius for circles, ellipses and stars is the average of their two radii.
density = float(vard[0]) if vard[0] else 1
if base.tag == "circle": er = float(base.get("r"))
elif base.tag == "ellipse": er = (float(base.get("rx")) + float(base.get("ry"))) / 2
elif base.tag == "path" and base.get(sdpns + "type") == "star": er = (float(base.get(sdpns + "r1")) + float(base.get(sdpns + "r2"))) / 2
N = round(width * height * er * er * density / 49000)

try: gparam = log(float(distro[1]))
except ValueError: gparam = 1.0986123 # equivalent to a decay rate of 3

outrn = t.Element("svg")
for q in range(N): outrn.append(nextspall())
with open("spallated.svg", 'w') as out: out.write(xmlprettyprint(t.ElementTree(outrn)))

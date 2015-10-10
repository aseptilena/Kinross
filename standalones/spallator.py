#!/usr/bin/env python3.5
# "Spallates" an input object on a canvas, generating a random pattern with a specified density. Scaling and rotation may also be specified.
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import random, sys
rgen = random.SystemRandom()
from kinback.miscellanea import xmlprettyprint, svgnms
import xml.etree.ElementTree as t
for n in svgnms: t.register_namespace(n, svgnms[n])
# The file should be like <svg height="" width="" ...><object/></svg>, dimensions defaulting to 1000.
if len(sys.argv) != 3:
     print("Usage: {} [file] [params]\nSee the documentation for details.".format(sys.argv[0]))
     sys.exit(1)
rn, vard = t.parse(sys.argv[1]).getroot(), sys.argv[2].split(";")
# Variability data: ";g 3 5 1.5;" matches circle-starfield
#                   "0.777;g 2.5 4 5;y" matches star-starfield
base, width, height = rn[0], rn.get("width", "1000"), rn.get("height", "1000")
# The density is a relative measure of how many objects are put into a 1000-by-1000 square, with 250 objects as 1 ("medium"), 500 as 2 ("dense") and so on.
# This corresponds to the old circle-starfield default behaviour; the aforementioned object count is width * height * "effective radius" / 14000.
# The effective radius for circles, ellipses and stars is the average of their two radii.
density = float(vard[0]) if vard[0] else 1
# Effective radius calculation
if base.tag == "circle": er = float(base.get("r"))
elif base.tag == "ellipse": er = (float(base.get("rx")) + float(base.get("ry"))) / 2
elif base.tag == "path" and base.get("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}type") == "star":
    er = (float(base.get("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}r1")) + float(base.get("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}r2"))) / 2
N = round(float(width) * float(height) * er * density / 14000)
print(N)
# TODO

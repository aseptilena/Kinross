#!/usr/bin/env python
# When given an ellipse, prints the two foci as a line
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from __future__ import division
import sys, inkex, gettext, math
sys.path.append('/usr/share/inkscape/extensions')
def pout(t): sys.exit((gettext.gettext(t)))

class root(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

    def effect(self):
        if len(self.selected) == 0: pout("Please select at least one ellipse.")
        for obj in self.selected:
            curr = self.selected[obj]
            x, y, a, b = float(curr.get("cx")), float(curr.get("cy")), float(curr.get("rx")), float(curr.get("ry"))
            d = math.sqrt(max(a, b) ** 2 - min(a, b) ** 2)
            dstring = "M{0} {1}{2}{3}".format(x - d * (a >= b), y - d * (a <= b), 'h' if a > b else 'v', 2 * d)
            attribs = {'style': curr.get("style"), 'd': dstring, 'transform': curr.get("transform")}
            inkex.etree.SubElement(curr.getparent(), inkex.addNS('path','svg'), attribs)

final = root()
final.affect()

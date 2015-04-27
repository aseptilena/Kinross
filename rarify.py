#!/usr/bin/env python3.4
# Rarify: an Inkscape vector file cleanup program
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
#
# P.S. Might want to streamline the code in the future.

import sys
import xml.etree.ElementTree as t

r = {"d": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}

# This kills attributes:
# if in file f any node n has attribute a (optionally with value v)
# then kill attribute e (a if not given, optionally only if e/a has value w).
def kill(f, n, a, e = None, v = None, w = None):
    l = e if e else a
    tmp = l.partition(":")
    p, q = tmp[0], tmp[2]
    k = f.findall(".//{0}[@{1}{2}]".format((n if ':' in n else "d:" + n) if n else "*", a, "='{0}'".format(v) if v else ""), r)
    for i in k:
        z = p if q == "" else "{{{0}}}{1}".format(r[p], q)
        if w == None or i.attrib[z] == w: del i.attrib[z]

# Default values for style attributes, can be whacko'd.
ddv = [["", ""],
       ["display", "inline"],
       ["overflow", "visible"],
       ["visibility", "visible"],
       ["isolation", "auto"],
       ["mix-blend-mode", "normal"],
       ["color-interpolation", "sRGB"],
       ["color-interpolation-filters", "linearRGB"],
       ["color-rendering", "auto"],
       ["paint-color-rendering", "auto"],
       ["paint-order", "normal"],
       ["image-rendering", "auto"],
       ["shape-rendering", "auto"],
       ["text-rendering", "auto"],
       ["clip-rule", "nonzero"],
       ["color", "black"],
       ["color", "#000000"],
       ["color", "#000"],
       ["solid-color", "black"],
       ["solid-color", "#000000"],
       ["solid-color", "#000"],
       ["solid-opacity", "1"],
       ["opacity", "1"],
       ["fill-opacity", "1"],
       ["fill-rule", "nonzero"],
       ["stroke-opacity", "1"],
       ["stroke-width", "1"],
       ["stroke-linecap", "butt"],
       ["stroke-linejoin", "miter"],
       ["stroke-miterlimit", "4"],
       ["stroke-dasharray", "none"],
       ["stroke-dashoffset", "0"],
       ["enable-background", "accumulate"],
       ["-inkscape-font-specification", "Sans"],
       ["marker", "none"],
       ["marker-start", "none"],
       ["marker-mid", "none"],
       ["marker-end", "none"]]

def stylewhack(o):
    om = {}
    m = o.get("style").split(";")
    for j in m:
        n = j.partition(":")
        om[n[0]] = n[2]
    def ifrm(a, b = None):
        if a in om and (b == om[a] or b == None): del om[a]
    def testrm(a, b):
        return a not in om or om[a] == b
    
    for d in ddv:
        ifrm(d[0], d[1])
    if testrm("stroke", "none"):
        ifrm("stroke-dashoffset")
        ifrm("stroke-dasharray")
        ifrm("stroke-opacity")
        ifrm("stroke-width")
        ifrm("stroke-linecap")
        ifrm("stroke-linejoin")
        ifrm("stroke-miterlimit")
        ifrm("stroke")
    if testrm("stroke-dasharray", "none"):
        ifrm("stroke-dashoffset")
        ifrm("stroke-dasharray")
    if len(om) == 0: del o.attrib["style"]
    elif len(om) < 4:
        del o.attrib["style"]
        for a in om: o.set(a, om[a])
    else: o.set("style", ";".join([a + ":" + om[a] for a in om]))

def rarify(st, fn):
    b = st.getroot()
    kill(b, "path", "inkscape:original-d", e = "d")
    kill(b, "", "inkscape:connector-curvature", v = "0")
    kill(b, "path", "sodipodi:nodetypes")
    
    kill(b, "path", "sodipodi:type", v = "star", e = "d")
    kill(b, "path", "sodipodi:type", v = "star", e = "inkscape:rounded", w = "0")
    kill(b, "path", "sodipodi:type", v = "star", e = "inkscape:randomized", w = "0")
    
    kill(b, "use", "x", v = "0")
    kill(b, "use", "y", v = "0")
    kill(b, "use", "height", v = "100%")
    kill(b, "use", "width", v = "100%")
    
    kill(b, "inkscape:path-effect", "is_visible", v = "true")
    kill(b, "inkscape:path-effect", "miter_limit", v = "4")
    kill(b, "inkscape:path-effect", "linejoin_type", v = "extrp_arc")
    kill(b, "inkscape:path-effect", "sort_points", v = "true")
    kill(b, "inkscape:path-effect", "interpolator_beta", v = "0.2")
    
    kill(b, "clipPath", "clipPathUnits", v = "userSpaceOnUse")
    for nv in b.findall("sodipodi:namedview", r): nv.clear()
    for o in b.findall(".//*[@style]", r): stylewhack(o)
    st.write("{0}-rarified.svg".format(fn[:-4]))

if len(sys.argv) == 1:
    print("Usage: " + sys.argv[0] + " [list of files in same directory separated by spaces]")
    sys.exit(1)
t.register_namespace("","http://www.w3.org/2000/svg")
t.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
t.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
t.register_namespace("xlink", "http://www.w3.org/1999/xlink")
t.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
t.register_namespace("cc", "http://creativecommons.org/ns#")
t.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
for f in sys.argv[1:]: rarify(t.parse(f), f)

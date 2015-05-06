#!/usr/bin/env python3.4
# Rarify: an Inkscape vector file cleanup program
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import sys
import xml.etree.ElementTree as t

tr, rn = None, None
nm = {"d": "http://www.w3.org/2000/svg",
      "inkscape": "http://www.inkscape.org/namespaces/inkscape",
      "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}
sd = {"display": "inline", # CSS/SVG properties and Inkscape's assumed values
      "overflow": "visible",
      "visibility": "visible",
      "isolation": "auto",
      "enable-background": "accumulate",
      # Fill and stroke
      "opacity": "1",
      "solid-opacity": "1",
      "fill": "#000",
      "fill-opacity": "1",
      "fill-rule": "nonzero",
      "stroke": "none",
      "stroke-opacity": "1",
      "stroke-width": "1",
      "stroke-linecap": "butt",
      "stroke-linejoin": "miter",
      "stroke-miterlimit": "4",
      "stroke-dasharray": "none",
      "stroke-dashoffset": "0",
      # Filters and gradients
      "filter": "none",
      "flood-color": "#000",
      "flood-opacity": "1",
      "lighting-color": "#fff",
      "stop-color": "#000",
      "stop-opacity": "1",
      # Advanced colouring
      "mix-blend-mode": "normal",
      "color-interpolation": "sRGB",
      "color-interpolation-filters": "linearRGB",
      "color-rendering": "auto",
      "paint-color-rendering": "auto",
      "paint-order": "normal",
      "image-rendering": "auto",
      "shape-rendering": "auto",
      "text-rendering": "auto",
      # Markers
      "marker": "none",
      "marker-start": "none",
      "marker-mid": "none",
      "marker-end": "none",
      # Clips and masks
      "clip-path": "none",
      "clip-rule": "nonzero",
      "mask": "none",
      # Text
      "font-size": "12px",
      "font-style": "normal",
      "font-variant": "normal",
      "font-stretch": "normal",
      "line-height": "125%",
      "letter-spacing": "0px",
      "word-spacing": "0px",
      "text-align": "start",
      "writing-mode": "lr-tb",
      "text-anchor": "start",
      "font-family": "Sans",
      "-inkscape-font-specification": "Sans"}
si = [["stroke-dasharray", "stroke-dashoffset"],
      ["stroke", "stroke-opacity", "stroke-width", "stroke-linejoin", "stroke-linecap", "stroke-miterlimit", "stroke-dasharray", "stroke-dashoffset"]]
      
def expand(a): return a if ":" not in a else "{{{0}}}{1}".format(nm[a[:a.index(":")]], a[a.index(":") + 1:])

# Function for removing redundant/implied attributes.
# Selector string format is A|(B)|C(|D): if some element A has all attribute pairs in B and any in C then remove all those in D (C if D not given).
def kill(s):
    params = s.split("|")
    a = params[0]
    b = dict([i.split("=") for i in params[1].split(",")]) if params[1] != "" else {}
    c = dict([i.split("=") for i in params[2].split(",")])
    d = dict([i.split("=") for i in params[3].split(",")]) if len(params) == 4 else {}
    e = list(c)
    bb = ".//" + (a if ':' in a or a == "*" else "d:" + a) + "".join(["[@{0}{1}]".format(i, "='{0}'".format(b[i]) if b[i] != "*" else "") for i in b])
    sl = [bb + "[@{0}{1}]".format(i, "='{0}'".format(c[i]) if c[i] != "*" else "") for i in c]
    for i in range(len(c)):
        rs = rn.findall(sl[i], nm)
        for j in rs:
            if len(d) == 0:
                if c[e[i]] == "*" or j.attrib[expand(e[i])] == c[e[i]]: del j.attrib[expand(e[i])]
            else:
                for k in d:
                    if d[k] == "*" or j.attrib[expand(k)] == d[k]: del j.attrib[expand(k)]

# Collect styling properties, optimise colour descriptors, kill as if they were attributes and split if it saves a few bytes.
def styler():
    om = {}
    def imply(a):
        if a in om and om[a] == sd[a]: del om[a]
    for a in sd:
        for i in rn.findall(".//*[@{0}]".format(a), nm):
            i.set("style", a + ":" + i.get(a) + ";" + i.get("style", ""))
            del i.attrib[a]
    for n in rn.findall(".//*[@style]", nm):
        rw = n.get("style").split(";")
        for i in range(rw.count("")): rw.remove("")
        om = dict([(a[:a.index(":")], a[a.index(":") + 1:]) for a in rw])
        # TODO colour normalisation
        for s in si:
            if s[0] not in om or om[s[0]] == sd[s[0]]:
                for a in s:
                    if a in om: del om[a]
        for a in sd:
            if a in om and om[a] == sd[a]: del om[a]
        if len(om) < 1: del n.attrib["style"]
        elif len(om) < 4:
            del n.attrib["style"]
            for a in om: n.set(a, om[a])
        else: n.set("style", ";".join([a + ":" + om[a] for a in om]))

def rarify(f):
    kill("path||inkscape:original-d=*|d=*")
    kill("*||inkscape:connector-curvature=0")
    kill("path||sodipodi:nodetypes=*")
    
    kill("path||sodipodi:type=star|d=*,inkscape:rounded=0,inkscape:randomized=0")
    kill("use||x=0,y=0,height=100%,width=100%")
    kill("inkscape:path-effect|effect=powerstroke|is_visible=true,miter_limit=4,linejoin_type=extrp_arc,sort_points=true,interpolator_beta=0.2")
    
    kill("clipPath||clipPathUnits=userSpaceOnUse")
    # Deleting the namedview tag causes Inkscape to fail to load larger SVGs correctly on LPEs, hence the clear command. See ...
    for nv in rn.findall("sodipodi:namedview", nm): nv.clear()
    styler()
    tr.write("{0}-rarified.svg".format(f[:-4]))

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
for f in sys.argv[1:]:
    tr = t.parse(f)
    rn = tr.getroot()
    rarify(f)

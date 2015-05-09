#!/usr/bin/env python3.4
# Rarify: an Inkscape vector file cleanup program
# Parcly Taxel / Jeremy Tan, 2015
import sys
import xml.etree.ElementTree as t

tr, rn = None, None
nm = {"d": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}
sd = {"display": "inline", "overflow": "visible", "visibility": "visible", "isolation": "auto", "enable-background": "accumulate",
      # Fill, stroke and markers
      "opacity": "1", "solid-opacity": "1", "fill": "#000", "fill-opacity": "1", "fill-rule": "nonzero",
      "stroke": "none", "stroke-opacity": "1", "stroke-width": "1", "stroke-linecap": "butt", "stroke-linejoin": "miter", "stroke-miterlimit": "4", "stroke-dasharray": "none", "stroke-dashoffset": "0",
      "marker": "none", "marker-start": "none", "marker-mid": "none", "marker-end": "none",
      # Filters and gradients
      "filter": "none", "flood-color": "#000", "flood-opacity": "1", "lighting-color": "#fff", "stop-color": "#000", "stop-opacity": "1",
      # Miscellaneous colouring
      "color-interpolation": "sRGB", "color-interpolation-filters": "linearRGB", "color-rendering": "auto", "paint-color-rendering": "auto", "paint-order": "normal", "mix-blend-mode": "normal", "image-rendering": "auto", "shape-rendering": "auto", "text-rendering": "auto",
      # Clips and masks
      "clip-path": "none", "clip-rule": "nonzero", "mask": "none",
      # Text
      "font-size": "12px", "font-style": "normal", "font-variant": "normal", "font-stretch": "normal", "line-height": "125%", "letter-spacing": "0px", "word-spacing": "0px", "text-align": "start", "writing-mode": "lr-tb", "text-anchor": "start", "font-family": "Sans", "-inkscape-font-specification": "Sans"}
si = [["stroke-dasharray", "stroke-dashoffset"],
      ["stroke", "stroke-opacity", "stroke-width", "stroke-linejoin", "stroke-linecap", "stroke-miterlimit", "stroke-dasharray", "stroke-dashoffset"]]
cm = {"#000000": "#000", "black": "#000", "#ffffff": "#fff", "white": "#fff",
      "#ff0000": "red", "#f00": "red", "#00ff00": "#0f0", "lime": "#0f0", "#0000ff": "#00f", "blue": "#00f",
      "#ffff00": "#ff0", "yellow": "#ff0", "#ff00ff": "#f0f", "magenta": "#f0f", "fuchsia": "f0f", "#00ffff": "#0ff", "cyan": "#0ff", "aqua": "#0ff",
      "808080": "grey", "gray": "grey",
      "#800000": "maroon", "#008000": "green", "#000080": "navy",
      "#808000": "olive", "#800080": "purple", "#008080": "teal"}

# Dictionary pair remover for kill and styler.
# s = (A)|B(|C); if d has A's pairs and any of B's delete C's (B if empty).
def expand(a): return a if ":" not in a else "{{{0}}}{1}".format(nm[a[:a.index(":")]], a[a.index(":") + 1:])
def dicrem(d, s):
    p = s.split("|")
    a = dict([i.split("=") for i in p[0].split(",")]) if p[0] != "" else {}
    b = dict([i.split("=") for i in p[1].split(",")])
    c = dict([i.split("=") for i in p[2].split(",")]) if len(p) == 3 else {}
    x = True if not a else min([expand(e) in d and a[e] in (d[expand(e)], "*") for e in a])
    y = max([expand(e) in d and b[e] in (d[expand(e)], "*") for e in b])
    if x and y:
        v = c if c else b
        for k in v:
            if expand(k) in d and v[k] in (d[expand(k)], "*"): del d[expand(k)]

# Function for removing redundant/implied attributes; exploits the fact that elements' attributes come in a dictionary.
# Selector string format is E|S where E is a path to the attribute and S is the string to be passed to dicrem.
def kill(s):
    r = s.partition("|")
    rs = rn.findall(".//" + (r[0] if ':' in r[0] or r[0] == "*" else "d:" + r[0]), nm)
    for j in rs: dicrem(j.attrib, r[2])

# Collect styling properties, optimise colour descriptors, kill as if they were attributes and split if it saves a few bytes.
def styler():
    om = {}
    for a in sd:
        for i in rn.findall(".//*[@{0}]".format(a), nm):
            i.set("style", a + ":" + i.get(a) + ";" + i.get("style", ""))
            del i.attrib[a]
    for n in rn.findall(".//*[@style]", nm):
        rw = n.get("style").split(";")
        for i in range(rw.count("")): rw.remove("")
        om = dict([(a[:a.index(":")], a[a.index(":") + 1:]) for a in rw])
        for c in ["fill", "stroke", "stop-color", "flood-color", "lighting-color", "color"]:
            if c in om and om[c] in cm: om[c] = cm[om[c]]
        for s in si:
            if s[0] not in om: om[s[0]] = sd[s[0]]
            dicrem(om, "|{0}|{1}".format(s[0] + "=" + sd[s[0]], ",".join([a + "=*" for a in s])))
        for a in sd: dicrem(om, "|{0}={1}".format(a, sd[a]))
        if len(om) < 1: del n.attrib["style"]
        elif len(om) < 4:
            del n.attrib["style"]
            for a in om: n.set(a, om[a])
        else: n.set("style", ";".join([a + ":" + om[a] for a in om]))

def rarify(f):
    kill("path||inkscape:original-d=*|d=*")
    kill("*||inkscape:connector-curvature=0")
    kill("*||sodipodi:nodetypes=*")
    
    kill("rect||x=0,y=0")
    kill("circle||cx=0,cy=0")
    kill("ellipse||cx=0,cy=0")
    kill("path||sodipodi:type=star|d=*,inkscape:rounded=0,inkscape:randomized=0,inkscape:flatsided=false")
    kill("use||x=0,y=0,height=100%,width=100%")
    
    kill("inkscape:path-effect||is_visible=true")
    kill("inkscape:path-effect|effect=powerstroke|miter_limit=4,linejoin_type=extrp_arc,sort_points=true,interpolator_beta=0.2,start_linecap_type=butt,end_linecap_type=butt")
    
    kill("clipPath||clipPathUnits=userSpaceOnUse")
    # kill("clipPath/path||!d=*,X=Y,!Z=W"): if clipPath/path contains something NOT d=*, something X=Y or something NOT Z=W
    # then delete the attribs that are not d=*, those not Z=W, those X=Y 
    kill("mask||maskUnits=userSpaceOnUse")
    kill("*||inkscape:collect=always")
    
    dicrem(rn.attrib, "|version=*,inkscape:version=*,sodipodi:docname=*,inkscape:export-filename=*,inkscape:export-xdpi=*,inkscape:export-ydpi=*")
    for nv in rn.findall("sodipodi:namedview", nm): nv.clear() # Deleting namedview breaks SVGs with LPEs; see (bug goes here).
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

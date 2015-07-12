#!/usr/bin/env python3.4
# Rarify: an Inkscape vector file cleanup program
# Parcly Taxel / Jeremy Tan, 2015
import sys
import xml.etree.ElementTree as t

tr, rn = None, None
nm = {"d": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}
sd = {"display": "inline", "overflow": "visible", "visibility": "visible", "isolation": "auto", "enable-background": "accumulate",
      # Fill, stroke and markers
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
      "marker": "none",
      "marker-start": "none",
      "marker-mid": "none",
      "marker-end": "none",
      # Filters and gradients
      "filter": "none",
      "flood-color": "#000",
      "flood-opacity": "1",
      "lighting-color": "#fff",
      "stop-color": "#000",
      "stop-opacity": "1",
      # Miscellaneous colouring
      "color": "#000",
      "solid-color": "#000",
      "color-interpolation": "sRGB",
      "color-interpolation-filters": "linearRGB",
      "color-rendering": "auto",
      "paint-color-rendering": "auto",
      "paint-order": "normal",
      "mix-blend-mode": "normal",
      "image-rendering": "auto",
      "shape-rendering": "auto",
      "text-rendering": "auto",
      # Clips and masks
      "clip-path": "none",
      "clip-rule": "nonzero",
      "mask": "none",
      # Text
      "font-size": "12px;medium",
      "font-style": "normal",
      "font-variant": "normal",
      "font-stretch": "normal",
      "font-weight": "normal",
      "line-height": "125%;normal",
      "letter-spacing": "0px",
      "word-spacing": "0px;normal",
      "text-align": "start",
      "direction": "ltr",
      "writing-mode": "lr-tb",
      "block-progression": "tb",
      "baseline-shift": "baseline",
      "text-anchor": "start",
      "text-decoration-line": "none",
      "font-variant-ligatures": "normal",
      "text-decoration-style": "solid",
      "font-variant-position": "normal",
      "font-variant-numeric": "normal",
      "font-variant-alternates": "normal",
      "font-variant-caps": "normal",
      "baseline-shift": "baseline",
      "white-space": "normal",
      "shape-padding": "0",
      "text-indent": "0",
      "text-decoration": "none",
      "text-decoration-color": "#000",
      "text-transform": "none",
      "letter-spacing": "normal",
      "font-feature-settings": "normal",
      "font-family": "Sans;sans-serif",
      "-inkscape-font-specification": "Sans"}
si = [["stroke-dasharray", "stroke-dashoffset"],
      ["stroke", "stroke-opacity", "stroke-width", "stroke-linejoin", "stroke-linecap", "stroke-miterlimit", "stroke-dasharray", "stroke-dashoffset"]]
cm = {"#000000": "#000", "black": "#000", "#ffffff": "#fff", "white": "#fff",
      "#ff0000": "red", "#f00": "red", "#00ff00": "#0f0", "lime": "#0f0", "#0000ff": "#00f", "blue": "#00f",
      "#ffff00": "#ff0", "yellow": "#ff0", "#ff00ff": "#f0f", "magenta": "#f0f", "fuchsia": "f0f", "#00ffff": "#0ff", "cyan": "#0ff", "aqua": "#0ff",
      "808080": "grey", "gray": "grey",
      "#800000": "maroon", "#008000": "green", "#000080": "navy",
      "#808000": "olive", "#800080": "purple", "#008080": "teal"}

def expand(a): return a if ":" not in a else "{{{0}}}{1}".format(nm[a[:a.index(":")]], a[a.index(":") + 1:])
def collapse(a):
    z = a.partition("}")
    for m in nm:
        if nm[m] == z[0][1:]: return (m + ":" if m != "d" else "") + z[2]
    return a

# Dictionary pair remover for kill and styler. s = (A)|B(|C); if d has A's pairs and any of B's delete C's (B if empty).
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
# Input to function below is E|S where E is a path to the attribute and S is the string to be passed to dicrem.
def kill(s):
    r = s.partition("|")
    rs = rn.findall(".//" + (r[0] if ':' in r[0] or r[0] == "*" else "d:" + r[0]), nm)
    for j in rs: dicrem(j.attrib, r[2])

def gets(k):
    rw = k.get("style", "").split(";")
    for i in range(rw.count("")): rw.remove("")
    return dict([(a[:a.index(":")], a[a.index(":") + 1:]) for a in rw])

def rarify(f):
    # Phase 1: node and attribute removals
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
    kill("mask||maskUnits=userSpaceOnUse")

    kill("*||inkscape:collect=always,inkscape:transform-center-x=*,inkscape:transform-center-y=*")
    dicrem(rn.attrib, "|version=*,inkscape:version=*,sodipodi:docname=*,inkscape:export-filename=*,inkscape:export-xdpi=*,inkscape:export-ydpi=*")
    for nv in rn.findall("sodipodi:namedview", nm): rn.remove(nv)
    # Phase 2: style property removals
    om = {}
    for a in sd:
        for i in rn.findall(".//*[@{0}]".format(a), nm):
            i.set("style", a + ":" + i.get(a) + ";" + i.get("style", ""))
            del i.attrib[a]
    # It is safe to remove all style save clip-rule from clips. Not for masks though.
    for n in rn.findall(".//d:clipPath/d:path", nm):
        om = gets(n)
        if om:
            for a in sd:
                if a != "clip-rule": dicrem(om, "|{0}=*".format(a))
            if len(om) < 1: del n.attrib["style"]
            else: n.set("style", ";".join([a + ":" + om[a] for a in om]))
    for n in rn.findall(".//*[@style]", nm):
        om = gets(n)
        # Colour simplification
        for c in ["fill", "stroke", "stop-color", "flood-color", "lighting-color", "color", "solid-color", "text-decoration-color"]:
            if c in om and om[c] in cm: om[c] = cm[om[c]]
        # Lack of some attributes wastes others; remove if applicable
        for s in si:
            if s[0] not in om: om[s[0]] = sd[s[0]]
            dicrem(om, "|{0}|{1}".format(s[0] + "=" + sd[s[0]], ",".join([a + "=*" for a in s])))
        # Removal of default-valued attributes
        for a in sd:
            bore = sd[a].split(";")
            for sa in bore: dicrem(om, "|{0}={1}".format(a, sa))
        # stroke-linejoin = round/bevel: stroke-miterlimit wasted
        # TODO
        
        if len(om) < 1: del n.attrib["style"]
        elif len(om) < 4:
            del n.attrib["style"]
            for a in om: n.set(a, om[a])
        else: n.set("style", ";".join([a + ":" + om[a] for a in om]))
    # Phase 3: unused definitions and redundant ID removal
    # 3a: dictionary of all elements and their references (assign temporary IDs to those lacking it)
    rd, cnt = {}, 0
    for k in rn.findall(".//*"):
        if not("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}" in k.tag or 
               "{http://creativecommons.org/ns#}" in k.tag or
               "{http://purl.org/dc/elements/1.1/}" in k.tag):
            rf, sty = {}, gets(k)
            for a in ["fill", "stroke", "clip-path", "mask", "filter"]:
                rf[a] = k.get(a, "")
                if a in sty: rf[a] = sty[a]
                rf[a] = rf[a][5:-1] if rf[a].startswith("url(#") else None
            rf["tag"] = collapse(k.tag)
            tmp = k.get("{http://www.w3.org/1999/xlink}href")
            rf["use"] = tmp[1:] if tmp != None else None
            tmp = k.get("{http://www.inkscape.org/namespaces/inkscape}path-effect")
            rf["path-effect"] = tmp[1:] if tmp != None else None
            rf["transform"] = k.get("transform")
            irk = k.get("id")
            if irk == None:
                while "q" + str(cnt) in rd: cnt += 1
                irk = "q" + str(cnt)
                k.set("id", irk)
            rd[irk] = rf
    # 3b: reference tree flattening TODO
    # 3c: removal of unused <defs> TODO
    # 3d: unreferenced ID removal
    ao, ro = set(rd.keys()), []
    for e in rd: ro.extend([rd[e][a] for a in ["use", "fill", "stroke", "clip-path", "mask", "filter", "path-effect"]])
    for rm in ao - set(ro):
        fat = rn.find(".//*[@id='{0}']".format(rm), nm)
        del fat.attrib["id"]
    if rn.get("id") != None: del rn.attrib["id"]
    # Final output
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

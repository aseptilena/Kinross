#!/usr/bin/env python3.4
# Rarify, the uncouth SVG optimiser
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import sys, argparse
import xml.etree.ElementTree as t

from kinback.ellipse import *
from kinback.affinity import *

tr, rn = None, None
nm = {"d": "http://www.w3.org/2000/svg",
      "inkscape": "http://www.inkscape.org/namespaces/inkscape",
      "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}
# Default styling attributes, as defined by the SVG specifications and Inkscape's default parameters
defstyle = {"display": "inline",
            "overflow": "visible",
            "visibility": "visible",
            "isolation": "auto",
            "enable-background": "accumulate",
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
            "color-interpolation": "sRGB",
            "color-interpolation-filters": "linearRGB",
            "color-rendering": "auto",
            "image-rendering": "auto",
            "mix-blend-mode": "normal",
            "paint-color-rendering": "auto",
            "paint-order": "normal",
            "shape-rendering": "auto",
            "solid-color": "#000",
            "text-rendering": "auto",
            # Clips and masks
            "clip-path": "none",
            "clip-rule": "nonzero",
            "mask": "none",
            # Text
            "baseline-shift": "baseline",
            "block-progression": "tb",
            "direction": "ltr",
            "font-family": "Sans",
            "font-feature-settings": "normal",
            "font-size": "medium",
            "font-stretch": "normal",
            "font-style": "normal",
            "font-variant": "normal",
            "font-variant-alternates": "normal",
            "font-variant-caps": "normal",
            "font-variant-ligatures": "normal",
            "font-variant-numeric": "normal",
            "font-variant-position": "normal",
            "font-weight": "normal",
            "letter-spacing": "normal",
            "line-height": "125%",
            "shape-padding": "0",
            "text-align": "start",
            "text-anchor": "start",
            "text-decoration": "none",
            "text-decoration-color": "#000",
            "text-decoration-line": "none",
            "text-decoration-style": "solid",
            "text-indent": "0",
            "text-transform": "none",
            "white-space": "normal",
            "word-spacing": "normal",
            "writing-mode": "lr-tb",
            "-inkscape-font-specification": "Sans"}
# The key for each pair precludes itself and the properties in the corresponding value, hence the name.
precld = {"stroke-dasharray": ["stroke-dashoffset"],
          "stroke": ["stroke-opacity", "stroke-width", "stroke-linejoin", "stroke-linecap", "stroke-miterlimit", "stroke-dasharray", "stroke-dashoffset"]}
# Colour aliases
calias = {"#000000": "#000", "black": "#000",
          "#ffffff": "#fff", "white": "#fff",
          "#ff0000": "red", "#f00": "red",
          "#00ff00": "#0f0", "lime": "#0f0",
          "#0000ff": "#00f", "blue": "#00f",
          "#ffff00": "#ff0", "yellow": "#ff0",
          "#ff00ff": "#f0f", "magenta": "#f0f", "fuchsia": "#f0f",
          "#00ffff": "#0ff", "cyan": "#0ff", "aqua": "#0ff",
          "#808080": "grey", "gray": "grey",
          "#800000": "maroon", "#008000": "green", "#000080": "navy",
          "#808000": "olive", "#800080": "purple", "#008080": "teal",
          
          "#ffa500": "orange", "#ffc0cb": "pink", "#a52a2a": "brown",
          "#c0c0c0": "silver", "#ffd700": "gold", "#f5f5dc": "beige",
          "#4b0082": "indigo", "#ee82ee": "violet", "#dda0dd": "plum"}

# Functions converting namespaces into URLs and vice versa
def expand(a): return a if ":" not in a else "{{{0}}}{1}".format(nm[a[:a.index(":")]], a[a.index(":") + 1:])
def collapse(a):
    z = a.partition("}")
    for m in nm:
        if nm[m] == z[0][1:]: return (m + ":" if m != "d" else "") + z[2]
    return a
# Dictionary match-and-remove with namespaces.
# Input pairs to remove as dictionary and prefix keys with ! to remove non-matchings.
# e.g. {"!this": "that"} removes this if it isn't that
#      {"![attribute]": None} doesn't do anything (remove if value is no thing)
# cond gives pairs all conditional for pr to take effect.
# As with the pairs for removal, !-prefixing indicates negation.
# e.g. {"d": None} stipulates that an attribute d has to be present
#      {"!stroke-linejoin": "miter"} requires stroke-linejoin to not be miter (and exist)
#      {![attribute]: None} is a premature break
def dmrn(d, pr, cond = {}):
    rute = True
    for c in cond:
        negate, term = c[0] == '!', c.lstrip("!")
        rute &= expand(term) in d and negate ^ (cond[c] in (d[expand(term)], None))
    if rute:
        for p in pr:
            negate, term = p[0] == '!', p.lstrip("!")
            if expand(term) in d and negate ^ (pr[p] in (d[expand(term)], None)): del d[expand(term)]
# The declutterer of XML nodes! * for tag matches any node.
def dclt(tag, pr, cond = {}):
    rs = rn.findall(".//" + (tag if ':' in tag or tag == "*" else "d:" + tag), nm)
    for j in rs: dmrn(j.attrib, pr, cond)

def rarify(f, opts):
    # Phase 1: attribute decluttering
    # Paths
    dclt("path", {"d": None}, {"inkscape:original-d": None}) # This is the very reason this script was written
    dclt("*", {"inkscape:connector-curvature": "0"})
    dclt("*", {"sodipodi:nodetypes": None})
    # Shapes
    dclt("rect", {"x": "0", "y": "0"})
    dclt("circle", {"cx": "0", "cy": "0"})
    dclt("ellipse", {"cx": "0", "cy": "0"})
    dclt("path", {"d": None, "inkscape:rounded": "0", "inkscape:randomized": "0", "inkscape:flatsided": "false"}, {"sodipodi:type": "star"})
    # LPEs
    dclt("inkscape:path-effect", {"is_visible": "true"})
    dclt("inkscape:path-effect", {"miter_limit": "4", "linejoin_type": "extrp_arc", "sort_points": "true", "interpolator_beta": "0.2",
                                  "start_linecap_type": "butt", "end_linecap_type": "butt"}, {"effect": "powerstroke"})
    dclt("inkscape:path-effect", {"xx": "true", "yy": "true", "bendpath1-nodetypes": None, "bendpath2-nodetypes": None,
                                                              "bendpath3-nodetypes": None, "bendpath4-nodetypes": None}, {"effect": "envelope"})
    dclt("inkscape:path-effect", {"copytype": "single_stretched", "fuse_tolerance": "0", "normal_offset": "0", "pattern-nodetypes": None, "prop_scale": "1", "prop_units": "false", "scale_y_rel": "false", "spacing": "0", "tang_offset": "0", "vertical_pattern": "false"}, {"effect": "skeletal"})
    # Other SVG objects
    dclt("use", {"x": "0", "y": "0", "height": "100%", "width": "100%"})
    dclt("clipPath", {"clipPathUnits": "userSpaceOnUse"})
    dclt("mask", {"maskUnits": "userSpaceOnUse"})
    # Miscellaneous
    dclt("*", {"inkscape:collect": "always", "inkscape:transform-center-x": None, "inkscape:transform-center-y": None})
    # Operations on the root node, which can't be reached by findall
    dmrn(rn.attrib, {"version": None, "inkscape:version": None, "sodipodi:docname": None,
                     "inkscape:export-filename": None, "inkscape:export-xdpi": None, "inkscape:export-ydpi": None})
    for nv in rn.findall("sodipodi:namedview", nm): rn.remove(nv)
    if opts[0]:
        for nv in rn.findall("d:metadata", nm): rn.remove(nv)
    if opts[1]: dmrn(rn.attrib, {"height": None, "width": None, "viewBox": None})
    
    # Phase 2: style property removals (but push properties into style tags first)
    for a in defstyle:
        for i in rn.findall(".//*[@{0}]".format(a), nm):
            i.set("style", a + ":" + i.get(a) + ";" + i.get("style", ""))
            del i.attrib[a]
    for n in rn.findall(".//d:clipPath/d:path", nm): # Look for "clip-rule:evenodd", keep only that
        if "clip-rule:evenodd" in n.get("style", ""): n.set("style", "clip-rule:evenodd")
        else: dmrn(n.attrib, {"style": None})
    # EXCEPT if the styled element represents a bespokely placed path. Then you don't do anything.
    ptemplate = rn.findall(".//d:defs/d:path", nm)
    for n in rn.findall(".//*[@style]", nm):
        # Prepare the style dictionary om
        raw = n.get("style", "").split(";")
        for i in range(raw.count("")): raw.remove("")
        om = dict([(a[:a.index(":")], a[a.index(":") + 1:]) for a in raw])
        if n not in ptemplate:
            # Colour aliasing
            for c in ["fill", "stroke", "stop-color", "flood-color", "lighting-color",
                      "color", "solid-color", "text-decoration-color"]:
                if c in om and om[c] in calias: om[c] = calias[om[c]]
            # Preclusions
            for p in precld:
                if p not in om: om[p] = defstyle[p]
                dmrn(om, {q: None for q in precld[p]}, {p: defstyle[p]})
            # If stroke-linejoin isn't miter, stroke-miterlimit is redundant
            dmrn(om, {"stroke-miterlimit": None}, {"!stroke-linejoin": "miter"})
            # Default values
            dmrn(om, defstyle)
        # Splitting a style attribute with less than four properties saves a few bytes
        if len(om) < 1: del n.attrib["style"]
        elif len(om) < 4:
            del n.attrib["style"]
            for a in om: n.set(a, om[a])
        else: n.set("style", ";".join([a + ":" + om[a] for a in om]))
    
    # Phase 3: unused definitions and redundant ID removal
    # 3a: reference map with temporary IDs
    # Dictionary pairs are {id: {uses, fills, strokes, etc. referenced by that ID}}
    rd, cnt = {}, 0
    for k in rn.findall(".//*"):
        rf = {}
        # Style properties
        for a in ["fill", "stroke", "clip-path", "mask", "filter"]:
            raw = k.get("style", "").split(";")
            sty = dict([(a[:a.index(":")], a[a.index(":") + 1:]) for a in raw]) if len(raw) > 1 else {}
            rf[a] = sty[a] if a in sty else k.get(a, "")
            rf[a] = rf[a][5:-1] if rf[a].startswith("url(#") else None
        # Not style properties
        rf["tag"] = collapse(k.tag)
        tmp = k.get("{http://www.w3.org/1999/xlink}href")
        rf["use"] = tmp[1:] if tmp != None else None
        tmp = k.get("{http://www.inkscape.org/namespaces/inkscape}path-effect")
        rf["path-effect"] = tmp[1:] if tmp != None else None
        irk = k.get("id")
        if irk == None:
            while "q" + str(cnt) in rd: cnt += 1
            irk = "q" + str(cnt)
            k.set("id", irk)
        rd[irk] = rf
    # 3b: unreferenced ID removal
    ao, ro = set(rd.keys()), []
    for e in rd: ro.extend([rd[e][a] for a in ["use", "fill", "stroke", "clip-path", "mask", "filter", "path-effect"]])
    for rm in ao - set(ro):
        fat = rn.find(".//*[@id='{0}']".format(rm), nm)
        del fat.attrib["id"]
    if rn.get("id") != None: del rn.attrib["id"]
    # 3c: removal of unused <defs>
    df, ud = rn.find(".//d:defs", nm), []
    if df != None:
        for dlm in df:
            if dlm.get("id") == None: ud.append(dlm)
        for z in ud: df.remove(z)
        if not len(list(df)): rn.remove(df)
    
    # Final output
    outf = open("{0}-rarified.svg".format(f[:-4]), 'w')
    if opts[2]: outf.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
    tr.write(outf, "unicode")
    outf.close()

t.register_namespace("", "http://www.w3.org/2000/svg")
t.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
t.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
t.register_namespace("xlink", "http://www.w3.org/1999/xlink")
t.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
t.register_namespace("cc", "http://creativecommons.org/ns#")
t.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
cdl = argparse.ArgumentParser(prog="./rarify.py", description="Rarify, the uncouth SVG optimiser")
cdl.add_argument("-m", "--metadata", action="store_true", default=False, help="remove metadata")
cdl.add_argument("-d", "--dimens", action="store_true", default=False, help="remove dimensions")
cdl.add_argument("-x", "--xml", action="store_true", default=False, help="add XML header")
cdl.add_argument("files", nargs="*", help="list of files to rarify")
flags = cdl.parse_args()
opts = (flags.metadata, flags.dimens, flags.xml)
for f in flags.files:
    tr = t.parse(f)
    rn = tr.getroot()
    rarify(f, opts)

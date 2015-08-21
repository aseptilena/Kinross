#!/usr/bin/env python3.4
# Helper functions for Kinross: SVG node processing and simplification (Rarify's "Sweetie Belle")
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import xml.etree.ElementTree as t
from .colours import repr2col, col2repr

# Default style properties
defstyle = {"display": "inline",
            "overflow": "visible",
            "visibility": "visible",
            "isolation": "auto",
            "enable-background": "accumulate",
            # Fill, stroke and markers
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
            "opacity": "1",
            "color-interpolation": "sRGB",
            "color-interpolation-filters": "linearRGB",
            "color-rendering": "auto",
            "image-rendering": "auto",
            "mix-blend-mode": "normal",
            "paint-color-rendering": "auto",
            "paint-order": "normal",
            "shape-rendering": "auto",
            "solid-color": "#000",
            "solid-opacity": "1",
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
# Default attributes of projects; None denotes any string
defattrb = [("path", {"d": None}, {"inkscape:original-d": None}), # This is the very reason this script was written
            (None, {"inkscape:connector-curvature": "0"}, {}),
            (None, {"sodipodi:nodetypes": None}, {}),
            
            ("circle", {"cx": "0", "cy": "0"}, {}),
            ("ellipse", {"cx": "0", "cy": "0"}, {}),
            ("path", {"d": None, "inkscape:rounded": "0", "inkscape:randomized": "0", "inkscape:flatsided": "false"}, {"sodipodi:type": "star"}),
            
            ("inkscape:path-effect", {"is_visible": "true"}, {}),
            ("inkscape:path-effect", {"miter_limit": "4", "linejoin_type": "extrp_arc", "sort_points": "true", "interpolator_beta": "0.2", "start_linecap_type": "butt", "end_linecap_type": "butt"}, {"effect": "powerstroke"}),
            ("inkscape:path-effect", {"xx": "true", "yy": "true", "bendpath1-nodetypes": None, "bendpath2-nodetypes": None, "bendpath3-nodetypes": None, "bendpath4-nodetypes": None}, {"effect": "envelope"}),
            ("inkscape:path-effect", {"copytype": "single_stretched", "fuse_tolerance": "0", "normal_offset": "0", "pattern-nodetypes": None, "prop_scale": "1", "prop_units": "false", "scale_y_rel": "false", "spacing": "0", "tang_offset": "0", "vertical_pattern": "false"}, {"effect": "skeletal"}),
            
            ("use", {"x": "0", "y": "0", "height": "100%", "width": "100%"}, {}),
            ("clipPath", {"clipPathUnits": "userSpaceOnUse"}, {}),
            ("mask", {"maskUnits": "userSpaceOnUse"}, {}),
            
            (None, {"inkscape:collect": "always", "inkscape:transform-center-x": None, "inkscape:transform-center-y": None}, {}),
            ("svg", {"version": None, "inkscape:version": None, "sodipodi:docname": None, "inkscape:export-filename": None, "inkscape:export-xdpi": None, "inkscape:export-ydpi": None}, {})]

# Colour properties and their corresponding opacities
colp = {"fill": "fill-opacity",
        "stroke": "stroke-opacity",
        "stop-color": "stop-opacity",
        "color": "opacity",
        "solid-color": "solid-opacity",
        "flood-color": "flood-opacity",
        "lighting-color": None,
        "text-decoration-color": None}

# Preclusions
precld = {"stroke-dasharray": ("stroke-dashoffset"),
          "stroke": ("stroke-opacity", "stroke-width", "stroke-linejoin", "stroke-linecap", "stroke-miterlimit", "stroke-dasharray", "stroke-dashoffset")}
# Namespace map
nm = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}

def nmsify(t):
    a = t.split(':')
    if len(a) == 1: return "{http://www.w3.org/2000/svg}" + t
    return "{{{0}}}{1}".format(nm[a[0]], a[1])
# How is this different from the above function? It doesn't add the default namespace, which is useful for attributes.
def expand(t):
    a = t.split(':')
    if len(a) == 1: return t
    return "{{{0}}}{1}".format(nm[a[0]], a[1])

# terse() returns the shortest representation of the input with opacity explicitly stated.
def terse(s, a):
    if s[0] == "u" or s == "none": return (s, a)
    else: return repr2col(col2repr(s, a))

# Dictionary match and remove with namespaces.
# pr is the list of pairs to remove; ! prefix removes non-matchings (key is there but value is not the one specified).
# cond gives pairs which must all be there; !-prefixing works similarly.
def dmrn(d, pr, cond = {}):
    rute = True
    for c in cond:
        negate, term = c[0] == '!', c.lstrip("!")
        rute &= expand(term) in d and negate ^ (cond[c] in (d[expand(term)], None))
    if rute:
        for p in pr:
            negate, term = p[0] == '!', p.lstrip("!")
            if expand(term) in d and negate ^ (pr[p] in (d[expand(term)], None)): del d[expand(term)]

# Returns the style dictionary while at the same time purging it from the node in question
def collsty(node):
    sd, sa = {}, []
    for p in node.attrib:
        if p in defstyle:
            sd[p] = node.get(p)
            sa.append(p)
    for a in sa: del node.attrib[a]
    sp = node.get("style", "").split(';')
    if sp: sd.update(dict([a.split(':') for a in sp if a]))
    node.set("style", "")
    return sd
# Sets the style while minimising the number of bytes used (collstyle will always leave a stub so del is OK)
def locksty(node, sd):
    if len(sd) < 1: del node.attrib["style"]
    elif len(sd) < 4:
        del node.attrib["style"]
        for p in sd: node.set(p, sd[p])
    else: node.set("style", ";".join([p + ":" + sd[p] for p in sd]))
    
# Phases 1 and 2 of the old (standalone) Rarify script on the node level
def nwhack(node):
    sd = collsty(node)
    for aset in defattrb:
        if aset[0] == None or node.tag == nmsify(aset[0]): dmrn(node.attrib, aset[1], aset[2])
    # Colour aliasing TODO handle opacities?
    for c in colp:
        if c in sd: sd[c] = terse(sd[c], None)[0]
    
    for p in precld:
        if p not in sd: sd[p] = defstyle[p]
        dmrn(sd, {q: None for q in precld[p]}, {p: defstyle[p]})
    dmrn(sd, {"stroke-miterlimit": None}, {"!stroke-linejoin": "miter"})
    dmrn(sd, defstyle)
    locksty(node, sd)

def streamsty(node): locksty(node, collsty(node))

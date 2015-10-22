# Helper functions for Kinross: SVG node processing and simplification (Rarify's "Sweetie Belle")
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import xml.etree.ElementTree
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
            "text-decoration-color": "#000"}
# Text styling only properly belongs on text and tspan tags!
dstytext = {"baseline-shift": "baseline",
            "block-progression": "tb",
            "direction": "ltr",
            "font-family": "sans-serif",
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
            "line-height": "normal",
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
rstytext = {a: None for a in dstytext}
# Inkscape aliases the following default style properties for text as such. There is no corresponding "None-dictionary" as above because all its keys are in dstytext.
styleplus = {"letter-spacing": "0px",
             "word-spacing": "0px",
             "line-height": "125%",
             "font-weight": "500"}
# Default attributes of objects; None denotes any string. The LPE output tuple, the very reason Rarify was written, is separate so as to enable controlling its execution.
defattrb = [(None, {"inkscape:connector-curvature": "0"}, {}),
            (None, {"sodipodi:nodetypes": None}, {}),
            
            ("circle", {"cx": "0", "cy": "0"}, {}),
            ("ellipse", {"cx": "0", "cy": "0"}, {}),
            ("path", {"d": None, "inkscape:rounded": "0", "inkscape:randomized": "0", "inkscape:flatsided": "false"}, {"sodipodi:type": "star"}),
            
            ("inkscape:path-effect", {"is_visible": "true"}, {}),
            ("inkscape:path-effect", {"interpolator_type": "CubicBezierFit",
                                      "miter_limit": "4",
                                      "linejoin_type": "extrp_arc",
                                      "sort_points": "true",
                                      "interpolator_beta": "0.2",
                                      "start_linecap_type": "butt",
                                      "end_linecap_type": "butt"}, {"effect": "powerstroke"}),
            ("inkscape:path-effect", {"xx": "true",
                                      "yy": "true",
                                      "bendpath1-nodetypes": None,
                                      "bendpath2-nodetypes": None,
                                      "bendpath3-nodetypes": None,
                                      "bendpath4-nodetypes": None}, {"effect": "envelope"}),
            ("inkscape:path-effect", {"copytype": "single_stretched",
                                      "fuse_tolerance": "0",
                                      "normal_offset": "0",
                                      "pattern-nodetypes": None,
                                      "prop_scale": "1",
                                      "prop_units": "false",
                                      "scale_y_rel": "false",
                                      "spacing": "0",
                                      "tang_offset": "0",
                                      "vertical_pattern": "false"}, {"effect": "skeletal"}),
            
            ("use", {"x": "0", "y": "0", "height": "100%", "width": "100%"}, {}),
            ("clipPath", {"clipPathUnits": "userSpaceOnUse"}, {}),
            ("mask", {"maskUnits": "userSpaceOnUse"}, {}),
            ("text", {"sodipodi:linespacing": "125%"}, {}),
            
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

# Namespace map for the two namespace-expanding functions, which really only need to bother with three namespaces
longnms = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}
def treename(t):
    """On node tags, returns their names as stored in the element tree."""
    a = t.split(':')
    if len(a) == 1: return "{http://www.w3.org/2000/svg}" + t
    return "{{{0}}}{1}".format(longnms[a[0]], a[1])
def fullattr(t):
    """Expands the namespaces of attributes to match their names in the tree. Not to be confused with treename."""
    a = t.split(':')
    if len(a) == 1: return t
    return "{{{0}}}{1}".format(longnms[a[0]], a[1])
# Returns the shortest representation of the input with opacity.
def tersecol(s, a):
    if s[0] == "u" or s == "none": return (s, a)
    else: return repr2col(col2repr(s, a))
def matchrm(d, pr, cond = {}):
    """Dictionary match-and-remove with namespaces.
    pr is the list of pairs to remove; ! prefix removes non-matchings (key is there but value is not the one specified).
    cond gives pairs which must all be there; !-prefixing works similarly."""
    rute = True
    for c in cond:
        negate, term = c[0] == '!', c.lstrip("!")
        rute &= fullattr(term) in d and negate ^ (cond[c] in (d[fullattr(term)], None))
    if rute:
        for p in pr:
            negate, term = p[0] == '!', p.lstrip("!")
            if fullattr(term) in d and negate ^ (pr[p] in (d[fullattr(term)], None)): del d[fullattr(term)]

def styledict(node, preserve = False):
    """Returns the style dictionary; if the second argument is True, also wipes it from the node."""
    sd, sa = {}, []
    for p in node.attrib:
        if p in defstyle:
            sd[p] = node.get(p)
            if not preserve: sa.append(p)
    for a in sa: del node.attrib[a]
    sp = node.get("style", "").split(';')
    if sp: sd.update(dict([a.split(':') for a in sp if a]))
    if not preserve: node.set("style", "")
    return sd
def stylesplit(node, sd):
    """Sets the style, minimising occupied space."""
    if len(sd) < 1: del node.attrib["style"]
    elif len(sd) < 4:
        del node.attrib["style"]
        for p in sd: node.set(p, sd[p])
    else: node.set("style", ";".join([p + ":" + sd[p] for p in sd]))

def whack(node, lpeoutput = False):
    """Phases 1 and 2 of the old Rarify script on the node level. lpeoutput, if True, preserves the d of paths with LPEs (which would normally be removed) so that other applications can render them correctly."""
    sd = styledict(node)
    for aset in defattrb:
        if aset[0] == None or node.tag == treename(aset[0]): matchrm(node.attrib, aset[1], aset[2])
    if not lpeoutput and node.tag == "{http://www.w3.org/2000/svg}path": matchrm(node.attrib, {"d": None}, {"inkscape:original-d": None})
    # Colour normalisation
    for c in colp:
        if c not in sd: sd[c] = defstyle[c]
        if colp[c] != None and colp[c] not in sd: sd[colp[c]] = defstyle[colp[c]]
        tersed = tersecol(sd[c], sd[colp[c]] if colp[c] else None)
        sd[c] = tersed[0]
        if colp[c]: sd[colp[c]] = tersed[1]
    # Preclusions
    for p in precld:
        if p not in sd: sd[p] = defstyle[p]
        matchrm(sd, {q: None for q in precld[p]}, {p: defstyle[p]})
    matchrm(sd, {"stroke-miterlimit": None}, {"!stroke-linejoin": "miter"})
    matchrm(sd, defstyle)
    if node.tag in ("{http://www.w3.org/2000/svg}text", "{http://www.w3.org/2000/svg}tspan"):
        matchrm(sd, dstytext)
        matchrm(sd, styleplus)
    else: matchrm(sd, rstytext)
    stylesplit(node, sd)
# In cases where the "redundant" attributes will matter later, do a weak whacking (canonise the style properties)
def weakwhack(node): stylesplit(node, styledict(node))
# The nodes a node references (via "URLs" and hashes)
def refsof(node):
    rf, sd = {}, styledict(node, True)
    for a in ("fill", "stroke", "clip-path", "mask", "filter"):
        if a in sd and sd[a][0] == 'u': rf[a] = sd[a][5:-1]
    tmp = node.get("{http://www.w3.org/1999/xlink}href")
    if tmp: rf["use"] = tmp[1:]
    tmp = node.get("{http://www.inkscape.org/namespaces/inkscape}path-effect")
    if tmp: rf["path-effect"] = tmp[1:]
    return rf

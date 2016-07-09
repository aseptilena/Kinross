# Helper functions for Kinross: SVG node processing and simplification (Rarify's "Sweetie Belle", phases 2 and 3)
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from xml.etree.ElementTree import tostring
from xml.dom.minidom import parseString
from .colours import shortcolour, shortdiaph
from .regexes import stylecrunch
from .affines import tf
from .segment import ellipt
def formalxml(rn):
    """Returns the formatted string of the element rn and its children (tab = two spaces)."""
    return parseString(tostring(rn, "unicode")).toprettyxml("  ")

def satellitedish():
    """As an aside, returns the SVG representation of my "satellite dish" logo."""
    from math import sqrt
    k, l, m = sqrt(13.5), sqrt(2), (31 + 12 * sqrt(3)) / 23
    t = sqrt(69 / (4 * (1 + m * m)))
    p, q = (l - k) / 2 - t, (l + k) / 2 - m * t
    d = [p, -q, l, -l, q, -p]
    c = [str(round(i * sqrt(2 / 3) + 4, 7)) for i in d]
    return '<svg><rect fill="#230f38" width="8" height="8"/><path style="fill:none;stroke:#6dc6fb;stroke-width:.2109375;stroke-linecap:round;stroke-linejoin:round" d="M1 1 {0} 7 7"/></svg>'.format(" ".join(c))

# SVG namespace strings in round brackets
_svg = "{http://www.w3.org/2000/svg}"
_ink = "{http://www.inkscape.org/namespaces/inkscape}"
_sod = "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}"
_xln = "{http://www.w3.org/1999/xlink}"
# Namespace dictionary for findall
nm_findall = {"svg": _svg[1:-1], "inkscape": _ink[1:-1], "sodipodi": _sod[1:-1]}
# Namespace dictionary for the element tree parser
svgnms = {"": _svg[1:-1], "inkscape": _ink[1:-1], "sodipodi": _sod[1:-1], "xlink": _xln[1:-1],
          "dc": "http://purl.org/dc/elements/1.1/", "cc": "http://creativecommons.org/ns#", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
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
            "mask": "none"}
# Text styling only properly belongs on text and tspan nodes, so these attributes can be removed on other nodes.
dstytext = {"baseline-shift": "baseline",
            "block-progression": "tb",
            "direction": "ltr",
            "dominant-baseline": "auto",
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
            "text-orientation": "mixed",
            "text-transform": "none",
            "white-space": "normal",
            "word-spacing": "normal",
            "writing-mode": "lr-tb"}
dstytextnone = {v: None for v in dstytext}
# Convenience SET of all style properties.
allstyle = set(defstyle.keys()) | set(dstytext.keys()) 
# Inkscape aliases the following default style properties for text as such:
styleplus = {"letter-spacing": "0px",
             "word-spacing": "0px",
             "line-height": "125%",
             "font-weight": "500"}
# Default attributes of objects; None denotes any string. The LPE output tuple, the reason Rarify was written in the first place, is separate so as to enable controlling its execution.
defattrb = [(None, {_ink + "connector-curvature": "0"}),
            (None, {_sod + "nodetypes": None}),
            
            (_svg + "rect", {"x": "0", "y": "0"}),
            (_svg + "circle", {"cx": "0", "cy": "0"}),
            (_svg + "ellipse", {"cx": "0", "cy": "0"}),
            (_svg + "path", {"d": None, _ink + "rounded": "0", _ink + "randomized": "0", _ink + "flatsided": "false"}, {_sod + "type": "star"}),
            
            (_ink + "path-effect", {"is_visible": "true"}),
            (_ink + "path-effect", {"interpolator_type": "CubicBezierFit",
                                    "miter_limit": "4",
                                    "linejoin_type": "extrp_arc",
                                    "sort_points": "true",
                                    "interpolator_beta": "0.2",
                                    "start_linecap_type": "butt",
                                    "end_linecap_type": "butt"}, {"effect": "powerstroke"}),
            (_ink + "path-effect", {"xx": "true",
                                    "yy": "true",
                                    "bendpath1-nodetypes": None,
                                    "bendpath2-nodetypes": None,
                                    "bendpath3-nodetypes": None,
                                    "bendpath4-nodetypes": None}, {"effect": "envelope"}),
            (_ink + "path-effect", {"copytype": "single_stretched",
                                    "fuse_tolerance": "0",
                                    "normal_offset": "0",
                                    "pattern-nodetypes": None,
                                    "prop_scale": "1",
                                    "prop_units": "false",
                                    "scale_y_rel": "false",
                                    "spacing": "0",
                                    "tang_offset": "0",
                                    "vertical_pattern": "false"}, {"effect": "skeletal"}),
            (_ink + "path-effect", {"attempt_force_join": "true",
                                    "linecap_type": "butt",
                                    "linejoin_type": "extrp_arc",
                                    "miter_limit": "100"}, {"effect": "join_type"}),
            
            (_svg + "use", {"x": None, "y": None, "height": None, "width": None}),
            (_svg + "clipPath", {"clipPathUnits": "userSpaceOnUse"}),
            (_svg + "mask", {"maskUnits": "userSpaceOnUse"}),
            
            (None, {_ink + "collect": "always", _ink + "transform-center-x": None, _ink + "transform-center-y": None}),
            (_svg + "svg", {"version": None, _ink + "version": None, _sod + "docname": None, _ink + "export-filename": None, _ink + "export-xdpi": None, _ink + "export-ydpi": None})]
# Colour and opacity properties
chromaprops = ("fill", "stroke", "stop-color", "color", "solid-color", "flood-color", "lighting-color", "text-decoration-color")
diaphanities = ("fill-opacity", "stroke-opacity", "stop-opacity", "opacity", "solid-opacity", "flood-opacity")

def rm_default(sd, dct, cond = {}):
    """Removes keys from sd according to the default dictionary dct. cond gives conditions; all keys in cond must be in sd
    and the corresponding values must match. None can be used in dct and cond to match any value. Dictionaries are assumed to have only string values."""
    for c in cond:
        if c not in sd or cond[c] not in (None, sd[c]): return
    k = list(sd.keys())
    for i in k:
        if i in dct and dct[i] in (None, sd[i]): del sd[i]
def expungestyle(node):
    """Takes all style attributes from the node and expunges them, then returns the dictionary of properties."""
    res = {s: node.attrib.pop(s) for s in allstyle & set(node.keys())}
    res.update(stylecrunch(node.attrib.pop("style", "")))
    return res
def obtainstyle(node):
    """Like expungestyle but does not remove the style properties."""
    res = {s: node.get(s) for s in allstyle & set(node.keys())}
    res.update(stylecrunch(node.get("style", "")))
    return res
def distributestyle(node, sd):
    """On a node with no style, sets it while minimising occupied space."""
    if sd:
        if len(sd) < 4: [node.set(p, sd[p]) for p in sd]
        else: node.set("style", ";".join([p + ":" + sd[p] for p in sd]))

def whack(node, lpecrush = False):
    """Phases 1 and 2 of the old Rarify script on the node level. lpecrush, if True, removes the Inkscape-generated d attributes of LPE-affected paths for smaller file sizes,
    at the cost of breaking the view in browsers and the like."""
    # Non-styling default attributes
    for aset in defattrb:
        if aset[0] == node.tag or not aset[0]: rm_default(node.attrib, *aset[1:])
    if lpecrush and node.tag.endswith("}path"): rm_default(node.attrib, {"d": None}, {_ink + "original-d": None})
    # Style dictionary, colour/opacity shortening, normalisation for paint-order
    sd = expungestyle(node)
    for c in chromaprops:
        if c in sd: sd[c] = shortcolour(sd[c])
    for d in diaphanities:
        if d in sd: sd[d] = shortdiaph(sd[d])
    if sd.get("paint-order", "normal") != "normal":
        pm = sd["paint-order"]
        if pm.count(" ") == 2: pm = pm[:pm.rfind(" ")]
        if pm.endswith("fill"): pm = pm[:-5]
        if pm == "fill stroke": pm = "normal"
        sd["paint-order"] = pm
    # Properties rendered useless if other properties are set certain ways
    if sd.get("stroke-dasharray", "none") == "none": sd.pop("stroke-dashoffset", 0)
    if sd.get("stroke", "none") == "none":
        for spr in ("stroke-opacity", "stroke-width", "stroke-linejoin", "stroke-linecap", "stroke-miterlimit", "stroke-dasharray", "stroke-dashoffset"): sd.pop(spr, 0)
    if sd.get("stroke-linejoin", "miter") != "miter": sd.pop("stroke-miterlimit", 0)
    if sd.get("fill") == "none": sd.pop("fill-rule", 0)
    sd.pop("-inkscape-font-specification", 0)
    # Default style property removal
    rm_default(sd, defstyle)
    if node.tag.endswith("}text") or node.tag.endswith("}tspan"):
        rm_default(sd, dstytext)
        rm_default(sd, styleplus)
    else: rm_default(sd, dstytextnone)
    # Final distribution into the node
    distributestyle(node, sd)
# In cases where the "redundant" attributes will matter later, do a weak whacking (canonise the style properties).
def weakwhack(node): distributestyle(node, expungestyle(node))
# Extra processing for text objects, which may contain tspans with redundant style properties
def textwhack(node):
    td, tit = obtainstyle(node), node.iter()
    next(tit)
    for t in tit:
        sd = expungestyle(t)
        rm_default(sd, td)
        distributestyle(t, sd)
def refsof(node):
    """Works out which nodes the input node references, whether by hashes or URIs. Assumes the style has already been canonised."""
    rf, sd = {}, obtainstyle(node)
    for a in ("fill", "stroke", "clip-path", "mask", "filter"):
        if a in sd and sd[a][0] == 'u': rf[a] = sd[a][5:-1]
    tmp = node.get(_xln + "href")
    if tmp: rf["use"] = tmp[1:]
    tmp = node.get(_ink + "path-effect")
    if tmp: rf["path-effect"] = tmp[1:]
    return rf

# Higher-order functions (involving some maths) follow
def path2oval(arc):
    """With a Sodipodi arc that is also an ellipse, converts it into a real ellipse; does not process transformations or further simplify into a circle."""
    if arc.get(_sod + "start") == None: # If it has no start attribute it also has no end attribute
        for param in ("cx", "cy", "rx", "ry"): arc.set(param, arc.attrib.pop(_sod + param))
        del arc.attrib[_sod + "type"]
        arc.attrib.pop("d", 0)
        arc.tag = _svg + "ellipse"
def ellipsecollapse(ell):
    """Given a transformed ellipse element, collapses the transform into the ellipse if it has no stroke and then converts into a circle if applicable."""
    if ell.get("stroke") == None and "stroke" not in stylecrunch(ell.get("style", "")): # ensures that no transformation of the stroke is lost
        tfstr = ell.get("transform", "rotate(0)")
        if "rotate" not in tfstr or tfstr.count('(') > 1:
            e, t, oth = ellipt.fromsvg_node(ell)
            tag, atb = (t @ e).tosvg_node()
            atb.update(oth)
            ell.tag, ell.attrib = _svg + tag, atb

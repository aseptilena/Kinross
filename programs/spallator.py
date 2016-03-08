#!/usr/bin/env python3.5
# The main function here "spallates" (makes many instances, some of which may be transformed) an object on a canvas.
# This was originally motivated by the need to generate plausible patterns for MLPFIM vectors, but can be fine-tuned.
# Parcly Taxel / Jeremy Tan, 2016 | https://parclytaxel.tumblr.com
from cmath import polar, rect
import xml.etree.ElementTree as t
from kinback.affines import affine, parsetransform, collapsibility
from kinback.ellipse import oval
from kinback.svgproc import formalxml
from kinback.discord import KinrossRandom, rectpointpick
sp = "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}"
t.register_namespace("sodipodi", sp[1:-1])
rng = KinrossRandom()

# The canvas is from the origin to a given opposite corner, assumed to be in quadrant 1. Other parameters are the spallated object,
# a density (number of instances per unit square) and a function providing a random SVG transformation string depending on canvas.
# The root <svg> element is returned, which may then be processed further; size in this script always refers to canvas size.
def spallate(obj, rtf, dens, size = 1000+1000j):
    rn = t.Element("svg", {"viewBox": "0 0 {} {}".format(size.real, size.imag)})
    for q in range(round(size.real * size.imag * dens)): rn.append(handletransform(obj, rtf(size)))
    return rn

def handletransform(item, tf):
    if item.tag == "circle" or item.tag == "ellipse":
        cx, cy, rx, ry = float(item.get("cx", "0")), float(item.get("cy", "0")), float(item.get("r", item.get("rx"))), float(item.get("r", item.get("ry")))
        others = {k: item.attrib[k] for k in item.attrib if k not in ("cx", "cy", "r", "rx", "ry")}
        ntag, nattrib = oval(complex(cx, cy), rx, ry).affine(parsetransform(tf)).svgrepr()
        nattrib.update(others)
        return t.Element(ntag, nattrib)
    if item.get(sp + "type") == "star":
        tm = parsetransform(tf)
        if collapsibility(tm):
            others = item.attrib.copy()
            centre = affine(tm, complex(float(item.get(sp + "cx", "0")), float(item.get(sp + "cy", "0"))))
            np1 = affine(tm, rect(float(item.get(sp + "r1")), float(item.get(sp + "arg1"))))
            np2 = affine(tm, rect(float(item.get(sp + "r2")), float(item.get(sp + "arg2"))))
            r1, arg1 = polar(np1 - centre)
            r2, arg2 = polar(np2 - centre)
            nparams = {sp + "cx": str(centre.real), sp + "cy": str(centre.imag), sp + "r1": str(round(r1, 3)),
                       sp + "r2": str(round(r2, 3)), sp + "arg1": str(round(arg1, 7)), sp + "arg2": str(round(arg2, 7))}
            others.update(nparams)
            return t.Element("path", others)
    props = item.attrib.copy()
    props["transform"] = tf
    return t.Element(item.tag, props)

# Examples of the function's use below; object/density fixed
# For the astroid sparkles in Nightmare Rarity's mane
astroid = t.Element("path", {"d": "M-5,0C-2-1-1-4 0-11 1-4 2-1 5,0 2,1 1,4 0,11-1,4-2,1-5,0Z", "fill": "#fff"})
def rtf_astroid(size):
    pos, scale = rectpointpick(size), 1 + min(rng.geometricvariate(2 / 3), 4) / 4
    return "translate({} {})scale({})".format(round(pos.real, 3), round(pos.imag, 3), scale)
def spallate_astroid(size = 1100+1400j): return spallate(astroid, rtf_astroid, 1.96e-4, size)

# For the Equestrian night sky
circle = t.Element("circle", {"r": "1", "fill": "#b4a8fe"})
def rtf_circle(size):
    pos, scale = rectpointpick(size), 3.5 + 1.5 * min(rng.geometricvariate(2 / 3), 5)
    return "translate({} {})scale({})".format(round(pos.real, 3), round(pos.imag, 3), scale)
def spallate_circle(size = 1000+1000j): return spallate(circle, rtf_circle, 2.5e-4, size)

# For the sparkles of magic auras and Luna's mane
star = t.Element("path", {"fill": "#b6ecff", sp + "type": "star", sp + "sides": "4", sp + "r1": "4.8", sp + "r2": "0.6", sp + "arg1": "0", sp + "arg2": "0.78539816"})
def rtf_star(size):
    pos, scale, twist = rectpointpick(size), min(rng.geometricvariate(3 / 5), 4) + 1, rng.random() * 90
    return "translate({} {})rotate({})scale({})".format(round(pos.real, 3), round(pos.imag, 3), twist, scale)
def spallate_star(size = 1000+1000j): return spallate(star, rtf_star, 1.49e-4, size)

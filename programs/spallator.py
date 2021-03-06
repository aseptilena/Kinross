#!/usr/bin/env python3.5
# The main function here "spallates" (makes many instances, some of which may be transformed) an object on a canvas.
# This was originally motivated by the need to generate plausible patterns for MLPFIM vectors, but can be fine-tuned.
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from cmath import polar, rect
import xml.etree.ElementTree as t
from kinback.affines import tf
from kinback.segment import ellipt
from kinback.discord import KinrossRandom, rectpointpick
sp = "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}"
t.register_namespace("sodipodi", sp[1:-1])
rng = KinrossRandom()

# spallate() requires four arguments:
# 1. The object to make copies of as an SVG element object.
# 2. The canvas size expressed as a complex number in quadrant 1 (positive real and imaginary parts; the actual canvas runs from the origin to this point).
# 3. A function returning a random SVG transformation string based on the canvas size.
# 4. The density of the spallation. This is the average number of objects per 10000 square units (100×100 square); the multiplication is done to avoid small numbers.
# The <svg> root node containing the spallated copies is returned.
def spallate(obj, rtf, dens, size = 1000+1000j):
    rn = t.Element("svg", {"viewBox": "0 0 {} {}".format(size.real, size.imag)})
    for q in range(round(size.real * size.imag * dens * 1e-4)): rn.append(handletransform(obj, rtf(size)))
    return rn

def handletransform(item, tfs):
    if item.tag == "circle" or item.tag == "ellipse":
        m = tf.fromsvg(tfs)
        e, u, oth = ellipt.fromsvg_node(item)
        tag, atb = (m @ u @ e).tosvg_node()
        atb.update(oth)
        return t.Element(tag, atb)
    if item.get(sp + "type") == "star":
        m = tf.fromsvg(tfs)
        if m.isconformal():
            others = item.attrib.copy()
            centre = m @ complex(float(item.get(sp + "cx", "0")), float(item.get(sp + "cy", "0")))
            np1 = m @ rect(float(item.get(sp + "r1")), float(item.get(sp + "arg1")))
            np2 = m @ rect(float(item.get(sp + "r2")), float(item.get(sp + "arg2")))
            r1, arg1 = polar(np1 - centre)
            r2, arg2 = polar(np2 - centre)
            nparams = {sp + "cx": str(centre.real), sp + "cy": str(centre.imag), sp + "r1": str(round(r1, 3)),
                       sp + "r2": str(round(r2, 3)), sp + "arg1": str(round(arg1, 7)), sp + "arg2": str(round(arg2, 7))}
            others.update(nparams)
            return t.Element("path", others)
    props = item.attrib.copy()
    props["transform"] = tfs
    return t.Element(item.tag, props)

# Examples of the function's use below; object/density fixed
# For the astroid sparkles in Nightmare Rarity's mane
astroid = t.Element("path", {"d": "M-5,0C-2-1-1-4 0-11 1-4 2-1 5,0 2,1 1,4 0,11-1,4-2,1-5,0Z", "fill": "#fff"})
def rtf_astroid(size):
    pos, scale = rectpointpick(size), 1 + min(rng.geometricvariate(2 / 3), 4) / 4
    return "translate({} {})scale({})".format(round(pos.real, 3), round(pos.imag, 3), scale)
def spallate_astroid(size = 1100+1400j): return spallate(astroid, rtf_astroid, 2, size)

# For the Equestrian night sky
circle = t.Element("circle", {"r": "1", "fill": "#b4a8fe"})
def rtf_circle(size):
    pos, scale = rectpointpick(size), 3.5 + 1.5 * min(rng.geometricvariate(2 / 3), 5)
    return "translate({} {})scale({})".format(round(pos.real, 3), round(pos.imag, 3), scale)
def spallate_circle(size = 1000+1000j): return spallate(circle, rtf_circle, 2.5, size)

# For the sparkles of magic auras and Luna's mane
star = t.Element("path", {"fill": "#b6ecff", sp + "type": "star", sp + "sides": "4", sp + "r1": "4.8", sp + "r2": "0.6", sp + "arg1": "0", sp + "arg2": "0.78539816"})
def rtf_star(size):
    pos, scale, twist = rectpointpick(size), min(rng.geometricvariate(3 / 5), 4) + 1, rng.random() * 90
    return "translate({} {})rotate({})scale({})".format(round(pos.real, 3), round(pos.imag, 3), twist, scale)
def spallate_star(size = 1000+1000j): return spallate(star, rtf_star, 1.5, size)

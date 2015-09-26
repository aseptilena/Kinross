# Helper functions for Kinross: regular expressions for shortest representations of floating-point numbers and path parsing
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import re
huge0 = re.compile(r"0{3,}$")
tiny0 = re.compile(r"(-?)\.(0{3,})")
numre = re.compile(r"([-+]?(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.?))(?:[eE][-+]?[0-9]+)?)")
spacere = re.compile(r"[ ,]*")

def floatinkrep(he):
    """This function is used by the Bezier and elliptical arc classes to give a float's shortest representation in SVG
    with respect to Inkscape's default precision (8 significant digits + 6 after decimal point)."""
    ilen = len(str( abs(int(he)) )) # This is a joke
    dec = str(round(he, min(6, 8 - ilen)))
    if "e" in dec: dec = "{0:f}".format(he).rstrip("0")
    if dec in ("-0.0", "0.0", "0"): return "0"
    if dec[:2] == "0.": dec = dec[1:]
    elif dec[:3] == "-0.": dec = "-" + dec[2:]
    elif dec[-2:] == ".0": dec = dec[:-2]
    em = huge0.search(dec)
    sm = tiny0.search(dec)
    if em: dec = "{}e{}".format(dec[:em.start()], len(em.group()))
    elif sm: dec = "{}{}e-{}".format(sm.group(1), dec[sm.end():], len(dec) - len(sm.group(1)) - 1)
    return dec

def floataffrep(f):
    """The same as the above function, but for transforms which keep 8 significant digits regardless of location."""
    pass # TODO

def tokenisepath(p):
    """Parses SVG path data into its tokens and converts numbers into floats.
    This does not further parse into curves and arcs afterwards, the task left instead to parserhythm() in the rhythms module."""
    t, tokens = [], [c for c in numre.split(p) if not spacere.fullmatch(c)]
    for v in tokens:
        if " " in v or v.isalpha(): t.extend(v.replace(" ", ""))
        else: t.append(float(v))
    return t

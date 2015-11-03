# Helper functions for Kinross: regular expressions for SVG parsing
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import re
huge0 = re.compile(r"0{3,}$")
tiny0 = re.compile(r"^(-?)\.(0{3,})")
nrgx = r"([-+]?(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.?))(?:[eE][-+]?[0-9]+)?)"
numre = re.compile(nrgx)
pathre = re.compile(nrgx[1:-1] + r"|[MCSQTLHVAZmcsqtlhvaz]")
rdigitnormal = lambda k: min(6, 8 - len(k))
rdigitaffine = lambda k: 8 if k == "0" else 8 - len(k)
transformbreaks = re.compile(r"(?:matrix|translate|scale|rotate|skewX|skewY)\s*\(.*?\)")

def floatinkrep(he, aflag = False):
    """Returns the shortest SVG representation of a float. aflag controls whether the float is for paths (8 sf + 6 dp) or transformations (8 sf + 8 dp)."""
    istr = str( abs(int(he)) )
    dec = "{:.8f}".format(round(he, (rdigitaffine if aflag else rdigitnormal)(istr))).rstrip("0").rstrip(".").lstrip("0").replace("-0.", "-.")
    if dec in ("", "-0"): return "0"
    em, sm = huge0.search(dec), tiny0.search(dec)
    if em: dec = "{}e{}".format(dec[:em.start()], len(em.group()))
    elif sm: dec = "{}{}e-{}".format(sm.group(1), dec[sm.end():], len(dec) - len(sm.group(1)) - 1)
    return dec

def tokenisepath(p):
    """Parses SVG path data into its tokens and converts numbers into floats.
    This does not further parse into curves and arcs afterwards, the task left instead to parserhythm() in svgpath."""
    return [t if t.isalpha() else float(t) for t in pathre.findall(p)]

def tokenisetransform(s):
    """Parses a transform in SVG format, returning [transform 1, [parameters of transform 1], transform 2, [parameters of transform 2], ...] in last-to-first-applied order."""
    l, res = transformbreaks.findall(s), []
    for tf in l:
        typ, params = tf[:-1].split("(")
        res.append([typ, [float(n) for n in numre.findall(params)]])
    return res

def numbercrunch(*strs):
    """Concatenates the given number strings, removing all redundant delimiters."""
    # A negative number (begin with -) can immediately follow any other number.
    # A positive float less than 1 (begin with .) can immediately follow exponential forms and numbers that also have a decimal point.
    # In all other cases, a space has to be inserted.
    rlist = [strs[0]]
    for n in strs[1:]:
        if not (n[0] == '-' or n[0] == '.' and ('.' in rlist[-1] or 'e' in rlist[-1])): rlist.append(" ")
        rlist.append(n)
    return "".join(rlist)

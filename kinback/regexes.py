# Helper functions for Kinross: regular expressions for SVG parsing
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
import re
nrgx = r"([-+]?(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.?))(?:[eE][-+]?[0-9]+)?)"
numre = re.compile(nrgx)
pathre = re.compile(nrgx[1:-1] + r"|[MCSQTLHVAZmcsqtlhvaz]")
transformbreaks = re.compile(r"(?:matrix|translate|scale|rotate|skewX|skewY)\s*\(.*?\)")
semicolons = re.compile(r"[^;]+")
singlerotation = re.compile(r"\s*rotate\s*\(\s*" + nrgx + r"\s*\)\s*")

from math import log10, floor
def msfi(x, D = 8):
    """Returns the Minimal String for a Float in Inkscape (8 sf + D dp)."""
    if round(x, D) == 0: return "0"
    a = abs(x)
    a = round(a, min(D, 8 - max(floor(log10(a)) + 1, 0)))
    if a % 1000 == 0: # can use a positive exponent for shortening, e.g. 137000 = 137e3
        i = str(int(a))
        cf = i.rstrip('0')
        res = "{}e{}".format(cf, len(i) - len(cf))
    elif a < 0.001: # can use a negative exponent for shortening, e.g. .00137 = 137e-5
        v = "{:.8f}".format(a).rstrip('0')[2:]
        res = "{}e-{}".format(v.lstrip('0'), len(v))
    else: res = str(a).strip('0').rstrip('.')
    return '-' * (x < 0) + res
floatinkrep = msfi # TODO transitional thing

def tokenisepath(p):
    """Parses SVG path data into its tokens and converts numbers into floats.
    This does not further parse into curves and arcs afterwards, the task left instead to parserhythm() in svgpath."""
    return [t if t.isalpha() else float(t) for t in pathre.findall(p)]

def tokenisetransform(s):
    """Parses a transform in SVG format, returning [[transform 1, [parameters of transform 1]], [transform 2, [parameters of transform 2]], ...] in last-to-first-applied order."""
    l, res = transformbreaks.findall(s), []
    for tf in l:
        typ, params = tf[:-1].split("(")
        res.append([typ, [float(n) for n in numre.findall(params)]])
    return res

def catn(*ns):
    """Concatenates the given number strings, removing all redundant delimiters."""
    res, dp = "", True
    for s in ns:
        res += s if not res or s[0] == '-' or s[0] == '.' and dp else ' ' + s
        dp = '.' in s or 'e' in s
    return res
numbercrunch = catn # TODO transitional thing

def stylecrunch(stystr):
    """Style string as input, dictionary of its attributes as output. Multiple and misplaced semicolons are skipped over seamlessly."""
    return dict(pair.split(":") for pair in semicolons.findall(stystr))

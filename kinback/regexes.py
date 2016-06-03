# Helper functions for Kinross: regular expressions for SVG parsing
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
import re
nrgx = r"([-+]?(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.?))(?:[eE][-+]?[0-9]+)?)"
pathre = re.compile(nrgx[1:-1] + r"|[MCSQTLHVAZmcsqtlhvaz]")
semicolons = re.compile(r"[^;]+")

from math import log10, floor
def fsmn(x, D = 8):
    """Float string minimal Inkscape representation (8 sf + D dp)."""
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
def catn(*ns):
    """Concatenates the given number strings, removing all redundant delimiters."""
    res, dp = "", True
    for s in ns:
        res += s if not res or s[0] == '-' or s[0] == '.' and dp else ' ' + s
        dp = '.' in s or 'e' in s
    return res

def tokenisepath(p):
    """Parses SVG path data into its tokens and converts numbers into floats.
    This does not further parse into curves and arcs afterwards, the task left instead to parserhythm() in svgpath."""
    return [t if t.isalpha() else float(t) for t in pathre.findall(p)]

def stylecrunch(stystr):
    """Style string as input, dictionary of its attributes as output. Multiple and misplaced semicolons are skipped over seamlessly."""
    return dict(pair.split(":") for pair in semicolons.findall(stystr))

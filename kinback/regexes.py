# Helper functions for Kinross: regular expressions for SVG parsing
# Parcly Taxel / Jeremy Tan, 2016
# http://parclytaxel.tumblr.com
import re
huge0 = re.compile(r"0{3,}$")
tiny0 = re.compile(r"(\.0{3,})(\d+)")
nrgx = r"([-+]?(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.?))(?:[eE][-+]?[0-9]+)?)"
numre = re.compile(nrgx)
pathre = re.compile(nrgx[1:-1] + r"|[MCSQTLHVAZmcsqtlhvaz]")
transformbreaks = re.compile(r"(?:matrix|translate|scale|rotate|skewX|skewY)\s*\(.*?\)")
semicolons = re.compile(r"[^;]+")
singlerotation = re.compile(r"\s*rotate\s*\(\s*" + nrgx + r"\s*\)\s*")

def floatinkrep(sf, N = 8):
    """Returns the shortest Inkscape representation of a float: 8 significant digits + N decimal places."""
    s, f = "-" if sf < 0 else "", abs(sf)
    left = len(str(int(f)).lstrip("0"))
    rf = round(f, min(8 - left, N))
    if not rf: return "0"
    if rf == int(rf):
        dec = str(int(rf))
        em = huge0.search(dec)
        if em: dec = "{}e{}".format(dec[:em.start()], len(em.group()))
    elif not left:
        dec = "{:.8f}".format(rf).rstrip("0")[1:]
        sm = tiny0.search(dec)
        if sm: dec = "{}e-{}".format(sm.group(2), len(sm.group(1)))
    else: dec = str(rf)
    return s + dec

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

def numbercrunch(*strs):
    """Concatenates the given number strings, removing all redundant delimiters."""
    # A negative number (begin with -) can immediately follow any other number.
    # A positive float less than 1 (begin with .) can immediately follow exponential forms and numbers that also have a decimal point.
    # In all other cases, a space has to be inserted.
    l = list(strs)
    for i in range(len(l) - 1, 0, -1):
        if l[i][0] == '-' or l[i][0] == '.' and ('.' in l[i - 1] or 'e' in l[i - 1]): continue
        l.insert(i, " ")
    return "".join(l)

def stylecrunch(stystr):
    """Style string as input, dictionary of its attributes as output. Multiple and misplaced semicolons are skipped over seamlessly."""
    return dict(pair.split(":") for pair in semicolons.findall(stystr))

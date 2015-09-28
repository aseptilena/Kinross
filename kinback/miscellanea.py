# Helper functions for Kinross: miscellaneous things
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import time, hashlib, webbrowser

exts = (".svg", ".png", ".jpg", ".jpeg", ".txt", ".tar.gz", ".tar.bz2", ".tar", ".gz", ".bz2", ".7z", ".zip", ".py")
# Stamp a filename with a given string, separated by a hyphen
def stamp(fn, s):
    for ext in exts:
        if fn.endswith(ext): return fn[:-len(ext)] + "-" + s + ext
    return fn + "-" + s

# Stamp with the date
def datestamp(fn): return stamp(fn, time.strftime("%d-%m-%y"))

# A stamp based on file contents, appending the first eight hex digits of the Whirlpool hash.
# Inspired by a similar system on Derpibooru (anonymous users there are differentiated by four hex digits).
def hashstamp(fn):
    h = hashlib.new("whirlpool")
    try:
        f = open(fn, 'rb')
        raw = f.read()
        h.update(raw)
        f.close()
    except FileNotFoundError:
        h.update(bytes(fn, "utf-8"))
    return stamp(fn, h.hexdigest()[:8])

# Generates my logo with coordinates rounded to n // 2 decimal places
def taxellogo(n = 20):
    from decimal import Decimal as D, getcontext
    getcontext().prec = n
    k, l, m = D(13.5).sqrt(), D(2).sqrt(), (31 + 12 * D(3).sqrt()) / 23
    t = (69 / (4 * (1 + m * m))).sqrt()
    p, q = (l - k) / 2 - t, (l + k) / 2 - m * t
    d = [p, -q, l, -l, q, -p]
    c = [str(round(i * (D(2) / D(3)).sqrt() + 4, n // 2)) for i in d]
    return '<svg><rect fill="#230f38" width="8" height="8"/><path style="fill:none;stroke:#6dc6fb;stroke-width:.2109375;stroke-linecap:round;stroke-linejoin:round" d="M1 1 {0} 7 7"/></svg>'.format(" ".join(c))

# Opens Derpibooru image #n
def derpipic(n, canonical = True): webbrowser.open("https://derpiboo{}/".format("ru.org" if canonical else ".ru") + str(n), 2)

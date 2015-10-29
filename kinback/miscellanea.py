# Helper functions for Kinross: miscellaneous things
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

def taxellogo():
    """My classic "four lines" logo, with coordinates rounded to ten decimal places."""
    from decimal import Decimal as D, localcontext
    with localcontext() as ctx:
        ctx.prec = 20
        k, l, m = D(13.5).sqrt(), D(2).sqrt(), (31 + 12 * D(3).sqrt()) / 23
        t = (69 / (4 * (1 + m * m))).sqrt()
        p, q = (l - k) / 2 - t, (l + k) / 2 - m * t
        d = [p, -q, l, -l, q, -p]
        c = [str(round(i * (D(2) / D(3)).sqrt() + 4, 10)) for i in d]
    return '<svg><rect fill="#230f38" width="8" height="8"/><path style="fill:none;stroke:#6dc6fb;stroke-width:.2109375;stroke-linecap:round;stroke-linejoin:round" d="M1 1 {0} 7 7"/></svg>'.format(" ".join(c))

def derpipic(n, canonical = True):
    """Opens Derpibooru image #n."""
    import webbrowser
    webbrowser.open("https://derpiboo{}/".format("ru.org" if canonical else ".ru") + str(n), 2)

def xmlprettyprint(et):
    """Converts an XML element tree (the object) into a pretty XML representation (tab = four spaces)."""
    import xml.dom.minidom as x, xml.etree.ElementTree as t
    return x.parseString(t.tostring(et.getroot(), "unicode")).toprettyxml("  ")

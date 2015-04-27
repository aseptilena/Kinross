#!/usr/bin/env python3.4
# This generates the SVG file for my logo, the construction of which is documented in
# http://parclytaxel.tumblr.com/post/58496447207 (set g to however big you like).
# Do whatever you want with it (or the logo).
from decimal import Decimal, getcontext
g = 20
getcontext().prec = g
k, l, m = Decimal(13.5).sqrt(), Decimal(2).sqrt(), (31 + 12 * Decimal(3).sqrt()) / 23
t = (69 / (4 * (1 + m * m))).sqrt()
p, q = (l - k) / 2 - t, (l + k) / 2 - m * t
d = [p, -q, l, -l, q, -p]
c = [str(round(i * (Decimal(2) / Decimal(3)).sqrt() + 4, g // 2)) for i in d]
with open("coords.svg", 'w') as out: out.write('<svg><rect fill="#230f38" width="8" height="8"/><path style="fill:none;stroke:#6dc6fb;stroke-width:.2109375;stroke-linecap:round;stroke-linejoin:round" d="M1 1 {0} 7 7"/><svg>'.format(" ".join(c)))

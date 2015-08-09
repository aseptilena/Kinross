#!/usr/bin/env python3.4
# With output colour and overlay, compute base colour (reverse alpha compositing)
import sys, time

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " [input file]\nLines in file are formatted as RGBA colours A' L [comment]")
    sys.exit(1)

with open("bases-{0}".format(time.strftime("%Y-%m-%d-%H-%M-%S")), 'w') as z:
    def splice(c): return [int(c[2 * i:2 * i + 2], 16) / 255 for i in range(4)]
    def clip(v): return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)
    P = 1
    with open(sys.argv[1], 'r') as q:
        for n in q:
            r = n[:-1].split(" ", 2)
            c, t, l = [splice(h) for h in r[:-1]], r[-1], [0, 0, 0, 0]
            j = (c[0][3] - c[1][3]) / (1 - c[1][3])
            l = [(c[0][i] * c[0][3] - c[1][i] * c[1][3]) / (j * (1 - c[1][3])) for i in range(3)] + [j]
            o = "".join(["{0:02x}".format(round(clip(a) * 255)) for a in l])
            z.write("{0}. {1}: {2}\n".format(P, t, o))
            P += 1

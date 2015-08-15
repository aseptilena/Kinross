#!/usr/bin/env python3.4
# Reverses alpha compositing, returning the overlay L
# Input file on command line contains several lines, each of four RGBA strings:
# A A' B B' [comment]
# A + L = A', B + L = B'
# L is then printed with its position and any comments.
import sys, time

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " [input file]\nLines in file are formatted as RGBA colours A A' B B' [comment]")
    sys.exit(1)

with open("overlays-{0}".format(time.strftime("%Y-%m-%d-%H-%M-%S")), 'w') as z:
    def splice(c): return [int(c[2 * i:2 * i + 2], 16) / 255 for i in range(4)]
    def clip(v): return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)
    P = 1
    with open(sys.argv[1], 'r') as q:
        for n in q:
            r = n[:-1].split(" ", 4)
            c, t, l = [splice(h) for h in r[:-1]], r[-1], [0, 0, 0, 0]
            l0, l1 = [c[1][3] * (c[1][i] - c[0][i]) for i in range(3)], [c[3][3] * (c[3][i] - c[2][i]) for i in range(3)]
            for i in range(3):
                k = l0[i] / l1[i]
                l[i] = (k * c[2][i] - c[0][i]) / (k - 1)
                l[3] += (l0[i] / (l[i] - c[0][i]) + l1[i] / (l[i] - c[2][i])) / 6
            o = "".join(["{0:02x}".format(round(clip(a) * 255)) for a in l])
            z.write("{0}. {1}: {2}\n".format(P, t, o))
            P += 1

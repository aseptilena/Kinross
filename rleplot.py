#!/usr/bin/env python3.4
# RLE-to-SVG converter
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import sys, time

# Just draw a square for each cell. Though naive, it allows for pretty things like gaps.
# I was very bored... might delete this file once I figure out how to import modules from far and wide.
def plot(ptn, psize, col):
    path = ""
    rs, cs = len(ptn), len(ptn[0])
    for r in range(rs):
        for c in range(cs):
            if ptn[r][c]:
                path += "M{0},{1}h{2}v{2}h-{2}".format(psize * c, psize * r, psize)
    path = "<svg width=\"{2}\" height=\"{3}\"><path fill=\"{1}\" d=\"{0}\"/></svg>".format(path, col, psize * cs, psize * rs)
    with open("rle.svg".format(time.strftime("%Y-%m-%d-%H-%M-%S")), 'w') as out:
        out.write(path)

test = [[0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 1, 1],
        [0, 0, 0, 1, 0]]

psize = input("Pixel size (default 10): ")
psize = 10. if psize == "" else float(psize)
col = input("Colour of RLE (default black): ")
col = "#000" if col == "" else "#" + col
plot(test, psize, col)

    

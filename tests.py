#!/usr/bin/env python3.5
# Tests for the Kinback library. The expected output is to the right of the line or on top if too long.
from kinback.ellipse import *
from kinback.pathery import *
from kinback.affines import *

celestia = parsepath("m2.9-.4c.9-.5 1.7-.7 2 .4s1.5.8 1.2-.2c.6.7.2 1.6-.8 1.8s-1.4-1-2.8 0")
print(prettypath(celestia)) # <2.9,-.4 3.8,-.9 4.6,-1.1 4.9,0> <4.9,0 5.2,1.1 6.4,.8 6.1,-.2> <6.1,-.2 6.7,.5 6.3,1.4 5.3,1.6> <5.3,1.6 4.3,1.8 3.9,.6 2.5,1.6>
print(minmitrelimit(celestia)) # 5
print(minmitrelimit([[bezier(1, 2, 3, 4)]])) # 4; this one has no corners

bs = bezier(5j, 9+2j, 3+1j, 12+7j)
for i in range(1, 10): print(bs.invlength(bs.length(i / 10) / bs.length())) # 0.1 to 0.9
ea = elliparc(1.2, ellipse(0, 2, 1, 0), 4.7)
for i in range(1, 10): print(ea.invlength(ea.length(i / 10) / ea.length())) # ditto
bt = bezier(9+6j, 18, -7-1j, 12+7j)
print(bt.boundingbox()) # ((4.668802369589486+1.25j), (12+7j))

#                        rotate(45-10-20)scale(2)
print(minimisetransform("translate(-10,-20) scale(2) rotate(45) translate(5,10)"))
#                        rotate(180.14907 198.57083-87.73782)scale(1-1)
print(minimisetransform("matrix(-0.99999662,-0.00260176,-0.00260176,0.99999662,397.36926,-174.95871)"))
#                        rotate(194.76117 133.06281-37.451292)scale(.84795182-.84795182)
print(minimisetransform("matrix(-0.81996625,-0.2160501,-0.2160501,0.81996625,271.27629,-39.763406)"))

#!/usr/bin/env python3.5
# Tests for the Kinback library. The expected output is to the right of the line or on top if too long.
from kinback.ellipse import *
from kinback.pathery import *
from kinback.affines import *
celestia = parsepath("m2.9-.4c.9-.5 1.7-.7 2 .4s1.5.8 1.2-.2c.6.7.2 1.6-.8 1.8s-1.4-1-2.8 0")
print(prettypath(celestia)) # <2.9,-.4 3.8,-.9 4.6,-1.1 4.9,0> <4.9,0 5.2,1.1 6.4,.8 6.1,-.2> <6.1,-.2 6.7,.5 6.3,1.4 5.3,1.6> <5.3,1.6 4.3,1.8 3.9,.6 2.5,1.6>
print(minmitrelimit(celestia)) # 5
print(minmitrelimit([[bezier(1, 2, 3, 4)]])) # 4; this one has no corners
print()
bs = bezier(5j, 9+2j, 3+1j, 12+7j)
print(bs.length()) # 13.92856143150691
ea = elliparc(1.2, ellipse(0, 2, 1, 1), 4.7)
print(ea.length()) # 5.548448510448969
print(ea.boundingbox()) # ((-1.3695910868501178-1.767546393965577j), (0.8280191614035356+1.1134099403318547j))
bt = bezier(9+6j, 18, -7-1j, 12+7j)
print(bt.boundingbox()) # ((4.668802369589486+1.25j), (12+7j))

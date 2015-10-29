#!/usr/bin/env python3.5
# Tests for the Kinback library. The expected output is to the right of the line or on top if too long.
from kinback.ellipse import *
from kinback.pathery import *
from kinback.affines import *

# ((-0.5801753182779774+6.403206599624836j), (-1.2858815280829052+3.2027085369818975j), (7.325416619694055+1.6143915515721436j), (6.37498063919398+5.148446618730812j))
print(intersect_ee(ellipse(3+3j, 4, 5, 0.6), ellipse(3+4j, 7, 2, -0.2)))
print(ell5pts(3j, 3+4j, 7+2j, 5-1j, 1)) # Ellipse centred on (3.5128205128205128, 1.4871794871794872) with axes 3.9086710109630833 and 2.415497581303145, the first axis tilted by -0.24029756940360553

celestia = parsepath("m2.9-.4c.9-.5 1.7-.7 2 .4s1.5.8 1.2-.2c.6.7.2 1.6-.8 1.8s-1.4-1-2.8 0")
print(prettypath(celestia)) # <2.9,-.4 3.8,-.9 4.6,-1.1 4.9,0> <4.9,0 5.2,1.1 6.4,.8 6.1,-.2> <6.1,-.2 6.7,.5 6.3,1.4 5.3,1.6> <5.3,1.6 4.3,1.8 3.9,.6 2.5,1.6>
print(minmitrelimit(celestia)) # 5
print(minmitrelimit([[bezier(1, 2, 3, 4)]])) # 4; this one has no corners

ea = elliparc(1.2, ellipse(0, 2, 1, 0), 4.7)
print(ea.length()) # 5.548448510448969

bs = bezier(5j, 9+2j, 3+1j, 12+7j)
print(bs.inflections()) # [0.723606797749979, 0.276393202250021]
print(bs.length()) # 13.92856143150691
bt = bezier(9+6j, 18, -7-1j, 12+7j)
print(bt.boundingbox()) # ((4.668802369589486+1.25j), (12+7j))

#                        rotate(45-10-20)scale(2)
print(minimisetransform("translate(-10,-20) scale(2) rotate(45) translate(5,10)"))
#                        rotate(180.14907 198.57083-87.73782)scale(1-1)
print(minimisetransform("matrix(-0.99999662,-0.00260176,-0.00260176,0.99999662,397.36926,-174.95871)"))
#                        rotate(194.76117 133.06281-37.451292)scale(.84795182-.84795182)
print(minimisetransform("matrix(-0.81996625,-0.2160501,-0.2160501,0.81996625,271.27629,-39.763406)"))

#!/usr/bin/env python3.5
# Tests for the Kinback library. The expected output is to the right of the line or on top if too long.
from kinback.ellipse import *
from kinback.svgpath import *

# ((-0.5801753182779774+6.403206599624836j), (-1.2858815280829052+3.2027085369818975j), (7.325416619694055+1.6143915515721436j), (6.37498063919398+5.148446618730812j))
print(intersect_ee(ellipse(3+3j, 4, 5, 0.6), ellipse(3+4j, 7, 2, -0.2)))
# Ellipse centred on (3.5128205128205128, 1.4871794871794872) with axes 3.9086710109630833 and 2.415497581303145, the first axis tilted by -0.24029756940360553
print(ell5pts(3j, 3+4j, 7+2j, 5-1j, 1))
ea = elliparc(0, 2, 1, 10, 1, 0, 2+1j)
eb = elliparc(0, ellipse(0, 2, 1, 0), 3 * pi / 2 - 0.01)
print(ea.length()) # 7.376705574218604
print(eb.ell.quartrarc() * 3) # 7.266336165 410756 (GeoGebra actually gets this wrong: 7.266336165 838058)
print(eb.length()) # 7.246336415408569

celestia = "m2.9-.4c.9-.5 1.7-.7 2 .4s1.5.8 1.2-.2c.6.7.2 1.6-.8 1.8s-1.4-1-2.8 0" # This string was hoof-optimised and contains a lot of edge cases
print(prettypath(parsepath(celestia))) # <2.9,-.4 3.8,-.9 4.6,-1.1 4.9,0> <4.9,0 5.2,1.1 6.4,.8 6.1,-.2> <6.1,-.2 6.7,.5 6.3,1.4 5.3,1.6> <5.3,1.6 4.3,1.8 3.9,.6 2.5,1.6>

b = bezier(96+78j, 30+30j, 104+43j, 22+81j)
print(b.length()) # 100.86008481303311

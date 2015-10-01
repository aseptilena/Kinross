#!/usr/bin/env python3.4
# Tests for the Kinback library. The expected output is to the right of the line or on top if too long.
from kinback.ellipse import *

# ((-0.5801753182779774+6.403206599624836j), (-1.2858815280829052+3.2027085369818975j), (7.325416619694055+1.6143915515721436j), (6.37498063919398+5.148446618730812j))
print(intersect_ee(ellipse(3+3j, 4, 5, 0.6), ellipse(3+4j, 7, 2, -0.2)))
print()
# Ellipse centred on (3.5128205128205128, 1.4871794871794872) with axes 3.9086710109630833 and 2.415497581303145, the first axis tilted by -0.24029756940360553
print(ell5pts(3j, 3+4j, 7+2j, 5-1j, 1))
print()
ea = elliparc(0, 2, 1, 10, 1, 0, 2+1j)
eb = elliparc(0, ellipse(0, 2, 1, 0), 3 * pi / 2 - 0.01)
print(ea.length()) # 7.376705574218604
print(eb.ell.quartrarc() * 3) # 7.266336165410756
print(eb.length()) # 7.246336415408569

#!/usr/bin/env python3.4
# Tests for the Kinback library. The expected output is to the right of the line or on top if too long.
from kinback.ellipse import *
from kinback.rhythms import *
from kinback.beziers import *
from kinback.regexes import *

b = "m 209.76779,421.91548 c -16.7391,-4.19875 -31.71488,-11.27917 -45.20441,-27.31132 7.40155,20.02501 22.76158,30.92624 42.6733,35.80322 z m -4.57861,20.09552 c -17.7874,-2.29116 -33.76131,-8.51292 -47.93312,-22.55389 9.76068,20.04871 25.97659,28.61786 46.81246,31.25988 z m 144.6519,156.84104 c 36.0799,-257.7036 -149.67943,-280.37221 -150.81365,-137.08689 -16.00624,-0.69543 -28.75225,-4.54928 -45.93591,-16.96195 11.33117,18.62421 31.06699,27.04651 55.62079,27.40517 -3.90829,-137.38122 156.52457,-127.24989 141.12877,126.64367 z"
a = parserhythm(b)
print(a)
print(reverserhythm(a))
print()
e = ellipse(0, 4, 1, 0)
print(e.perimeter()) # 17.156843550313667
# ((-0.5801753182779774+6.403206599624836j), (-1.2858815280829052+3.2027085369818975j), (7.325416619694055+1.6143915515721436j), (6.37498063919398+5.148446618730812j))
print(intersect_ee(ellipse(3+3j, 4, 5, 0.6), ellipse(3+4j, 7, 2, -0.2)))
# Circle with centre (3.735294117647059, 2.9705882352941178) and radius 4.038097122866465
print(circ3pts(4+7j, 1, 3-1j))
# Ellipse centred on (3.5128205128205128, 1.4871794871794872) with axes 3.9086710109630833 and 2.415497581303145, the first axis tilted by -0.24029756940360553
print(ell5pts(3j, 3+4j, 7+2j, 5-1j, 1))
print()
print(floatinkrep(.00001051)) # -11e-6
y = bezier(*[3j, 3+4j, 7+2j, 5-1j, 1])
print(y(0.25)) # (2.328125+3.21875j)
print(y.d()) # <(9.0, 3.0), (12.0, -6.0), (-6.0, -9.0)>
print(y.velocity(0.5)) # (6.75-4.5j)

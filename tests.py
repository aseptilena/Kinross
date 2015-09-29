#!/usr/bin/env python3.4
# Tests for the Kinback library. The expected output is to the right of the line or on top if too long.
from kinback.ellipse import *
from kinback.beziers import *
from kinback.algebra import *

e = ellipse(0, 4, 1, 0)
print(e.perimeter()) # 17.156843550313667
# ((-0.5801753182779774+6.403206599624836j), (-1.2858815280829052+3.2027085369818975j), (7.325416619694055+1.6143915515721436j), (6.37498063919398+5.148446618730812j))
print(intersect_ee(ellipse(3+3j, 4, 5, 0.6), ellipse(3+4j, 7, 2, -0.2)))
# Circle with centre (3.735294117647059, 2.9705882352941178) and radius 4.038097122866465
print(circ3pts(4+7j, 1, 3-1j))
# Ellipse centred on (3.5128205128205128, 1.4871794871794872) with axes 3.9086710109630833 and 2.415497581303145, the first axis tilted by -0.24029756940360553
print(ell5pts(3j, 3+4j, 7+2j, 5-1j, 1))
print()
y = bezier(*[3j, 3+4j, 7+2j, 5-1j])
print(y(0.5)) # (4.375+2.5j)
print(y.split(0.5)[1]) # <(4.375, 2.5), (5.5, 1.75), (6.0, 0.5), (5.0, -1.0)>
ea = elliparc(0, 100, 50, 10, 1, 0, 100+50j)
print(ea) # {(4.7995147433659895, 51.14533946694863), 100.0, 50.0, 0.17453292519943295: 4.575886525335371 -> -0.36097503655678714}
print(ea.lenfunc(0.63)) # 71.4365914191138815696758857368943424060555160370897062766673
print()
print(adaptivesimpson(lambda x: 1 / x, 1, 100)) # should agree to 12 decimal digits with log(100): 4.60517018598810541810298923515504629290758957098279944155263

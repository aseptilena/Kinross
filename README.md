**Kinross: a vector library and assorted Python scripts for Inkscape**  
Parcly Taxel / Jeremy Tan, 2015  
[Tumblr](http://parclytaxel.tumblr.com) | [Twitter](https://twitter.com/Parcly_Taxel) | [Derpibooru](https://derpiboo.ru/profiles/Parcly+Taxel)  

**Don't say it's _My Little Pony: Friendship Is Magic_**  
…but of course it is. I once struggled to vector Princess Luna's flowing mane, so I wrote an Inkscape extension – Flevobézier – to partially automate the process, the code based on *my* thought processes when I did it myself. (That is, the combination of manual editing and intelligent code works better than either alone.) Eventually I got much better at queueing the nodes by eye and I wrote a bunch of smaller scripts for simpler tasks like computing the opacity of a breezie's wing, until I noticed that on paths affected by live path effects (LPEs) the _d_ attribute could be deleted without affecting Inkscape's ability to render it. From there sprang the star of this repository, **Rarify**, and eventually the repository itself.

Kinross is a town in Scotland whose sister Perth provided the Australian Perth's name, which is why the licence file is idiosyncratically named Perth.

**Things in the cabinet of curiosities**  
Rarify is an SVG optimiser better than the traditional [Scour](http://codedread.com/scour) in two respects: it saves more bytes and preserves editability of objects in the image (at least for Inkscape). For example, the [248702-byte SVG source](https://dl.dropboxusercontent.com/u/102416850/Luna's%20Cold%20Spot.svg) of [*Luna's Cold Spot*](https://derpiboo.ru/505397) becomes 137425 bytes (55.3%) with Scour but only 108350 bytes (43.6%) with Rarify. As Liam White once found out:

    liam@liam-Desktop:~/horses$ ~/source/Kinross/rarify.py misery.svg
    misery.svg: 0.312, 693471 -> 214049 (30.87%)

There is also a half-mathematical (vector), half-linguistic (SVG) library called the _Kinback_ which contains some of the functions Rarify uses, including an element tree parser and cleaner, as well as a script called Spallator that takes an object and scatters many instances across a canvas. Both Rarify and Spallator are to be run in a folder where the Kinback is also present; Python 3.5 is required for operation, since the long-awaited [approximate equality function](https://docs.python.org/3/library/cmath.html#cmath.isclose) arrived in that version.

**The ~~cutie map~~ path format**  
Kinross paths are lists of subpaths, which in turn are lists of two kinds of classes representing segments: Bézier curves (containing three points or complex numbers for quadratics, four points for cubics and two points for lines) and elliptical arcs (containing the source ellipse and two t-values for the endpoints). Both classes are parametrised by a parameter _t_ ∈ \[0, 1] and implement a number of common functions:
* Value at _t_ and at endpoints (0, 1)
* Splitting into two curves or arcs at _t_
* Reversed segment
* Segment length
* Tangents at _t_ and at endpoints

Closed subpaths (those with a z) have the sentinel **0** at their end, whether their defined endpoints are near each other or not.

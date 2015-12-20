**Kinross: a vector library and assorted Python scripts for Inkscape**  
Parcly Taxel / Jeremy Tan, 2015  
[Tumblr](http://parclytaxel.tumblr.com) | [Twitter](https://twitter.com/Parcly_Taxel) | [Derpibooru](https://derpiboo.ru/profiles/Parcly+Taxel)  

**Don't say it's _My Little Pony: Friendship Is Magic_**  
…but of course it is. I once struggled to vector Princess Luna's flowing mane, so I wrote an Inkscape extension – Flevobézier – to partially automate the process, the code based on my thought processes when I did it myself. (That is, the combination of manual editing and intelligent code works better than either alone.) Eventually I got much better at queueing the nodes by eye and I wrote a bunch of smaller scripts for simpler tasks like computing the opacity of a breezie's wing, until I noticed that on paths affected by live path effects (LPEs) the _d_ attribute could be deleted without affecting Inkscape's ability to render it. From there sprang the star of this repository, Rarify, and eventually the repository itself.

Kinross is a town in Scotland whose sister Perth provided the Australian Perth's name, which is why the licence file is idiosyncratically named Perth.

**Things in the cabinet of curiosities**  
Rarify (the correct spelling is rar**e**fy but it got influenced by the MLPFIM unicorn Rarity) is an SVG optimiser better than the traditional [Scour](http://codedread.com/scour) in two respects: it saves more bytes and preserves editability of objects in the image (at least for Inkscape). For example, with default settings the [248702-byte SVG source](https://dl.dropboxusercontent.com/u/102416850/Luna's%20Cold%20Spot.svg) of [*Luna's Cold Spot*](https://derpiboo.ru/505397) becomes 137656 bytes (55.3%) with Scour 0.26 but only 105904 bytes (42.6%) with Rarify. As Liam White once found out:

    liam@liam-Desktop:~/horses$ ~/source/Kinross/rarify.py misery.svg
    misery.svg: 0.312, 693471 -> 214049 (30.87%)

This script, as well as another called Spallator that scatters many instances of an object across a canvas, depends on a half-mathematical-half-linguistic library called _Kinback_; it includes among other things a full-fledged XML parser and cleaner and should be placed in the same folder. Python 3.5 is required for operation due to my use of the [isclose function](https://docs.python.org/3/library/cmath.html#cmath.isclose), liberal unpacking and floating-point infinities/NaNs that were introduced in that version.

**Path structure and functions**  
Kinross paths are lists of subpaths, which in turn are lists of two kinds of classes representing segments: Bézier curves (containing four points or complex numbers for quadratics, three points for cubics and two points for lines) and elliptical arcs (containing the ellipse on which the elliptical arc sits and two endpoint _t_-values). Both classes are parametrised by a parameter _t_ ∈ \[0, 1] and implement common segment/path functions: value at, splitting, reverse, direction at, etc. Even "hard" functions like arc length and its inverse are included for completeness – this is a _library_, right?

The z command in SVG is represented by 0 at the end of a subpath; it may be applied even if the endpoints are not close.

**(Non-fancy) mathematics**  
Some of the latest mathematics is included in the vector library, which for my purposes means developed in the 20th century or later and as far as I know is hardly implemented in other vector libraries. I use Romberg's method for numerical integration (1955), Bareiss's determinant algorithm (1968), Adlaj's iterative formula for the perimeter of an ellipse (2012) and what is possibly the greatest fluke of them all: a very simple way of computing the parameters of self-intersection in a cubic Bézier curve that does so _which I had to work out myself_. This last formula came about after I read about [the "successes" achieved by some Hunt Chang in this field](https://sites.google.com/site/curvesintersection) – nobody listened to him, of course, because he did not publish his results.

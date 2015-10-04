**Kinross – fast Python scripts for Inkscape**  
Parcly Taxel / Jeremy Tan, 2015  
[Tumblr](http://parclytaxel.tumblr.com) | [Twitter](https://twitter.com/Parcly_Taxel) | [Derpibooru](https://derpiboo.ru/profiles/Parcly+Taxel)  

**Don't say it's _My Little Pony: Friendship Is Magic_**  
…but of course it is. Vectoring Princess Luna's flowing mane was once a tedious operation, so I wrote a Python extension – Flevobézier – for the purpose and based on how *I* did it. Such was its utility that I wrote some more vectoring scripts, which have all been collected here. They are meant to be simple and fast, which means they can also be dangerous (at least to your vectors) – do watch out.

The star of this repository is undoubtedly Rarify, an SVG optimiser better than the traditional [Scour](http://codedread.com/scour) in two respects: it saves more bytes and preserves editability of objects in the image. For example, the 248702-byte SVG source of [*Luna's Cold Spot*](https://derpiboo.ru/505397) becomes 137425 bytes (around 55%) with Scour but only 111061 bytes (45%) with Rarify. As Liam White once found out:

    liam@liam-Desktop:~/horses$ ~/source/Kinross/rarify.py misery.svg
    misery.svg: 0.312, 693471 -> 214049 (30.87%)
Kinross is a town in Scotland whose sister Perth provided the Australian Perth's name, which is why the licence file is idiosyncratically named Perth.

**Running the scripts**  
Originally there were Inkscape extensions and standalone scripts included, but because one pony could count the former's programs and the latter was a fragmented bunch of functions they were consolidated into the _Kinback_ library. The remaining "endpoint" programs are to be run in a place where the library is also present; Python 3.5 is required for operation.

**The ~~cutie map~~ path format**  
Kinross paths are lists of subpaths, which in turn are lists of two kinds of classes representing segments: Bézier curves (containing three points or complex numbers for quadratics, four points for cubics and two points for lines) and elliptical arcs (containing the source ellipse and two t-values for the endpoints). Both classes are parametrised by a parameter _t_ ∈ \[0, 1] and implement a number of common functions:
* Value at _t_ and at endpoints (0, 1)
* Splitting into two curves or arcs at _t_
* Reversed segment
* Segment length
* Tangents at _t_ and at endpoints

Closed subpaths (those with a z) have the sentinel **0** at their end, whether their defined endpoints are near each other or not.

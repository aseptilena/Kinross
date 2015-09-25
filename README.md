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
Originally there were Inkscape extensions and standalone scripts included, but because one pony could count the former's programs and the latter was a fragmented bunch of functions they were consolidated into the _Kinback_ library. The remaining "endpoint" programs are to be run in a place where the library is also present; Python 3.4 is required for operation.

**The ~~cutie map~~ path format**  
Points (nodes and handles alike) are complex numbers, exploiting Python's native support for them and simplifying things a lot. *Rhythms* are lists of points (the cardinality corresponding to a set of commands in [the SVG specifications](http://www.w3.org/TR/SVG11/paths.html) as below), subpaths are lists of rhythms and paths are lists of subpaths:
* **Z**: zero points
* **M/L/H/V**: one point (one at a subpath's start is compulsory and understood only as M)
* **Q/T**: two points
* **C/S**: three points
* **A**: four points

Every rhythm is a straight transcription of specification syntax – except the last one which is (rstart, centre, rend, end): the ellipse is defined by Rytz's construction on the first three points and its direction is always positive-angle/clockwise from rstart to rend.

**Kinross: a vector library and assorted Python scripts for Inkscape**  
Parcly Taxel / Jeremy Tan, 2016  
[Tumblr](http://parclytaxel.tumblr.com) | [Twitter](https://twitter.com/Parcly_Taxel) | [Derpibooru](https://derpiboo.ru/profiles/Parcly+Taxel)  

**Don't say it's _My Little Pony: Friendship Is Magic_**  
…but of course it is. I once struggled to vector Princess Luna's flowing mane, so I wrote an Inkscape extension – Flevobézier – to partially automate the process, the code based on my thought processes when I did it myself. (That is, the combination of manual editing and intelligent code works better than either alone.) Eventually I got much better at queueing the nodes by eye and I wrote a bunch of smaller scripts for simpler tasks like computing the opacity of a breezie's wing, until I noticed that on paths affected by live path effects (LPEs) the _d_ attribute could be deleted without affecting Inkscape's ability to render it. From there sprang the star of this repository, Rarify, and eventually the repository itself.

Kinross is a town in Scotland whose sister Perth provided the Australian Perth's name, which is why the licence file is idiosyncratically named Perth.

**Things in the cabinet of curiosities**  
Rarify (the correct spelling is rar**e**fy but it got influenced by the MLPFIM unicorn Rarity) is an SVG optimiser better than the traditional [Scour](https://github.com/codedread/scour) in two respects: it saves more bytes and preserves editability of objects in the image (at least for Inkscape). For example, the [248702-byte SVG source](https://dl.dropboxusercontent.com/u/102416850/Luna's%20Cold%20Spot.svg) of [*Luna's Cold Spot*](https://derpiboo.ru/505397) becomes 130099 bytes (52.3%) with Scour 0.32 but only 105521 bytes (42.4%) with `./rarify.py -l` (162905 bytes with default options). As Liam White once found out:

    liam@liam-Desktop:~/horses$ ~/source/Kinross/rarify.py misery.svg
    misery.svg: 0.312, 693471 -> 214049 (30.87%)

The optimiser depends on the Kinback library, which implements a full-fledged XML processor and vector API. It requires Python 3.5 beacuse of my use of several features introduced then, including the [approximate equality function](https://docs.python.org/3/library/cmath.html#cmath.isclose) and generalised parameter unpacking. The library should be placed in the same folder as the script that depends on it; the standalones folder houses independent scripts, including a pony colour generator based on [my quasi-serious research into the topic](http://parclytaxel.tumblr.com/post/136659988109).

**Fancy mathematics? (Kinback in more detail)**  
From a simple macro system for vector algebra, I expanded Kinback to include many other algebraic structures. The dependency tree is rather straightforward; fundamental algebra and regular expressions sit at the bottom, followed by ellipses and affine transformations, then the two types of SVG segments (Bézier curves up to cubics and elliptical arcs) and finally higher-order path/node processing. (I have not yet written the minimal path writer, even though the parser is already in place.) Paths are lists of subpaths, which are themselves lists of the two segments. Both classes exploit Python's duck typing by implementing common functions: point, split, direction, bounding box, even arc length. Closed paths have a 0 where they end and begin.

A characteristic of Kinback is its use of modern mathematics: Romberg's method (1955), Bareiss's determinant algorithm (1968), Adlaj's iterative formula for the perimeter of an ellipse (2012) and my short method of determining self-intersections in a cubic Bézier curve. The last item came about after I saw [the "successes" achieved by some Hunt Chang in this field](https://sites.google.com/site/curvesintersection) – nobody listened to him, of course, because he did not publish his results.

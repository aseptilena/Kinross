**Kinross: fast Python scripts for Inkscape**  
Parcly Taxel / Jeremy Tan, 2015  
[Tumblr](http://parclytaxel.tumblr.com) | [Deviant Art](https://parclytaxel.deviantart.com) | [Derpibooru](https://derpiboo.ru/profiles/51c64a35a4c72ddce400081e)  
GPLv2+ / CC BY-SA 4.0 / FAL 1.3

**Don't say it's _My Little Pony: Friendship Is Magic_**  
…but of course it is. When I was vectoring out Princess Luna's flowing mane I was frustrated at how slow I was at placing the individual nodes and handles, so I wrote a Python extension (Flevobézier) to handle this for me based on how *I* myself did it (i.e. heuristics and estimation). Such was its utility that I went on to write a few more scripts (to be used independently of Inkscape), which have all been collected here. They are meant to be simple and fast, which means they can also be dangerous (at least to your vectors) – do watch out.

The name of this repository comes from the town of Kinross in Scotland, whose "sister" Perth happens to be the etymology behind the Australian Perth's name.

**Extensions, incompatibility and everything else**  
There are two types of programs in Kinross: extensions for Inkscape (located in the extensions folder) and standalone scripts. For the former you take the \*.inx and \*.py files and place them into your custom Inkscape extensions folder (~/.config/inkscape/extensions on Linux); for the latter you just run them and follow any instructions that appear &ndash; you do need the Python 3.4 interpreter though. In the future I plan to include standalone versions of *the extensions themselves* which will be included in their folders of origin.

**The ~~cutie map~~ path format**  
The internal format Kinross uses to store paths was set in pitch (not stone) after Flevobézier; the additions and modifications mostly concern how to represent all the pen movements defined in [the SVG specifications](http://www.w3.org/TR/SVG11/paths.html).

*Points* (nodes and handles alike) are represented as two-dimensional **vector** objects from the origin to their absolute locations in the SVG coordinate space they inhabit; for example a path whose d attribute begins with "M8 3" begins with the point (8, 3). Thinking of points as vectors makes operations on them easier to understand and code, since they are often separable into x and y components. A *movement* is a list of points (one case incorporates a boolean though, see below), a *simple path* (or simpath in short) is a list of movements and a *path* is a list of simple paths – I know, this looks like what the simplepath.parsePath() function in Inkscape, right?

Of course not. The beauty of this format is that **the movements are defined by their lengths and the types of items they contain**, so no letters are necessary. None is exploited on two levels to preserve reverse conversion like None:
* **M**: end previous simpath (if any), start new simpath, one point
* **Z**: zero points, end current simpath
* **LHV**: one point (H has y-coordinate = None, V has x-coordinate = None)
* **CS**: three points (S has first point = None, None)
* **QT**: two points (T has first point = None, None)
* **A**: point + boolean + point

The points encoded by all movements except the last are obvious from the specifications; the elliptical arc movement, however, represents the arc whose centre is the first point going from the current pen position to the second point, the boolean indicating counterclockwise movement around the centre if false and vice versa. TODO

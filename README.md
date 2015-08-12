**Kinross – fast Python scripts for Inkscape**  
Parcly Taxel / Jeremy Tan, 2015  
[Tumblr](http://parclytaxel.tumblr.com) | [Twitter](https://twitter.com/Parcly_Taxel) | [Derpibooru](https://derpiboo.ru/profiles/Parcly+Taxel)  

**Don't say it's _My Little Pony: Friendship Is Magic_**  
…but of course it is. Vectoring Princess Luna's flowing mane was once a tedious operation, so I wrote a Python extension – Flevobézier – for the purpose and based on how *I* did it. Such was its utility that I wrote some more vectoring scripts, which have all been collected here. They are meant to be simple and fast, which means they can also be dangerous (at least to your vectors) – do watch out.

Kinross is a town in Scotland whose sister Perth provided the Australian Perth's name, which is why the licence file is idiosyncratically named Perth.

**Extensions, incompatibility and everything else**  
There are two types of programs in Kinross: extensions for Inkscape (located in the extensions folder) and standalone scripts (generators). For the former you take the \*.inx and \*.py files and place them into your custom Inkscape extensions folder (~/.config/inkscape/extensions on Linux); for the latter you either run the script in-place or take the *kinback* folder and place both it and the script in question in the same directory to run. Python 3.4 is required for operation.

**The ~~cutie map~~ path format**  
Points (nodes and handles alike) are complex numbers, thereby exploiting Python's native support for them and simplifying things a lot. *Rhythms* are lists of points (the cardinality corresponding to a set of commands in [the SVG specifications](http://www.w3.org/TR/SVG11/paths.html) as below), subpaths are lists of rhythms and paths are lists of subpaths:
* **Z**: zero points
* **M/L/H/V**: one point (one at a subpath's start is compulsory and understood only as M)
* **Q/T**: two points
* **C/S**: three points
* **A**: five points

For example, "M8 3" is the first rhythm of a subpath containing the point (8, 3). Every rhythm but the last is a straight transcription of specification syntax. (The elliptical arc movement, however, represents the arc whose centre is the first point going from the current pen position to the second point, the boolean indicating counterclockwise movement around the centre if false and vice versa.)

(OY OY OY)

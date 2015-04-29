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
The internal format Kinross uses to store paths was set in pitch (not stone) after Flevobézier; the additions and modifications mostly concern how to represent all the cursor movements defined in the SVG specifications.

A *node* is a two-dimensional **vector** from the origin to its absolute location in the SVG coordinate space it inhabits; for example a path whose d attribute begins with "M8 3" would be represented as a path object beginning with the node (8, 3). Thinking of points as vectors makes operations on them easier to understand and code, since they are often separable into x and y components. TODO

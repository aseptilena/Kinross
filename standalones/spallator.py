#!/usr/bin/env python3.5
# "Spallates" an input object on a canvas, generating a random pattern with a specified "density".
# Whether there is scaling, the scaling distribution if there is one (geometric or normal) and whether there is rotation may also be specified.
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import random
rgen = random.SystemRandom()
from kinback.miscellanea import xmlprettyprint
import xml.etree.ElementTree as t
# On the command line are passed two things: the file containing the object/canvas and a string detailing the density and variability info.
# Obtain the object from the canvas (the first thing that isn't a group or in <defs>)
# TODO

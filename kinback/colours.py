#!/usr/bin/env python3.4
# Helper functions for Kinross: colours in all their colours
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

# An RGBA colour is a 3- or 4-tuple of floats in [0, 1]; the lack of a fourth (alpha) value denotes full opacity (......ff).
# These can be readily converted to and from other colour spaces; operations between them are easier in this format.

aliases = {"black":   (0., 0., 0.),
           "white":   (1., 1., 1.),
           "red":     (1., 0., 0.),
           "lime":    (0., 1., 0.),
           "blue":    (0., 0., 1.),
           "yellow":  (1., 1., 0.),
           "magenta": (1., 0., 1.),
           "fuchsia": (1., 0., 1.),
           "cyan":    (0., 1., 1.),
           "aqua":    (0., 1., 1.),
           "gray":    (.5, .5, .5),
           "grey":    (.5, .5, .5),
           "maroon":  (.5, 0., 0.),
           "green":   (0., .5, 0.),
           "navy":    (0., 0., .5),
           "olive":   (.5, .5, 0.),
           "purple":  (.5, 0., .5),
           "teal":    (0., .5, .5),
           
           # TODO all the X11 colours, not just those seven characters or less
           # As listed on the Wikipedia page on them!
          "#ffa500": "orange", "#ffc0cb": "pink", "#a52a2a": "brown",
          "#c0c0c0": "silver", "#ffd700": "gold", "#f5f5dc": "beige",
          "#4b0082": "indigo", "#ee82ee": "violet", "#dda0dd": "plum"}

def toccol(s): # String to internal representation
    pass
def fromccol(c): # Internal representation to SHORTEST string
    pass

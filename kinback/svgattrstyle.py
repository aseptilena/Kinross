#!/usr/bin/env python3.4
# Helper functions for Kinross: SVG node processing
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import xml.etree.ElementTree as t
from .colours import *

# Default style properties
defstyle = {"display": "inline",
            "overflow": "visible",
            "visibility": "visible",
            "isolation": "auto",
            "enable-background": "accumulate",
            # Fill, stroke and markers
            "opacity": "1",
            "solid-opacity": "1",
            "fill": "#000",
            "fill-opacity": "1",
            "fill-rule": "nonzero",
            "stroke": "none",
            "stroke-opacity": "1",
            "stroke-width": "1",
            "stroke-linecap": "butt",
            "stroke-linejoin": "miter",
            "stroke-miterlimit": "4",
            "stroke-dasharray": "none",
            "stroke-dashoffset": "0",
            "marker": "none",
            "marker-start": "none",
            "marker-mid": "none",
            "marker-end": "none",
            # Filters and gradients
            "filter": "none",
            "flood-color": "#000",
            "flood-opacity": "1",
            "lighting-color": "#fff",
            "stop-color": "#000",
            "stop-opacity": "1",
            # Miscellaneous colouring
            "color": "#000",
            "color-interpolation": "sRGB",
            "color-interpolation-filters": "linearRGB",
            "color-rendering": "auto",
            "image-rendering": "auto",
            "mix-blend-mode": "normal",
            "paint-color-rendering": "auto",
            "paint-order": "normal",
            "shape-rendering": "auto",
            "solid-color": "#000",
            "text-rendering": "auto",
            # Clips and masks
            "clip-path": "none",
            "clip-rule": "nonzero",
            "mask": "none",
            # Text
            "baseline-shift": "baseline",
            "block-progression": "tb",
            "direction": "ltr",
            "font-family": "Sans",
            "font-feature-settings": "normal",
            "font-size": "medium",
            "font-stretch": "normal",
            "font-style": "normal",
            "font-variant": "normal",
            "font-variant-alternates": "normal",
            "font-variant-caps": "normal",
            "font-variant-ligatures": "normal",
            "font-variant-numeric": "normal",
            "font-variant-position": "normal",
            "font-weight": "normal",
            "letter-spacing": "normal",
            "line-height": "125%",
            "shape-padding": "0",
            "text-align": "start",
            "text-anchor": "start",
            "text-decoration": "none",
            "text-decoration-color": "#000",
            "text-decoration-line": "none",
            "text-decoration-style": "solid",
            "text-indent": "0",
            "text-transform": "none",
            "white-space": "normal",
            "word-spacing": "normal",
            "writing-mode": "lr-tb",
            "-inkscape-font-specification": "Sans"}

# This function performs (most of) Phase 1 (redundant attributes) and Phase 2 (redundant style properties) in the standalone Rarify script.
def nwhack(node):
    # Phase 1
    pass
    # Phase 2
    pass

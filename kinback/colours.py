#!/usr/bin/env python3.4
# Helper functions for Kinross: colours in all their colours
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com

# An RGB(A) colour is a 3- or 4-tuple of floats in [0, 1].
# These can be readily converted to and from other colour spaces; operations between them are easier in this format.

# The CSS colour alias set, ordered by how their Wikipedia page lists them
aliases = {"pink": (255, 192, 203), # Pink
           "lightpink": (255, 182, 193),
           "hotpink": (255, 105, 180),
           "deeppink": (255, 20, 147),
           "palevioletred": (219, 112, 147),
           "mediumvioletred": (199, 21, 133),
           "lightsalmon": (255, 160, 122), # Red
           "salmon": (250, 128, 114),
           "darksalmon": (233, 150, 122),
           "lightcoral": (240, 128, 128),
           "indianred": (205, 92, 92),
           "crimson": (220, 20, 60),
           "firebrick": (178, 34, 34),
           "darkred": (139, 0, 0),
           "red": (255, 0, 0),
           "orangered": (255, 69, 0), # Orange
           "tomato": (255, 99, 71),
           "coral": (255, 127, 80),
           "darkorange": (255, 140, 0),
           "orange": (255, 165, 0),
           "yellow": (255, 255, 0), # Yellow
           "lightyellow": (255, 255, 224),
           "lemonchiffon": (255, 250, 205),
           "lightgoldenrodyellow": (250, 250, 210),
           "papayawhip": (255, 239, 213),
           "moccasin": (255, 228, 181),
           "peachpuff": (255, 218, 185),
           "palegoldenrod": (238, 232, 170),
           "khaki": (240, 230, 140),
           "darkkhaki": (189, 183, 107),
           "gold": (255, 215, 0),
           "cornsilk": (255, 248, 220), # Brown
           "blanchedalmond": (255, 235, 205),
           "bisque": (255, 228, 196),
           "navajowhite": (255, 222, 173),
           "wheat": (245, 222, 179),
           "burlywood": (222, 184, 135),
           "tan": (210, 180, 140),
           "rosybrown": (188, 143, 143),
           "sandybrown": (244, 164, 96),
           "goldenrod": (218, 165, 32),
           "darkgoldenrod": (184, 134, 11),
           "peru": (205, 133, 63),
           "chocolate": (210, 105, 30),
           "saddlebrown": (139, 69, 19),
           "sienna": (160, 82, 45),
           "brown": (165, 42, 42),
           "maroon": (128, 0, 0),
           "darkolivegreen": (85, 107, 47), # Green
           "olive": (128, 128, 0),
           "olivedrab": (107, 142, 35),
           "yellowgreen": (154, 205, 50),
           "limegreen": (50, 205, 50),
           "lime": (0, 255, 0),
           "lawngreen": (124, 252, 0),
           "chartreuse": (127, 255, 0),
           "greenyellow": (173, 255, 47),
           "springgreen": (0, 255, 127),
           "mediumspringgreen": (0, 250, 154),
           "lightgreen": (144, 238, 144),
           "palegreen": (152, 251, 152),
           "darkseagreen": (143, 188, 143),
           "mediumseagreen": (60, 179, 113),
           "seagreen": (46, 139, 87),
           "forestgreen": (34, 139, 34),
           "green": (0, 128, 0),
           "darkgreen": (0, 100, 0),
           "mediumaquamarine": (102, 205, 170), # Cyan
           "cyan": (0, 255, 255),
           "aqua": (0, 255, 255),
           "lightcyan": (224, 255, 255),
           "paleturquoise": (175, 238, 238),
           "aquamarine": (127, 255, 212),
           "turquoise": (64, 224, 208),
           "mediumturquoise": (72, 209, 204),
           "darkturquoise": (0, 206, 209),
           "lightseagreen": (32, 178, 170),
           "cadetblue": (95, 158, 160),
           "darkcyan": (0, 139, 139),
           "teal": (0, 128, 128),
           "lightsteelblue": (176, 196, 222), # Blue
           "powderblue": (176, 224, 230),
           "lightblue": (173, 216, 230),
           "skyblue": (135, 206, 235),
           "lightskyblue": (135, 206, 250),
           "deepskyblue": (0, 191, 255),
           "dodgerblue": (30, 144, 255),
           "cornflowerblue": (100, 149, 237),
           "steelblue": (70, 130, 180),
           "royalblue": (65, 105, 225),
           "blue": (0, 0, 255),
           "mediumblue": (0, 0, 205),
           "darkblue": (0, 0, 139),
           "navy": (0, 0, 128),
           "midnightblue": (25, 25, 112),
           "lavender": (230, 230, 250), # Purple
           "thistle": (216, 191, 216),
           "plum": (221, 160, 221),
           "violet": (238, 130, 238),
           "orchid": (218, 112, 214),
           "magenta": (255, 0, 255),
           "fuchsia": (255, 0, 255),
           "mediumorchid": (186, 85, 211),
           "mediumpurple": (147, 112, 219),
           "blueviolet": (138, 43, 226),
           "darkviolet": (148, 0, 211),
           "darkorchid": (153, 50, 204),
           "darkmagenta": (139, 0, 139),
           "purple": (128, 0, 128),
           "indigo": (75, 0, 130),
           "darkslateblue": (72, 61, 139),
           "rebeccapurple": (102, 51, 153),
           "slateblue": (106, 90, 205),
           "mediumslateblue": (123, 104, 238),
           "white": (255, 255, 255), # Greyscale
           "snow": (255, 250, 250),
           "honeydew": (240, 255, 240),
           "mintcream": (245, 255, 250),
           "azure": (240, 255, 255),
           "aliceblue": (240, 248, 255),
           "ghostwhite": (248, 248, 255),
           "whitesmoke": (245, 245, 245),
           "seashell": (255, 245, 238),
           "beige": (245, 245, 220),
           "oldlace": (253, 245, 230),
           "floralwhite": (255, 250, 240),
           "ivory": (255, 255, 240),
           "antiquewhite": (250, 235, 215),
           "linen": (250, 240, 230),
           "lavenderblush": (255, 240, 245),
           "mistyrose": (255, 228, 225),
           "gainsboro": (220, 220, 220),
           "lightgrey": (211, 211, 211),
           "silver": (192, 192, 192),
           "darkgray": (169, 169, 169),
           "grey": (128, 128, 128),
           "gray": (128, 128, 128),
           "dimgray": (105, 105, 105),
           "lightslategray": (119, 136, 153),
           "slategray": (112, 128, 144),
           "darkslategray": (47, 79, 79),
           "black": (0, 0, 0)}

# These functions take the raw (string) value of a colour property and its corresponding opacity and convert to and from the internal representation.
# Calling fromccol(toccol(s, a)) should return the shortest possible representation of s and a; if the result's a is None it means no opacity property needs to be put.
def toccol(s, a = None):
    if s in aliases: z = [i / 255 for i in aliases[s]]
    else:
        t = s.strip('#')
        if len(t) == 3: z = [int(t[i] + t[i], 16) / 255 for i in range(3)]
        else: z = [int(t[i:i + 2], 16) / 255 for i in range(0, 6, 2)]
    if a != None and float(a) < 1.: z.append(float(a))
    return tuple(z)

def fromccol(c):
    pass

# Because I'm a completeness freak, conversions to other colour spaces.
# r = sRGB, x = CIEXYZ (1931), l = CIELAB (1976)
# Tristimulus values for D65:
xn, yn, zn = .95047, 1., 1.08883
def r2x(c):
    def linearise(k): return k / 12.92 if k <= .04045 else ((k + .055) / 1.055) ** 2.4
    cc = [linearise(k) for k in c[:3]]
    z = [.4124 * cc[0] + .3576 * cc[1] + .1805 * cc[2],
         .2126 * cc[0] + .7152 * cc[1] + .0722 * cc[2],
         .0193 * cc[0] + .1192 * cc[1] + .9505 * cc[2]]
    if len(c) == 4: z.append(c[3])
    return tuple(z)
def x2r(c):
    def delinearise(k): return 12.92 * k if k <= .0031308 else 1.055 * k ** (1 / 2.4) - 0.055
    cc = [3.2406 * c[0] - 1.5372 * c[1] -  .4986 * c[2],
          -.9689 * c[0] + 1.8758 * c[1] +  .0415 * c[2],
           .0557 * c[0] -  .2040 * c[1] + 1.0570 * c[2]]
    z = [delinearise(k) for k in cc]
    if len(c) == 4: z.append(c[3])
    return tuple(z)
def x2l(c):
    def cise(k): return k ** (1 / 3) if k > 216 / 24389 else k * 841 / 108 + 4 / 29
    z = [116 * cise(c[1] / yn) - 16,
         500 * (cise(c[0] / xn) - cise(c[1] / yn)),
         200 * (cise(c[1] / yn) - cise(c[2] / zn))]
    if len(c) == 4: z.append(c[3])
    return tuple(z)
def l2x(c):
    def icise(k): return k ** 3 if k > 6 / 29 else 108 / 841 * (k - 4 / 29)
    l0 = (c[0] + 16) / 116
    z = [xn * icise(l0 + c[1] / 500),
         yn * icise(l0),
         zn * icise(l0 - c[2] / 200)]
    if len(c) == 4: z.append(c[3])
    return tuple(z)

# Helper functions for Kinross: colours in all their colours
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
from math import isclose

# An RGBA colour is a 4-tuple of floats in [0, 1]; operations, especially alpha compositing and its reverse, are easier in this format.
# The CSS colour aliases follow in the order Wikipedia gives them:
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

# decs[n] = shortest string that when converted to float, multiplied by 255 and rounded to nearest integer (even in ties) will yield n
decs = ("0"   , ".004", ".008", ".01" , ".016", ".02" , ".024", ".028", ".03" , ".036", ".04" , ".044", ".048", ".05" , ".056", ".06" ,
        ".064", ".068", ".07" , ".076", ".08" , ".084", ".088", ".09" , ".096", ".098", ".1"  , ".104", ".11" , ".112", ".116", ".12" ,
        ".124", ".13" , ".132", ".136", ".14" , ".144", ".15" , ".152", ".156", ".16" , ".164", ".17" , ".172", ".176", ".18" , ".184",
        ".19" , ".192", ".196", ".2"  , ".204", ".208", ".21" , ".216", ".22" , ".224", ".228", ".23" , ".236", ".24" , ".244", ".248",
        ".25" , ".256", ".26" , ".264", ".268", ".27" , ".276", ".28" , ".284", ".288", ".29" , ".296", ".3"  , ".302", ".304", ".31" ,
        ".312", ".316", ".32" , ".324", ".33" , ".332", ".336", ".34" , ".344", ".35" , ".352", ".356", ".36" , ".364", ".37" , ".372",
        ".376", ".38" , ".384", ".39" , ".392", ".396", ".4"  , ".404", ".408", ".41" , ".416", ".42" , ".424", ".428", ".43" , ".436",
        ".44" , ".444", ".448", ".45" , ".456", ".46" , ".464", ".468", ".47" , ".476", ".48" , ".484", ".488", ".49" , ".496", ".498",
        ".5"  , ".504", ".51" , ".512", ".516", ".52" , ".524", ".53" , ".532", ".536", ".54" , ".544", ".55" , ".552", ".556", ".56" ,
        ".564", ".57" , ".572", ".576", ".58" , ".584", ".59" , ".592", ".596", ".6"  , ".604", ".608", ".61" , ".616", ".62" , ".624",
        ".628", ".63" , ".636", ".64" , ".644", ".648", ".65" , ".656", ".66" , ".664", ".668", ".67" , ".676", ".68" , ".684", ".688",
        ".69" , ".696", ".7"  , ".702", ".704", ".71" , ".712", ".716", ".72" , ".724", ".73" , ".732", ".736", ".74" , ".744", ".75" ,
        ".752", ".756", ".76" , ".764", ".77" , ".772", ".776", ".78" , ".784", ".79" , ".792", ".796", ".8"  , ".804", ".808", ".81" ,
        ".816", ".82" , ".824", ".828", ".83" , ".836", ".84" , ".844", ".848", ".85" , ".856", ".86" , ".864", ".868", ".87" , ".876",
        ".88" , ".884", ".888", ".89" , ".896", ".898", ".9"  , ".904", ".91" , ".912", ".916", ".92" , ".924", ".93" , ".932", ".936",
        ".94" , ".944", ".95" , ".952", ".956", ".96" , ".964", ".97" , ".972", ".976", ".98" , ".984", ".99" , ".992", ".996",    "1")

# The colour string may be # + 3/6/8 hexes, an alias or an RGB/HSL bracket. The opacity is a string representing a number in [0, 1].
# Separately specified opacities override colour string opacities.
def col2repr(col, alpha = None):
    if col in aliases: return tuple([i / 255 for i in aliases[col]] + [1. if alpha == None else float(alpha)])
    elif "(" in col:
        ket = col[4:-1].replace(" ", "").split(",")
        if ord(col[0]) & 31 == 18: # R or r of RGB
            bra = [float(c[:-1]) / 100 if ket[0][-1] == "%" else float(c) / 255 for c in ket]
        else: # HSL
            h, s, l = float(ket[0]) / 60, float(ket[1][:-1]) / 100, float(ket[2][:-1]) / 100
            c = (1 - abs(2 * l - 1)) * s
            x, m = (1 - abs(h % 2 - 1)) * c, l - c / 2
            bra = [c, x, 0.] if h % 2 < 1 else [x, c, 0.]
            for q in range(int(h / 2)): bra.insert(0, bra.pop())
            bra = [p + m for p in bra]
        return tuple(bra + [1. if alpha == None else float(alpha)])
    else:
        h, a = col.strip('#'), 1.
        if len(h) == 3: rgb = [int(2 * h[i], 16) / 255 for i in range(3)]
        else: rgb = [int(h[i:i + 2], 16) / 255 for i in range(0, 6, 2)]
        if len(h) == 8: a = int(h[6:], 16) / 255
        if alpha != None: a = float(alpha)
        return (rgb[0], rgb[1], rgb[2], a)
# four causes an eight-hex RGBA string to be returned instead of a six-hex RGB string or alias and an opacity float for pasting into Inkscape's fill/stroke dialogue.
def repr2col(tups, four = False):
    if four: return "".join(["{0:02x}".format(round(comp * 255)) for comp in tups])
    else:
        nm = None
        rgb = tuple(round(i * 255) for i in tups[:3])
        for a in aliases:
            if rgb == aliases[a]: nm = a
        if nm == "gray": nm = "grey"
        if max(i % 17 for i in rgb): code = "#" + "".join(["{:02x}".format(i) for i in rgb])
        else: code = "#" + "".join(["{:x}".format(i >> 4) for i in rgb])
        if nm == None or len(code) <= len(nm): nm = code
        return (nm, decs[round(tups[3] * 255)]) # Alpha is rounded to the smallest possible display differential, 1 / 255

# Conversions between colour spaces: sRGB, CIEXYZ, CIELAB
def xyz2rgb(c):
    def delinearise(k): return 12.92 * k if k <= .0031308 else 1.055 * k ** (1 / 2.4) - 0.055
    cc = [3.2406 * c[0] - 1.5372 * c[1] -  .4986 * c[2],
          -.9689 * c[0] + 1.8758 * c[1] +  .0415 * c[2],
           .0557 * c[0] -  .2040 * c[1] + 1.0570 * c[2]]
    z = [delinearise(k) for k in cc]
    return (z[0], z[1], z[2], c[3])
def rgb2xyz(c):
    def linearise(k): return k / 12.92 if k <= .04045 else ((k + .055) / 1.055) ** 2.4
    cc = [linearise(k) for k in c[:3]]
    z = [.4124 * cc[0] + .3576 * cc[1] + .1805 * cc[2],
         .2126 * cc[0] + .7152 * cc[1] + .0722 * cc[2],
         .0193 * cc[0] + .1192 * cc[1] + .9505 * cc[2]]
    return (z[0], z[1], z[2], c[3])
xn, yn, zn = .95047, 1., 1.08883 # D65 tristimulus values
def xyz2lab(c):
    def cise(k): return k ** (1 / 3) if k > 216 / 24389 else k * 841 / 108 + 4 / 29
    z = [116 * cise(c[1] / yn) - 16,
         500 * (cise(c[0] / xn) - cise(c[1] / yn)),
         200 * (cise(c[1] / yn) - cise(c[2] / zn))]
    return (z[0], z[1], z[2], c[3])
def lab2xyz(c):
    def icise(k): return k ** 3 if k > 6 / 29 else 108 / 841 * (k - 4 / 29)
    l0 = (c[0] + 16) / 116
    z = [xn * icise(l0 + c[1] / 500),
         yn * icise(l0),
         zn * icise(l0 - c[2] / 200)]
    return (z[0], z[1], z[2], c[3])
def rgb2lab(c): return xyz2lab(rgb2xyz(c))
def lab2rgb(c): return xyz2rgb(lab2xyz(c))

# Calculations may occasionally produce values outside [0, 1]; this function clips them to the desired range.
def clip01(c): return tuple(1. if p > 1. else (0. if p < 0. else p) for p in c)

# Three alpha-compositing functions, the latter two of which used to be in other places.
# Let the (back)ground be B, the "source" (tint) S and the result (comp) R, then
# R_A = S_A + B_A * (1 - S_A)
# R_R = (S_R * S_A + B_R * B_A * (1 - S_A)) / R_A, 0 if R_A = 0, same for the other two primaries
def alphacomp(back, tint): # tint over back = comp
    resa = back[3] * (1 - tint[3]) + tint[3]
    if isclose(resa, 0.): return (0., 0., 0., 0.)
    else: return clip01([(tint[i] * tint[3] + back[i] * back[3] * (1 - tint[3])) / resa for i in range(3)] + [resa])
# B_A = (R_A - S_A) / (1 - S_A)
# B_R = (R_R * R_A - S_R * S_A) / (R_A - S_A)
def alphaback(tint, comp):
    if isclose(tint[3], 1.): return (0., 0., 0., 1.)
    elif isclose(tint[3], comp[3]): return (0., 0., 0., 0.)
    else:
        rgb = [(comp[i] * comp[3] - tint[i] * tint[3]) / (comp[3] - tint[3]) for i in range(3)]
        rgb.append((comp[3] - tint[3]) / (1 - tint[3]))
        return clip01(rgb)
# R1_R * R1_A = S_R * S_A + B1_R * (R1_A - S_A)
#             = S_R * S_A + B1_R * R1_A - B1_R * S_A
#             = S_A * (S_R - B1_R) + B1_R * R1_A
# (R1_R - B1_R) * R1_A = S_A * (S_R - B1_R)
#                   K1 = S_A * (S_R - B1_R)
# S_R = K1 / S_A + B1_R <-----------.
#     = K2 / S_A + B2_R             |
# K1 + B1_R * S_A = K2 + B2_R * S_A |
# S_A = (K2 - K1) / (B1_R - B2_R) --.
#
# The three pairs of primaries yield at most three values for S_A.
# The average is back-substituted to find S_R values for both background/composite pairs, which are again averaged.
def alphatint(back1, comp1, back2, comp2):
    p, ta, kval, out = 0, 0., [], []
    for i in range(3):
        k1 = (comp1[i] - back1[i]) * comp1[3]
        k2 = (comp2[i] - back2[i]) * comp2[3]
        kval.append((k1, k2))
        if not isclose(back1[i], back2[i]):
            p += 1
            ta += (k2 - k1) / (back1[i] - back2[i])
    if p == 0: return (0., 0., 0., .5)
    ta /= p
    if isclose(ta, 0.): return (0., 0., 0., 0.)
    for i in range(3):
        c1 = kval[i][0] / ta + back1[i]
        c2 = kval[i][1] / ta + back2[i]
        out.append((c1 + c2) / 2)
    out.append(ta)
    return clip01(out)

#!/usr/bin/env python3.4
# Rarify, the uncouth SVG optimiser
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import sys, argparse
import xml.etree.ElementTree as t
from kinback.svgattrstyle import *
tr, rn = None, None

def expand(a): return a if ":" not in a else "{{{0}}}{1}".format(nm[a[:a.index(":")]], a[a.index(":") + 1:])
def collapse(a):
    z = a.partition("}")
    for m in nm:
        if nm[m] == z[0][1:]: return (m + ":" if m != "d" else "") + z[2]
    return a

def rarify(f, opts):
    # Currently moving to svgattrstyle ("Sweetie Belle"), please use an earlier version
    # TODO here, here
    for nv in rn.findall("sodipodi:namedview", nm): rn.remove(nv)
    if opts[0]:
        for nv in rn.findall("d:metadata", nm): rn.remove(nv)
    if opts[1]: dmrn(rn.attrib, {"height": None, "width": None, "viewBox": None})
    
    
    for n in rn.findall(".//d:clipPath/d:path", nm): # Look for "clip-rule:evenodd", keep only that
        if "clip-rule:evenodd" in n.get("style", ""): n.set("style", "clip-rule:evenodd")
        else: dmrn(n.attrib, {"style": None})
    
    # EXCEPT if the styled element represents a bespokely placed path. Then you don't do anything.
    ptemplate = rn.findall(".//d:defs/d:path", nm)
    for n in rn.findall(".//*[@style]", nm):
        
        # POINTER HERE TODO
        if n not in ptemplate:
            nwhack(n)
    
    # Phase 3: unused definitions and redundant ID removal
    # 3a: reference map with temporary IDs
    # Dictionary pairs are {id: {uses, fills, strokes, etc. referenced by that ID}}
    rd, cnt = {}, 0
    for k in rn.findall(".//*"):
        rf = {}
        # Style properties
        for a in ["fill", "stroke", "clip-path", "mask", "filter"]:
            raw = k.get("style", "").split(";")
            sty = dict([(a[:a.index(":")], a[a.index(":") + 1:]) for a in raw]) if len(raw) > 1 else {}
            rf[a] = sty[a] if a in sty else k.get(a, "")
            rf[a] = rf[a][5:-1] if rf[a].startswith("url(#") else None
        # Not style properties
        rf["tag"] = collapse(k.tag)
        tmp = k.get("{http://www.w3.org/1999/xlink}href")
        rf["use"] = tmp[1:] if tmp != None else None
        tmp = k.get("{http://www.inkscape.org/namespaces/inkscape}path-effect")
        rf["path-effect"] = tmp[1:] if tmp != None else None
        irk = k.get("id")
        if irk == None:
            while "q" + str(cnt) in rd: cnt += 1
            irk = "q" + str(cnt)
            k.set("id", irk)
        rd[irk] = rf
    # 3b: unreferenced ID removal
    ao, ro = set(rd.keys()), []
    for e in rd: ro.extend([rd[e][a] for a in ["use", "fill", "stroke", "clip-path", "mask", "filter", "path-effect"]])
    for rm in ao - set(ro):
        fat = rn.find(".//*[@id='{0}']".format(rm), nm)
        del fat.attrib["id"]
    if rn.get("id") != None: del rn.attrib["id"]
    # 3c: removal of unused <defs>
    df, ud = rn.find(".//d:defs", nm), []
    if df != None:
        for dlm in df:
            if dlm.get("id") == None: ud.append(dlm)
        for z in ud: df.remove(z)
        if not len(list(df)): rn.remove(df)
    
    # Final output
    outf = open("{0}-rarified.svg".format(f[:-4]), 'w')
    if opts[2]: outf.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
    tr.write(outf, "unicode")
    outf.close()

t.register_namespace("", "http://www.w3.org/2000/svg")
t.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
t.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
t.register_namespace("xlink", "http://www.w3.org/1999/xlink")
t.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
t.register_namespace("cc", "http://creativecommons.org/ns#")
t.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
cdl = argparse.ArgumentParser(prog="./rarify.py", description="Rarify, the uncouth SVG optimiser")
cdl.add_argument("-m", "--metadata", action="store_true", default=False, help="remove metadata")
cdl.add_argument("-d", "--dimens", action="store_true", default=False, help="remove dimensions")
cdl.add_argument("-x", "--xml", action="store_true", default=False, help="add XML header")
cdl.add_argument("files", nargs="*", help="list of files to rarify")
flags = cdl.parse_args()
opts = (flags.metadata, flags.dimens, flags.xml)
for f in flags.files:
    tr = t.parse(f)
    rn = tr.getroot()
    rarify(f, opts)

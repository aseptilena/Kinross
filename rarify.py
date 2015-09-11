#!/usr/bin/env python3.4
# Rarify, the uncouth SVG optimiser
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import os, time, argparse
from kinback.svgattrstyle import *
t, tr, rn = xml.etree.ElementTree, None, None

def rarify(f):
    global t
    tr = t.parse(f)
    rn = tr.getroot()
    begin = time.perf_counter()
    # Phase 1: semantic node operations
    for nv in rn.findall("sodipodi:namedview", nm): rn.remove(nv)
    if flags.metadata:
        for md in rn.findall("svg:metadata", nm): rn.remove(md)
    if flags.dimens: matchrm(rn.attrib, {"height": None, "width": None, "viewBox": None})
    if flags.scripts:
        for sc in rn.findall("svg:script", nm): rn.remove(sc)
    # Isolated clipping paths can be stripped of all style except for clip-rule:evenodd
    for clips in rn.findall(".//svg:clipPath/svg:path", nm):
        if "clip-rule:evenodd" in clips.get("style", ""): clips.set("style", "clip-rule:evenodd")
        else: matchrm(clips.attrib, {"style": None})
    # Bespokely placed paths and metadata are processed differently
    templates = set(rn.findall(".//svg:defs/svg:path", nm))
    mdelem = set(rn.findall(".//svg:title", nm) + rn.findall(".//svg:metadata", nm) + rn.findall(".//svg:metadata//*", nm))
    actual = set([rn] + rn.findall(".//*")) - templates - mdelem
    for n in actual: whack(n)
    for t in templates: weakwhack(t)
    # Phase 2: reference tree pruning
    # 2a: reference map with temporary IDs
    rd, cnt, reob = {}, 0, set()
    for k in rn.findall(".//*"):
        cits, irk = refsof(k), k.get("id")
        if irk == None:
            while "q" + str(cnt) in rd: cnt += 1
            irk = "q" + str(cnt)
            k.set("id", irk)
        rd[irk] = cits
        for i in cits: reob.add(cits[i])
    # 2b: unreferenced IDs
    for rm in set(rd.keys()) - reob: del rn.find(".//*[@id='{0}']".format(rm), nm).attrib["id"]
    if rn.get("id") != None: del rn.attrib["id"]
    # 2c: unused <defs>
    df, ud = rn.find(".//svg:defs", nm), []
    if df != None:
        for dlm in df:
            if dlm.get("id") == None: ud.append(dlm)
        for z in ud: df.remove(z)
        if not len(list(df)): rn.remove(df)
    # Final output
    outfn = "{0}-rarified.svg".format(f[:-4])
    outf = open(outfn, 'w')
    if flags.xml: outf.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
    tr.write(outf, "unicode")
    outf.close()
    end = time.perf_counter()
    before, after = os.path.getsize(f), os.path.getsize(outfn)
    print("{}: {:.3f}, {} -> {} ({:.2%})".format(f, end - begin, before, after, after / before))

t.register_namespace("", "http://www.w3.org/2000/svg")
t.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
t.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
t.register_namespace("xlink", "http://www.w3.org/1999/xlink")
t.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
t.register_namespace("cc", "http://creativecommons.org/ns#")
t.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
cdl = argparse.ArgumentParser(prog="./rarify.py", description="Rarify, the uncouth SVG optimiser")
cdl.add_argument("-m", "--metadata", action="store_false", default=True, help="don't remove metadata")
cdl.add_argument("-d", "--dimens", action="store_true", default=False, help="remove dimensions")
cdl.add_argument("-s", "--scripts", action="store_true", default=False, help="remove scripts")
cdl.add_argument("-x", "--xml", action="store_true", default=False, help="add XML header")
cdl.add_argument("files", nargs="*", help="list of files to rarify")
flags = cdl.parse_args()
for f in flags.files: rarify(f)

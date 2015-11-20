#!/usr/bin/env python3.5
# Rarify, the uncouth SVG optimiser
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import os, time, argparse
import xml.etree.ElementTree as t
from kinback.svgproc import *
from kinback.affines import minimisetransform, lingradcollapse
from kinback.ellipse import ellipsecollapse
tr, rn = None, None

def rarify(f):
    global t
    tr = t.parse(f)
    rn = tr.getroot()
    begin = time.perf_counter()
    # Phase 1: node tree operations
    for nv in rn.findall("sodipodi:namedview", nm_findall): rn.remove(nv)
    # Embrittlement of zero-length groups
    N = 1
    while N:
        N = 0
        sel = rn.findall(".//svg:g/..", nm_findall)
        for par in sel:
            torm = []
            for nd in list(par):
                if nd in sel: continue
                if nd.tag == "{http://www.w3.org/2000/svg}g" and not list(nd): torm.append(nd)
            for degen in torm: par.remove(degen)
            N += len(torm)
    if flags.metadata:
        for md in rn.findall("svg:metadata", nm_findall): rn.remove(md)
        for md in rn.findall("svg:title", nm_findall): rn.remove(md)
    if flags.scripts:
        for sc in rn.findall("svg:script", nm_findall): rn.remove(sc)
    # Phase 2: individual node attribute/style property processing
    # Isolated clipping paths can be stripped of all style except for clip-rule:evenodd
    for clips in rn.findall(".//svg:clipPath/svg:path", nm_findall):
        if "clip-rule:evenodd" in clips.get("style", ""): clips.set("style", "clip-rule:evenodd")
        else: matchrm(clips.attrib, {"style": None})
    # Bespokely placed paths and metadata are processed differently
    templates = set(rn.findall(".//svg:defs/svg:path", nm_findall))
    mdelem = set(rn.findall(".//svg:title", nm_findall) + rn.findall(".//svg:metadata", nm_findall) + rn.findall(".//svg:metadata//*", nm_findall))
    actual = set([rn] + rn.findall(".//*")) - templates - mdelem
    for n in actual: whack(n, flags.lpeoutput)
    for t in templates: weakwhack(t)
    if flags.dimens: matchrm(rn.attrib, {"height": None, "width": None, "viewBox": None})
    # Phase 3: reference tree pruning
    # 3a: reference map with temporary IDs
    rd, cnt, reob = {}, 0, set() # rd = reference dictionary
    for k in rn.findall(".//*"):
        cits, irk = refsof(k), k.get("id")
        if irk == None:
            while "q" + str(cnt) in rd: cnt += 1
            irk = "q" + str(cnt)
            k.set("id", irk)
        rd[irk] = cits
        for i in cits: reob.add(cits[i])
    # 3b: unreferenced IDs
    for rm in set(rd.keys()) - reob: del rn.find(".//*[@id='{0}']".format(rm), nm_findall).attrib["id"]
    if rn.get("id") != None: del rn.attrib["id"]
    # 3c: unused <defs>
    df, ud = rn.find(".//svg:defs", nm_findall), []
    if df != None:
        for dlm in df:
            if dlm.get("id") == None: ud.append(dlm)
        for z in ud: df.remove(z)
        if not len(list(df)): rn.remove(df)
    # Phase 3½: transcoding of "path circles and ellipses" (the internal representations of these objects before 0.91) into actual circles and ellipses
    for pce in rn.findall(".//svg:path[@sodipodi:type='arc']", nm_findall):
        b = path2oval(pce)
        if b != None: pce.tag, pce.attrib = b
    # Phase 4: transformation processing
    # 4a: collapsing into unstroked ellipses that reference no other objects
    for tfell in rn.findall(".//svg:ellipse[@transform]", nm_findall):
        if not refsof(tfell): ellipsecollapse(tfell)
    # 4b: simplification
    for withtf in rn.findall(".//*[@transform]", nm_findall):
        mt = minimisetransform(withtf.get("transform"))
        if mt == None: del withtf.attrib[transform]
        else: withtf.set("transform", mt)
    # Final output
    outfn = "{0}-rarified.svg".format(f[:-4])
    outf = open(outfn, 'w')
    if flags.xml: outf.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
    tr.write(outf, "unicode")
    outf.close()
    end = time.perf_counter()
    before, after = os.path.getsize(f), os.path.getsize(outfn)
    print("{}: {:.3f}, {} → {} ({:.2%})".format(f, end - begin, before, after, after / before))

for n in svgnms: t.register_namespace(n, svgnms[n])
cdl = argparse.ArgumentParser(prog="./rarify.py", description="Rarify, the uncouth SVG optimiser")
cdl.add_argument("-m", "--metadata", action="store_false", default=True, help="don't remove metadata")
cdl.add_argument("-d", "--dimens", action="store_true", default=False, help="remove dimensions")
cdl.add_argument("-s", "--scripts", action="store_false", default=True, help="don't remove scripts")
cdl.add_argument("-l", "--lpeoutput", action="store_true", default=False, help="preserve LPE output for rendering by other applications")
cdl.add_argument("-x", "--xml", action="store_true", default=False, help="add XML header")
cdl.add_argument("files", nargs="*", help="list of files to rarify")
flags = cdl.parse_args()
for f in flags.files: rarify(f)

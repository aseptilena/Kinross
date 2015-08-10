#!/usr/bin/env python3.4
# Helper functions for Kinross: timestamps for files
# Parcly Taxel / Jeremy Tan, 2015
# http://parclytaxel.tumblr.com
import time, hashlib

exts = (".svg", ".png", ".jpg", ".jpeg", ".txt", ".tar.gz", ".tar.bz2", ".tar", ".gz", ".bz2", ".7z", ".zip", ".py")
# Stamp a filename with a given string, separated by a hyphen
def stamp(fn, s):
    for ext in exts:
        if fn.endswith(ext): return fn[:-len(ext)] + "-" + s + ext
    return fn + "-" + s

# Classic timestamp (with Unix time)
def timestamp(fn): return stamp(fn, str(int(time.time())))

# A stamp based on file contents, appending the first eight hex digits of the Whirlpool hash.
# Inspired by a similar system on Derpibooru (anonymous users there are differentiated by four hex digits).
def hashstamp(fn):
    h = hashlib.new("whirlpool")
    try:
        f = open(fn, 'rb')
        raw = f.read()
        h.update(raw)
        f.close()
    except FileNotFoundError:
        h.update(bytes(fn, "utf-8"))
    return stamp(fn, h.hexdigest()[:8])

# Helper functions for Kinross: paths
# Parcly Taxel / Jeremy Tan, 2016
# https://parclytaxel.tumblr.com
from cmath import isclose
from .regexes import pcomm_re, num_re, fsmn, catn
from .segment import bezier, ellipt

strides = {'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7}
class path:
    def __init__(self, p):
        # The path class holds a list of lists for the sub-paths and the segments within them.
        # There is a separate list that holds closedness.
        self.segments, self.closed, pen = [], [], 0
        for headload in pcomm_re.finditer(p):
            head, load = headload.groups()
            typ, rel = head.upper(), head.islower()
            load = [float(n) for n in num_re.findall(load)]
            
            if typ == "M": # This is a special case, as any extra numbers after the second are equivalent to linetos
                pen = complex(load[0], load[1]) + (pen if rel else 0)
                self.segments.append([])
                self.closed.append(False)
                load = load[2:]
                while load:
                    pento = complex(load[0], load[1]) + (pen if rel else 0)
                    self.segments[-1].append(bezier(pen, pento))
                    pen, load = pento, load[2:]
            elif typ == "Z":
                self.closed[-1] = True
                start, end = self.segments[-1][0](0), self.segments[-1][-1](1)
                if not isclose(start, end): self.segments[-1].append(bezier(end, start))
                pen = start
            else:
                cmds = [load[i * strides[typ]:(i + 1) * strides[typ]] for i in range(len(load) // strides[typ])]
                for cmd in cmds:
                    if   typ == "H": params = [complex(cmd[0] + (pen.real if rel else 0), pen.imag)]
                    elif typ == "V": params = [complex(pen.real, cmd[0] + (pen.imag if rel else 0))]
                    elif typ == "A":
                        end = complex(cmd[5], cmd[6]) + (pen if rel else 0)
                        params = cmd[:5] + [end]
                    else:
                        params = [complex(cmd[2 * i], cmd[2 * i + 1]) + (pen if rel else 0) for i in range(len(cmd) // 2)]
                        if typ in "ST":
                            rpoint = pen if not self.segments[-1] else self.segments[-1][-1].svg_refl(typ)
                            params = [rpoint] + params
                    params = [pen] + params
                    self.segments[-1].append(ellipt.fromsvg_path(*params) if typ == "A" else bezier(*params))
                    pen = params[-1]

def parsepath(p):
    out = ""
    for headload in pcomm_re.finditer(p):
        head, load = headload.groups()
        typ, rel = head.upper(), head.islower()
        load = catn(*[fsmn(float(n)) for n in num_re.findall(load)])
        out += head + load
    print(out)

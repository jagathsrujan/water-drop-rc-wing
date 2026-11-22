"""Minimal DXF R12 writer/reader (mm). Entities: closed POLYLINE, CIRCLE, TEXT. No external libraries."""


def _hdr():
    return ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$INSUNITS", "70", "4", "0", "ENDSEC",
            "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "4",
            "0", "LAYER", "2", "CUT", "70", "0", "62", "1", "6", "CONTINUOUS",
            "0", "LAYER", "2", "ENGRAVE", "70", "0", "62", "5", "6", "CONTINUOUS",
            "0", "LAYER", "2", "SHEET", "70", "0", "62", "8", "6", "CONTINUOUS",
            "0", "LAYER", "2", "LABEL", "70", "0", "62", "3", "6", "CONTINUOUS",
            "0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]


class DXF:
    def __init__(self):
        self.L = _hdr()

    def poly(self, pts, layer="CUT"):
        self.L += ["0", "POLYLINE", "8", layer, "66", "1", "70", "1", "10", "0.0", "20", "0.0", "30", "0.0"]
        for x, y in pts:
            self.L += ["0", "VERTEX", "8", layer, "10", "%.4f" % x, "20", "%.4f" % y, "30", "0.0"]
        self.L += ["0", "SEQEND", "8", layer]

    def circle(self, x, y, r, layer="CUT"):
        self.L += ["0", "CIRCLE", "8", layer, "10", "%.4f" % x, "20", "%.4f" % y, "30", "0.0", "40", "%.4f" % r]

    def text(self, x, y, h, s, layer="LABEL"):
        self.L += ["0", "TEXT", "8", layer, "10", "%.3f" % x, "20", "%.3f" % y, "30", "0.0", "40", "%.2f" % h, "1", s]

    def save(self, path):
        with open(path, "w") as f:
            f.write("\n".join(self.L + ["0", "ENDSEC", "0", "EOF"]) + "\n")


def read(path):
    """Return list of entities: ('poly', layer, [(x,y)...]) / ('circle', layer, (x,y,r)) / ('text', layer, (x,y,s))."""
    tok = [l.strip() for l in open(path).read().splitlines()]
    pairs = list(zip(tok[0::2], tok[1::2]))
    ents, i, cur = [], 0, None
    while i < len(pairs):
        c, v = pairs[i]
        if c == "0" and v in ("POLYLINE", "CIRCLE", "TEXT", "VERTEX", "SEQEND"):
            if v == "POLYLINE":
                cur = ["poly", None, []]
                i += 1
                while i < len(pairs) and pairs[i][0] != "0":
                    if pairs[i][0] == "8":
                        cur[1] = pairs[i][1]
                    i += 1
                continue
            if v == "VERTEX":
                x = y = None
                i += 1
                while i < len(pairs) and pairs[i][0] != "0":
                    if pairs[i][0] == "10":
                        x = float(pairs[i][1])
                    if pairs[i][0] == "20":
                        y = float(pairs[i][1])
                    i += 1
                cur[2].append((x, y))
                continue
            if v == "SEQEND":
                ents.append(tuple(cur))
                cur = None
                i += 1
                continue
            d, lay = {}, None
            i += 1
            while i < len(pairs) and pairs[i][0] != "0":
                if pairs[i][0] == "8":
                    lay = pairs[i][1]
                d[pairs[i][0]] = pairs[i][1]
                i += 1
            if v == "CIRCLE":
                ents.append(("circle", lay, (float(d["10"]), float(d["20"]), float(d["40"]))))
            else:
                ents.append(("text", lay, (float(d["10"]), float(d["20"]), d.get("1", ""))))
            continue
        i += 1
    return ents

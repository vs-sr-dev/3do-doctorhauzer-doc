#!/usr/bin/env python3
"""ole2.py -- the OLE2 / Compound File Binary directory, for the two things on
this disc that wear it.

`D0 CF 11 E0 A1 B1 1A E1` is Microsoft's Compound File Binary format: a FAT
filesystem inside a file, with a directory of named streams and storages. It is
published -- Microsoft released the specification as [MS-CFB] -- so this reader
follows the document rather than guessing, and it validates on a specimen whose
answer is known before it is turned loose on a population.

Two populations on this object wear it:

  * 36 `.sld` files, 17,472,000 bytes, which look proprietary and are not;
  * one `Thumbs.db`, 5,632 bytes, which is Windows Explorer's thumbnail cache
    and is nobody's content at all.

What this reads, per [MS-CFB]:

  header, 512 bytes
     0   8  signature D0 CF 11 E0 A1 B1 1A E1
    24   2  minor version
    26   2  major version (3 -> 512-byte sectors, 4 -> 4096)
    30   2  sector shift, log2 of the sector size
    32   2  mini sector shift
    44   4  number of FAT sectors
    48   4  first directory sector
    56   4  mini stream cutoff (normally 4096)
    60   4  first mini-FAT sector
    68   4  first DIFAT sector
    76 436  the first 109 DIFAT entries

  directory entry, 128 bytes
     0  64  name, UTF-16LE
    64   2  name length in bytes, including the terminator
    66   1  object type: 0 unallocated, 1 storage, 2 stream, 5 root
    80  16  CLSID
   100   8  creation time, FILETIME
   108   8  modified time, FILETIME
   116   4  starting sector
   120   8  stream size

    python tools/ole2.py FILE
    python tools/ole2.py FILE --dump-stream NAME
    python tools/ole2.py DIR --census
"""

import argparse
import datetime
import os
import struct
import sys

SIG = bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1])
FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
TYPES = {0: "unalloc", 1: "storage", 2: "stream", 5: "root"}


def filetime(v):
    if not v:
        return ""
    try:
        return (datetime.datetime(1601, 1, 1)
                + datetime.timedelta(microseconds=v // 10)).strftime(
                    "%Y-%m-%d %H:%M:%S")
    except Exception:
        return "?"


class CFB:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        if self.data[:8] != SIG:
            raise ValueError("not an OLE2 compound file")
        h = self.data
        self.minor = struct.unpack_from("<H", h, 24)[0]
        self.major = struct.unpack_from("<H", h, 26)[0]
        self.ssz = 1 << struct.unpack_from("<H", h, 30)[0]
        self.mssz = 1 << struct.unpack_from("<H", h, 32)[0]
        self.nfat = struct.unpack_from("<I", h, 44)[0]
        self.dirstart = struct.unpack_from("<I", h, 48)[0]
        self.cutoff = struct.unpack_from("<I", h, 56)[0]
        self.minifat = struct.unpack_from("<I", h, 60)[0]
        self.difat_start = struct.unpack_from("<I", h, 68)[0]
        self.ndifat = struct.unpack_from("<I", h, 72)[0]
        self.difat = [struct.unpack_from("<I", h, 76 + 4 * i)[0]
                      for i in range(109)]

    def sector(self, n):
        off = (n + 1) * self.ssz
        return self.data[off:off + self.ssz]

    def fat(self):
        out = []
        for s in self.difat:
            if s in (FREESECT, ENDOFCHAIN):
                continue
            b = self.sector(s)
            for i in range(0, len(b), 4):
                out.append(struct.unpack_from("<I", b, i)[0])
        return out

    def chain(self, start, fat, limit=1 << 20):
        out = []
        s = start
        while s not in (ENDOFCHAIN, FREESECT) and len(out) < limit:
            out.append(s)
            if s >= len(fat):
                break
            s = fat[s]
        return out

    def entries(self):
        fat = self.fat()
        out = []
        for s in self.chain(self.dirstart, fat):
            b = self.sector(s)
            for i in range(0, len(b), 128):
                e = b[i:i + 128]
                if len(e) < 128:
                    break
                nl = struct.unpack_from("<H", e, 64)[0]
                typ = e[66]
                if typ == 0:
                    continue
                name = e[0:max(0, nl - 2)].decode("utf-16-le", "replace")
                clsid = e[80:96]
                out.append({
                    "name": name,
                    "type": TYPES.get(typ, str(typ)),
                    "clsid": clsid.hex(),
                    "created": filetime(struct.unpack_from("<Q", e, 100)[0]),
                    "modified": filetime(struct.unpack_from("<Q", e, 108)[0]),
                    "start": struct.unpack_from("<I", e, 116)[0],
                    "size": struct.unpack_from("<Q", e, 120)[0],
                })
        return out


def report(path, verbose=True):
    c = CFB(path)
    ents = c.entries()
    if verbose:
        print("== %s  (%d bytes) ==" % (path, len(c.data)))
        print("  version %d.%d   sector %d   mini sector %d   FAT sectors %d"
              % (c.major, c.minor, c.ssz, c.mssz, c.nfat))
        print("  directory entries: %d" % len(ents))
        print("  %-38s %-8s %10s  %-19s %s"
              % ("name", "type", "bytes", "modified", "clsid"))
        for e in ents:
            cls = e["clsid"]
            cls = "-" if cls == "0" * 32 else cls
            print("  %-38s %-8s %10d  %-19s %s"
                  % (e["name"][:38], e["type"], e["size"],
                     e["modified"] or e["created"], cls))
    return c, ents


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--ext", default=".sld")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

    if not a.census:
        report(a.path)
        return

    from collections import Counter
    shapes = Counter()
    clsids = Counter()
    names = Counter()
    n = ok = bad = 0
    total = 0
    for dp, _dn, fn in os.walk(a.path):
        for f in fn:
            if not f.lower().endswith(a.ext.lower()):
                continue
            n += 1
            p = os.path.join(dp, f)
            total += os.path.getsize(p)
            try:
                c, ents = report(p, verbose=False)
            except Exception as exc:
                bad += 1
                print("  FAILED %s: %s" % (p, exc))
                continue
            ok += 1
            shapes[tuple(sorted(e["name"] for e in ents))] += 1
            for e in ents:
                names[e["name"]] += 1
                if e["clsid"] != "0" * 32:
                    clsids[e["clsid"]] += 1
    print("files with extension %s : %d   parsed %d   failed %d   bytes %d"
          % (a.ext, n, ok, bad, total))
    print()
    print("distinct directory shapes: %d" % len(shapes))
    for sh, c in shapes.most_common(6):
        print("  x%-5d %s" % (c, " | ".join(sh)[:110]))
    print()
    print("stream/storage names, by how many files carry them:")
    for nm, c in names.most_common(20):
        print("  %-40s %5d" % (nm[:40], c))
    print()
    print("non-zero CLSIDs:")
    for cl, c in clsids.most_common(10):
        print("  %s  x%d" % (cl, c))


if __name__ == "__main__":
    main()

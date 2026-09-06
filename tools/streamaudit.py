#!/usr/bin/env python3
"""streamaudit.py -- account for every byte of a Data Streamer file by chunk
tag, and total the sound the films carry.

`cvidmovie.py` decodes the pictures and is the right tool for that. This one
answers the two questions the accounting needs and it does not decode anything:

  * **where do the bytes go**, by tag -- `SHDR`, `FILM`, `SNDS`, `FILL`, `CTRL`
    -- so that a directory's byte total can be reconciled against what the
    format explains;
  * **how much recorded sound is inside the films.** A disc's sound is not only
    what is in AIFF containers. `thesis3do.py` reads `COMM` chunks and cannot
    see a `SNDS` stream, and on a disc whose films are a third of the pressing
    that is the difference between a right number and a wrong one on the same
    question.

**And it takes `--resync`, because one film on this disc needs it.** The
Data Streamer's chunk rule is the platform's: four printable characters, a
big-endian `u32` length **including the eight-byte header**, chunks tiling the
file to its last byte. `/OrgData/stream/TRDS` carries, at offset 7,995,388, a
bare `FILL` tag with **no length field after it** -- the next four bytes are
the `FILM` tag of the chunk that follows. A walker stops there and reports
688,132 bytes it cannot explain. Stepping four bytes and carrying on chains
104 more chunks to the file's last byte exactly.

**The resync is reported, never silent.** A tool that repairs a stream without
saying so turns a defect on a pressing into a clean number, which is the
opposite of the job.

    python tools/streamaudit.py DIR --census
    python tools/streamaudit.py FILE
    python tools/streamaudit.py DIR --census --resync
"""
import argparse
import os
import struct
import sys

TAGS = ("SHDR", "FILM", "SNDS", "FILL", "CTRL", "STRM", "MDAG")


def walk(d, resync=False):
    """Return (chunks, bytes_by_tag, end, resyncs)."""
    by = {}
    i = 0
    n = 0
    fixes = []
    while i + 8 <= len(d):
        tag = d[i:i + 4]
        ln = struct.unpack_from(">I", d, i + 4)[0]
        ok = (all(32 <= c < 127 for c in tag) and 8 <= ln <= len(d) - i)
        if not ok:
            if resync and all(32 <= c < 127 for c in tag) and i + 8 <= len(d) \
                    and all(32 <= c < 127 for c in d[i + 4:i + 8]):
                # a bare tag with no length: the next four bytes are a tag too
                fixes.append((i, tag.decode("latin-1")))
                i += 4
                continue
            break
        by[tag] = by.get(tag, 0) + ln
        i += ln
        n += 1
    return n, by, i, fixes


def sound(d, resync=False):
    """SSMP payload bytes and what the SNDS SHDR sub-chunks declare."""
    ssmp = decl = 0
    rate = bits = ch = 0
    comp = b""
    i = 0
    while i + 8 <= len(d):
        tag = d[i:i + 4]
        ln = struct.unpack_from(">I", d, i + 4)[0]
        if not (all(32 <= c < 127 for c in tag) and 8 <= ln <= len(d) - i):
            if resync and all(32 <= c < 127 for c in tag):
                i += 4
                continue
            break
        if tag == b"SNDS" and i + 64 <= len(d):
            sub = d[i + 16:i + 20]
            if sub == b"SHDR":
                bits, rate, ch = struct.unpack_from(">III", d, i + 40)
                comp = d[i + 52:i + 56]
                decl += struct.unpack_from(">I", d, i + 60)[0]
            elif sub == b"SSMP":
                ssmp += struct.unpack_from(">I", d, i + 20)[0]
        i += ln
    return ssmp, decl, bits, rate, ch, comp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--resync", action="store_true")
    ap.add_argument("--user-area", type=int, default=0,
                    help="bytes of user area, to print sound as a share of it")
    a = ap.parse_args()

    files = []
    if os.path.isdir(a.target):
        for n in sorted(os.listdir(a.target)):
            p = os.path.join(a.target, n)
            if os.path.isfile(p) and open(p, "rb").read(4) == b"SHDR":
                files.append(p)
    else:
        files = [a.target]

    if not files:
        print("REFUSED: no file in %s begins SHDR" % a.target)
        return 1

    tot_by = {}
    tot_ssmp = tot_decl = tot_size = tot_walked = 0
    nfix = 0
    print("%-8s %10s %10s %7s %10s %10s %10s %9s"
          % ("file", "bytes", "walked", "chunks", "FILM", "SNDS", "FILL",
             "SSMP"))
    for p in files:
        d = open(p, "rb").read()
        n, by, end, fixes = walk(d, a.resync)
        ssmp, decl, bits, rate, ch, comp = sound(d, a.resync)
        tot_size += len(d)
        tot_walked += end
        tot_ssmp += ssmp
        tot_decl += decl
        nfix += len(fixes)
        for k, v in by.items():
            tot_by[k] = tot_by.get(k, 0) + v
        print("%-8s %10d %10d %7d %10d %10d %10d %9d%s"
              % (os.path.basename(p), len(d), end, n,
                 by.get(b"FILM", 0), by.get(b"SNDS", 0), by.get(b"FILL", 0),
                 ssmp, "" if end == len(d) else "   <- DOES NOT CLOSE"))
        for off, tag in fixes:
            print("        RESYNCED at %d: a bare %r tag with no length field"
                  % (off, tag))
        if rate:
            print("        sound: %d-bit %d Hz x%d, compression %r, "
                  "SSMP %d %s declared %d"
                  % (bits, rate, ch, comp.decode("latin-1"), ssmp,
                     "==" if ssmp == decl else "!=", decl))

    print()
    print("files walked            : %d" % len(files))
    print("bytes in those files    : %d" % tot_size)
    print("bytes the chunks explain: %d" % tot_walked)
    print("unexplained             : %d" % (tot_size - tot_walked))
    print("resyncs performed       : %d" % nfix)
    print()
    print("by tag:")
    for k in sorted(tot_by, key=lambda t: -tot_by[t]):
        print("  %-6s %10d  %6.2f %% of the eight files"
              % (k.decode("latin-1"), tot_by[k],
                 100.0 * tot_by[k] / tot_size))
    print()
    print("recorded sound inside the films:")
    print("  SSMP sample bytes     : %d" % tot_ssmp)
    print("  SNDS SHDR declares    : %d" % tot_decl)
    print("  difference            : %d" % (tot_ssmp - tot_decl))
    if a.user_area:
        print("  as a share of the %d-byte user area : %.4f %%"
              % (a.user_area, 100.0 * tot_ssmp / a.user_area))
    return 0


if __name__ == "__main__":
    sys.exit(main())

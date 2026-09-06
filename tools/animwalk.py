#!/usr/bin/env python3
"""animwalk.py -- walk the 3DO `ANIM` / `CCB ` cel container and prove it tiles.

WHY THIS EXISTS

Four 3DO discs into this collection there was a reader for the `CCB ` drawing
primitive (`ccbread.py`) and a decoder for one cel to a PNG (`celdecode.py`),
and neither one answers the question this disc asks: **how many of the
containers close, and what is in them.** `ccbread.py census` walks a tree but
counts only CCB chunks and reports one number per file; it cannot tell you that
a file is `ANIM CCB PLUT XTRA PDAT PDAT PDAT` and that the three PDATs are three
frames.

THE CONTAINER, AND WHAT IS DERIVED HERE RATHER THAN ASSUMED

The chunk rule is INHERITED from the first disc of this collection and is
re-checked on every file here: four printable characters, big-endian u32 length
INCLUDING the eight-byte header, chunks tiling the file to its last byte with no
padding and no residue. A file that leaves one byte over is a failure and is
reported as one.

What is DERIVED on this disc:

  * a still cel is `CCB ` first; an animation is `ANIM` first, and the `ANIM`
    chunk is 0x20 or 0x30 bytes;
  * inside either, there is exactly ONE `CCB ` chunk and ONE optional `PLUT`
    and ONE optional `XTRA`, and then one or more `PDAT`;
  * **the number of `PDAT` chunks is the number of frames**, because a still
    cel has one and an animation has many;
  * the third 32-bit word of an `ANIM` chunk (offset +0x10 in the file, index 2
    counting from the first word after the eight-byte header) EQUALS the number
    of `PDAT` chunks that follow it -- **on 159 of the 180 files that have one**.
    The tool prints that fraction and does NOT name the field, because an
    identity that fails on 21 files is a description and not a definition.

What is NOT derived and is NOT claimed: the meaning of any other word of the
`ANIM` chunk, the contents of `XTRA`, and anything about the 0x30 form's four
extra words beyond the fact that they exist. `--words` prints their value
distribution so that the next disc can do better; it names nothing.

DECODING FRAMES, AND WHY THAT NEEDED THIS TOOL

`celdecode.py` decodes "the Nth cel of a file" and a cel is a `CCB ` chunk. On
this disc every container holds exactly ONE `CCB `, so `celdecode.py --all` on
a 198-frame animation reports **"1 of 1 cels decoded"** and writes one PNG. It
is not wrong; it is answering a different question.

`render` here pairs the container's single `CCB ` and `PLUT` with EACH `PDAT`
in turn, which is what the container's own shape says a frame is. The
rendering itself is `celdecode.render`, imported rather than copied, so the
pixel arithmetic stays derived in one place. **How many of the PDATs render
is a measurement in both directions and `frames --census` prints it.**

usage:
    animwalk.py census TREE            every container in a tree
    animwalk.py census TREE --words    plus the ANIM word distributions
    animwalk.py census TREE --csv F    per-file rows to a CSV
    animwalk.py dump FILE              one file, chunk by chunk
    animwalk.py frames FILE OUTDIR     every PDAT of one file as a PNG
    animwalk.py frames FILE OUTDIR --index N    just frame N
    animwalk.py frames TREE --census   render every frame of every container,
                                       write nothing, and count the failures
    animwalk.py validate               negative controls; every one MUST fail
"""
import argparse
import collections
import csv
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The two tags that may start a container. Anything else is not one of ours and
# is skipped in a census rather than counted as a failure -- an AIFF is not a
# broken cel.
HEADS = (b"ANIM", b"CCB ")

# Every tag seen inside a container on this disc. A tag outside this set is not
# an error; it is printed under `unexpected` so that a fifth disc adding one is
# visible instead of silent.
KNOWN = (b"ANIM", b"CCB ", b"PLUT", b"XTRA", b"PDAT", b"CTPT")


class Bad(Exception):
    pass


def walk(d):
    """Return [(offset, tag, length)] or raise Bad. No zero-tail tolerance:
    this container tiles exactly and a tolerance would hide the failures this
    tool exists to count."""
    off = 0
    out = []
    while off + 8 <= len(d):
        tag = d[off:off + 4]
        clen = struct.unpack(">I", d[off + 4:off + 8])[0]
        if not all(32 <= c < 127 for c in tag):
            raise Bad("tag %r at %d is not four printable characters"
                      % (tag, off))
        if clen < 8:
            raise Bad("chunk %s at %d declares length %d, minimum is 8"
                      % (tag.decode("latin1"), off, clen))
        if off + clen > len(d):
            raise Bad("chunk %s at %d declares %d bytes, %d remain"
                      % (tag.decode("latin1"), off, clen, len(d) - off))
        out.append((off, tag, clen))
        off += clen
    if off != len(d):
        raise Bad("chain ends at %d, file is %d bytes -- residue %d"
                  % (off, len(d), len(d) - off))
    return out


def anim_words(d, off, clen):
    """The 32-bit words of an ANIM chunk after its eight-byte header."""
    n = (clen - 8) // 4
    return [struct.unpack(">I", d[off + 8 + 4 * i:off + 12 + 4 * i])[0]
            for i in range(n)]


def census(tree, want_words, csvpath):
    paths = []
    for dp, dn, fn in os.walk(tree):
        for f in fn:
            paths.append(os.path.join(dp, f))
    paths.sort()

    tags = collections.Counter()
    tagbytes = collections.Counter()
    taglens = collections.defaultdict(set)
    shapes = collections.Counter()
    heads = collections.Counter()
    animlens = collections.Counter()
    words = collections.defaultdict(collections.Counter)
    frames = collections.Counter()
    rows = []
    failures = []
    nseen = ncontainer = nclosed = 0
    id_hit = id_tot = 0
    id_miss = []

    for p in paths:
        nseen += 1
        with open(p, "rb") as f:
            d = f.read()
        if d[:4] not in HEADS:
            continue
        ncontainer += 1
        rel = "/" + os.path.relpath(p, tree).replace(os.sep, "/")
        heads[d[:4]] += 1
        try:
            ch = walk(d)
        except Bad as e:
            failures.append((rel, str(e)))
            continue
        nclosed += 1
        for off, tag, clen in ch:
            tags[tag] += 1
            tagbytes[tag] += clen
            taglens[tag].add(clen)
        shapes[tuple(t for _, t, _ in ch)] += 1
        npdat = sum(1 for _, t, _ in ch if t == b"PDAT")
        frames[npdat] += 1
        w = []
        if ch[0][1] == b"ANIM":
            animlens[ch[0][2]] += 1
            w = anim_words(d, ch[0][0], ch[0][2])
            for i, v in enumerate(w):
                words[i][v] += 1
            id_tot += 1
            if len(w) > 2 and w[2] == npdat:
                id_hit += 1
            else:
                id_miss.append((rel, w[2] if len(w) > 2 else None, npdat))
        rows.append((rel, len(d), ch[0][1].decode("latin1"), len(ch), npdat,
                     w[2] if len(w) > 2 else ""))

    print("files seen in the tree                : %d" % nseen)
    print("containers (first tag ANIM or CCB )   : %d" % ncontainer)
    print("  first tag ANIM                      : %d" % heads[b"ANIM"])
    print("  first tag CCB                       : %d" % heads[b"CCB "])
    print("closing at residue zero               : **%d of %d**"
          % (nclosed, ncontainer))
    print("failing to close                      : %d" % len(failures))
    for rel, why in failures:
        print("    %-46s %s" % (rel, why))
    print()

    print("CHUNK INVENTORY, over the %d containers that close" % nclosed)
    print("  %-6s %8s %14s   lengths" % ("tag", "count", "bytes"))
    total = 0
    for tag, n in tags.most_common():
        total += tagbytes[tag]
        ls = sorted(taglens[tag])
        shown = (", ".join(str(x) for x in ls) if len(ls) <= 4
                 else "%d distinct, %d..%d" % (len(ls), ls[0], ls[-1]))
        print("  %-6s %8d %14d   %s"
              % (tag.decode("latin1"), n, tagbytes[tag], shown))
    print("  %-6s %8d %14d" % ("TOTAL", sum(tags.values()), total))
    unexpected = [t for t in tags if t not in KNOWN]
    print("  unexpected tags: %s"
          % (", ".join(sorted(t.decode("latin1") for t in unexpected))
             or "none"))
    print()

    print("PDAT COUNT PER CONTAINER -- one PDAT is one frame")
    for n in sorted(frames):
        print("  %4d PDAT : %d files" % (n, frames[n]))
    print("  containers with exactly one PDAT : %d of %d"
          % (frames[1], nclosed))
    print()

    print("CONTAINER SHAPES, %d distinct" % len(shapes))
    for shape, n in shapes.most_common(8):
        s = " ".join(t.decode("latin1").strip() or "?" for t in shape)
        if len(shape) > 9:
            s = (" ".join(t.decode("latin1").strip()
                          for t in shape[:6])
                 + " ... +%d PDAT" % (len(shape) - 6))
        print("  %4d  %s" % (n, s))
    print()

    if id_tot:
        print("THE ONE IDENTITY THIS TOOL WILL STATE")
        print("  ANIM word 2 == number of PDAT chunks : **%d of %d**"
              % (id_hit, id_tot))
        print("  the exceptions, %d of them:" % len(id_miss))
        dirs = collections.Counter(os.path.dirname(r) for r, _, _ in id_miss)
        for dpath, n in dirs.most_common():
            print("    %-40s %d" % (dpath, n))
        for rel, w2, npdat in id_miss[:6]:
            print("    %-46s word2=%-4s PDAT=%d" % (rel, w2, npdat))
        if len(id_miss) > 6:
            print("    ... and %d more" % (len(id_miss) - 6))
        print("  ANIM chunk lengths: %s"
              % ", ".join("0x%02x x %d" % (k, v)
                          for k, v in sorted(animlens.items())))
        print()

    if want_words:
        print("ANIM WORD DISTRIBUTIONS -- printed, not named")
        for i in sorted(words):
            c = words[i]
            top = ", ".join("0x%x x %d" % (v, n) for v, n in c.most_common(3))
            print("  word %-2d  distinct %-4d  %s" % (i, len(c), top))
        print()

    if csvpath:
        with open(csvpath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["path", "bytes", "head", "chunks", "pdat", "anim_w2"])
            w.writerows(rows)
        print("per-file rows written to %s (%d rows)" % (csvpath, len(rows)))

    return nclosed == ncontainer and not failures


def dump(path):
    with open(path, "rb") as f:
        d = f.read()
    print("%s -- %d bytes, first tag %r" % (path, len(d), d[:4]))
    try:
        ch = walk(d)
    except Bad as e:
        print("REFUSED: %s" % e)
        return False
    for off, tag, clen in ch:
        line = "  %8d  %-4s  %8d" % (off, tag.decode("latin1"), clen)
        if tag == b"ANIM":
            line += "   words " + " ".join(
                "%08x" % w for w in anim_words(d, off, clen))
        print(line)
    print("  closes at residue zero, %d chunks" % len(ch))
    return True


def parts(d, ch):
    """Split a walked container into (ccb, plut, [pdat payloads]).

    The CCB and the PLUT are parsed by celdecode's own readers so that the
    field layout has exactly one definition in this toolbox.
    """
    import celdecode as cd
    ccb = plut = None
    pdats = []
    for off, tag, clen in ch:
        if tag == b"CCB ":
            ccb = cd.parse_ccb(d, off) if hasattr(cd, "parse_ccb") else None
            if ccb is None:
                import ccbread
                ccb = ccbread.parse_ccb(d, off)
        elif tag == b"PLUT":
            plut = cd.read_plut(d, off, clen)
        elif tag == b"PDAT":
            pdats.append(d[off + 8:off + clen])
    return ccb, plut, pdats


def frames(path, outdir, index, want_census):
    import celdecode as cd

    def one(p):
        with open(p, "rb") as f:
            d = f.read()
        if d[:4] not in HEADS:
            return None
        return d, walk(d)

    if want_census:
        paths = []
        for dp, dn, fn in os.walk(path):
            for f in fn:
                paths.append(os.path.join(dp, f))
        paths.sort()
        nfile = nframe = nok = 0
        why = collections.Counter()
        badfiles = []
        for p in paths:
            got = one(p)
            if got is None:
                continue
            d, ch = got
            nfile += 1
            ccb, plut, pdats = parts(d, ch)
            fails = 0
            for pd in pdats:
                nframe += 1
                try:
                    cd.render(ccb, plut, pd)
                    nok += 1
                except Exception as e:
                    fails += 1
                    why[type(e).__name__ + ": " + str(e)[:60]] += 1
            if fails:
                rel = "/" + os.path.relpath(p, path).replace(os.sep, "/")
                badfiles.append((rel, fails, len(pdats)))
        print("containers rendered      : %d" % nfile)
        print("PDAT chunks (frames)     : %d" % nframe)
        print("frames that render       : **%d of %d**" % (nok, nframe))
        print("frames that do not       : %d" % (nframe - nok))
        for rel, f, n in badfiles[:20]:
            print("    %-46s %d of %d" % (rel, f, n))
        if len(badfiles) > 20:
            print("    ... and %d more files" % (len(badfiles) - 20))
        for reason, n in why.most_common(6):
            print("    %-60s x %d" % (reason, n))
        return nok == nframe

    got = one(path)
    if got is None:
        raise SystemExit("animwalk: %r does not begin ANIM or CCB " % path)
    d, ch = got
    ccb, plut, pdats = parts(d, ch)
    if ccb is None:
        raise SystemExit("animwalk: %r has no CCB chunk" % path)
    os.makedirs(outdir, exist_ok=True)
    want = range(len(pdats)) if index is None else [index]
    ok = True
    for i in want:
        if i >= len(pdats):
            raise SystemExit("animwalk: frame %d of %d" % (i, len(pdats)))
        try:
            w, h, rgb = cd.render(ccb, plut, pdats[i])
        except Exception as e:
            print("  frame %3d  FAILED: %s" % (i, e))
            ok = False
            continue
        out = os.path.join(outdir, "%03d_%dx%d_%dbpp.png"
                           % (i, w, h, ccb["bpp"]))
        cd.png(out, w, h, rgb)
        print("  frame %3d  %dx%d %dbpp packed=%s -> %s"
              % (i, w, h, ccb["bpp"], ccb["packed"], os.path.basename(out)))
    print("%d PDAT chunks in %s" % (len(pdats), os.path.basename(path)))
    return ok


def validate():
    """Negative controls. Every one MUST be refused; a pass here is a failure
    of the tool and the exit code says so."""
    cases = [
        ("2,048 zero bytes", b"\0" * 2048),
        ("the string iamaduck, 2,048 bytes", b"iamaduck" * 256),
        ("a chunk declaring more than the file holds",
         b"CCB \x00\x00\x10\x00" + b"\0" * 72),
        ("a chunk of length 4", b"CCB \x00\x00\x00\x04" + b"\0" * 72),
        ("a tag that is not printable", b"\x01\x02\x03\x04\x00\x00\x00\x10"
         + b"\0" * 8),
        ("a container with one byte of residue",
         b"CCB \x00\x00\x00\x50" + b"\0" * 72 + b"\x00"),
        ("an AIFF", b"FORM\x00\x00\x00\x12AIFFCOMM" + b"\0" * 10),
    ]
    ok = True
    for name, data in cases:
        try:
            walk(data)
            print("FAIL: %-44s ACCEPTED and should not have been" % name)
            ok = False
        except Bad as e:
            print("ok  : %-44s refused -- %s" % (name, e))
    # one positive control, so that a tool that refuses everything fails too
    good = (b"CCB \x00\x00\x00\x50" + b"\0" * 72
            + b"PDAT\x00\x00\x00\x0c" + b"\0" * 4)
    try:
        ch = walk(good)
        print("ok  : %-44s accepted, %d chunks"
              % ("positive control (CCB + PDAT)", len(ch)))
    except Bad as e:
        print("FAIL: positive control refused -- %s" % e)
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("census")
    c.add_argument("tree")
    c.add_argument("--words", action="store_true")
    c.add_argument("--csv")
    d = sub.add_parser("dump")
    d.add_argument("file")
    fp = sub.add_parser("frames")
    fp.add_argument("file")
    fp.add_argument("outdir", nargs="?")
    fp.add_argument("--index", type=int)
    fp.add_argument("--census", action="store_true")
    sub.add_parser("validate")
    a = ap.parse_args()

    if a.cmd == "census":
        if not os.path.isdir(a.tree):
            raise SystemExit("animwalk: census takes a DIRECTORY, and %r is "
                             "not one. (celdecode.py's ninth inherited defect "
                             "is exactly this, unguarded.)" % a.tree)
        ok = census(a.tree, a.words, a.csv)
    elif a.cmd == "dump":
        if os.path.isdir(a.file):
            raise SystemExit("animwalk: dump takes a FILE, and %r is a "
                             "directory." % a.file)
        ok = dump(a.file)
    elif a.cmd == "frames":
        if a.census:
            if not os.path.isdir(a.file):
                raise SystemExit("animwalk: frames --census takes a DIRECTORY")
        else:
            if os.path.isdir(a.file):
                raise SystemExit("animwalk: frames takes a FILE unless "
                                 "--census is given")
            if not a.outdir:
                raise SystemExit("animwalk: frames FILE needs an OUTDIR")
        ok = frames(a.file, a.outdir, a.index, a.census)
    else:
        ok = validate()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

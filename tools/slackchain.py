#!/usr/bin/env python3
"""slackchain.py -- does an unowned region read as ONE thing or as fragments?

THE QUESTION THIS ANSWERS. A region of a disc image that no file owns has two
very different explanations, and they make different predictions:

  * **one contiguous object** -- the image was laid over a medium that already
    held something, the builder wrote only the front of it, and the tail is the
    old content read straight through. Then text runs should CROSS sector
    boundaries at close to the rate they cross any other 2,048-byte boundary,
    because there is no boundary there at all;
  * **many fragments** -- the region is unallocated blocks of a file system,
    gathered from wherever they happened to be. Then sector boundaries are
    also allocation boundaries and runs should stop at them far more often
    than chance.

THE MEASURE. For each pair of adjacent 2,048-byte blocks, ask whether a
printable run of at least six characters spans the join. Compare that rate
with the rate at which runs cross an arbitrary interior offset of the same
block -- the interior rate is the control, taken from the same bytes, and it
is what a boundary that is not a boundary looks like.

    crossing rate at the join      / crossing rate at an interior offset

A ratio near 1.00 says the sector boundaries are invisible to the content and
the region is continuous. A ratio near 0 says the content stops at every
boundary and the region is a heap of unrelated blocks.

It also classifies every block -- zero, text-heavy, binary -- and reports the
runs of each class, because "one contiguous object" and "one contiguous object
containing both a documentation file and a library" are different claims.

REFUSAL: a file whose length is not a multiple of the block size, or a file of
under two blocks, is refused with exit status 2. `--validate` builds both
populations and requires the tool to tell them apart.

usage:
    slackchain.py REGION.bin [--block 2048]
    slackchain.py --validate
"""
import argparse
import os
import re
import sys

RUN = re.compile(rb"[ -~]{6,}")


class Refused(Exception):
    pass


def spans(data, block, at):
    """How many block joins have a printable run of >= 6 spanning `at` bytes
    into the block, counting a run that covers the offset with at least three
    characters on each side."""
    n = len(data) // block
    hit = 0
    for i in range(n - 1):
        off = i * block + at
        window = data[off - 8:off + 8]
        if len(window) < 16:
            continue
        m = RUN.search(window)
        if m and m.start() <= 5 and m.end() >= 11:
            hit += 1
    return hit, n - 1


def classify(data, block):
    out = []
    for i in range(len(data) // block):
        b = data[i * block:(i + 1) * block]
        if not any(b):
            out.append("zero")
            continue
        printable = sum(1 for c in b if 32 <= c < 127 or c in (9, 10, 13))
        out.append("text" if printable * 2 > block else "binary")
    return out


def runs_of(labels):
    out = []
    for i, lab in enumerate(labels):
        if out and out[-1][0] == lab:
            out[-1][2] += 1
        else:
            out.append([lab, i, 1])
    return out


def report(data, block):
    n = len(data) // block
    print("blocks                               %d of %d bytes" % (n, block))

    join_hit, join_tot = spans(data, block, 0)
    ctrl = []
    for at in (401, 809, 1213, 1619):
        h, t = spans(data, block, at)
        ctrl.append(h / t if t else 0.0)
    join = join_hit / join_tot if join_tot else 0.0
    interior = sum(ctrl) / len(ctrl)
    print()
    print("-- do printable runs cross the block joins? --------------------")
    print("  runs spanning the join               %d of %d = %.4f"
          % (join_hit, join_tot, join))
    print("  runs spanning four interior offsets  mean %.4f  (the control)"
          % interior)
    if interior > 0:
        print("  ratio join / interior                %.4f" % (join / interior))
        print("     ~1.00 = the joins are invisible, the region is continuous")
        print("     ~0.00 = content stops at every block, the region is a heap")
    print()

    labels = classify(data, block)
    counts = {k: labels.count(k) for k in ("zero", "text", "binary")}
    print("-- what the blocks are ----------------------------------------")
    for k in ("text", "binary", "zero"):
        print("  %-8s %8d  (%.4f %%)" % (k, counts[k], 100.0 * counts[k] / n))
    rr = runs_of(labels)
    print("  runs of one class                    %d" % len(rr))
    big = sorted(rr, key=lambda r: -r[2])[:10]
    print("  the ten longest:")
    for lab, start, length in big:
        print("    %-7s block %6d .. %6d   %6d blocks" %
              (lab, start, start + length - 1, length))
    return join, interior


def validate():
    import random
    random.seed(7)
    block = 2048
    words = [b"the quick brown fox jumps over the lazy dog ",
             b"Library Functions and Macros ",
             b"WATCOM C/C++ Extended Keywords "]

    # population one: one continuous document, cut into blocks
    doc = b"".join(random.choice(words) for _ in range(4000))
    doc = doc[:block * 60]
    cont = doc

    # population two: the same text, but every block truncated and padded
    frag = bytearray()
    for i in range(60):
        piece = doc[i * block:(i + 1) * block]
        frag += piece[:1400] + bytes(block - 1400)
    frag = bytes(frag)

    print("-- continuous population --------------------------------------")
    j1, i1 = report(cont, block)
    print()
    print("-- fragmented population --------------------------------------")
    j2, i2 = report(frag, block)
    print()
    r1 = j1 / i1 if i1 else 0.0
    r2 = j2 / i2 if i2 else 0.0
    ok = r1 > 0.5 and r2 < 0.1
    print("continuous ratio %.4f, fragmented ratio %.4f -- %s"
          % (r1, r2, "the tool separates them" if ok
             else "THE TOOL DOES NOT SEPARATE THEM"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("region", nargs="?")
    ap.add_argument("--block", type=int, default=2048)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if args.validate:
        return validate()
    if not args.region:
        ap.print_help()
        return 2
    try:
        data = open(args.region, "rb").read()
        if len(data) % args.block:
            raise Refused("%d bytes is not a multiple of %d"
                          % (len(data), args.block))
        if len(data) < 2 * args.block:
            raise Refused("under two blocks")
    except Refused as exc:
        print("REFUSED: %s" % exc)
        return 2
    print("=" * 66)
    print("SLACK CONTINUITY  %s" % os.path.basename(args.region))
    print("=" * 66)
    report(data, args.block)
    return 0


if __name__ == "__main__":
    sys.exit(main())

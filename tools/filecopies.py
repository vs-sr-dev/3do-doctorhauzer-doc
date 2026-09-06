#!/usr/bin/env python3
"""filecopies.py -- hash every copy of every FILE the Opera directory declares,
and measure where the copies sit.

`opercopies.py` already compares the copies of every DIRECTORY, which is what
five 3DO discs needed, because on five discs of five exactly two files had a
second copy and both of them were metadata. This disc has eighty files with up
to seven copies each and 34.3367 % of its pressing is second-or-later copies of
file content, so the questions change shape:

  * are the copies of a FILE identical? Nobody has ever asked. `opercopies.py`
    compares directory BLOCKS, and a file's copies are its own bytes;
  * WHERE are the copies? The address of every copy is in the directory record
    already, so the layout is a field read rather than a search. If the copies
    of one file are spread across the pressing, the duplication buys seek
    distance; if they are clustered, it does not;
  * do the copies land in the bands the seven root-directory copies delimit?
    The root's own copies on this disc are spread 1+1+1+1+1+1+1 where five discs
    of five clustered them, which is the thing that suggested the question.

Every count prints its denominator. A file's copy is read as `block_count`
blocks from that copy's address and truncated to `byte_count`, which is exactly
how `opera.py` reads copy 0, so a difference reported here is a difference in
the pressed bytes and not in the reader.

    python tools/filecopies.py IMAGE
    python tools/filecopies.py IMAGE --bands
    python tools/filecopies.py IMAGE --list          one record per copy
    python tools/filecopies.py IMAGE --min-copies 7
"""
import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import opera  # noqa: E402


def band_of(block, roots):
    """Which of the len(roots) bands delimited by the root copies holds block."""
    n = 0
    for i, r in enumerate(roots):
        if block >= r:
            n = i
    return n


def bundles(a):
    """Cluster every copy of every file into contiguous runs on the pressing,
    then group the runs by which files they hold.

    The question this answers is the one the copy list cannot: a file's copy
    addresses say where its own copies are, and say nothing about whether the
    same NEIGHBOURS travel with it. If a run of files is laid down together
    several times, the unit of duplication is the run and not the file, and the
    disc is a working-set layout rather than a redundancy scheme.
    """
    vol = opera.Volume(a.image, raw=a.raw, off=a.off)

    placed = []
    for e in vol.files:
        for i, c in enumerate(e.copies):
            placed.append((c, c + e.block_count, e.path, i))
    placed.sort()

    runs = []
    cur = [placed[0]]
    for p in placed[1:]:
        if p[0] <= cur[-1][1] + a.join:
            cur.append(p)
        else:
            runs.append(cur)
            cur = [p]
    runs.append(cur)

    sig = {}
    for r in runs:
        key = tuple(sorted(set(x[2] for x in r)))
        sig.setdefault(key, []).append(r)

    repeated = {k: v for k, v in sig.items() if len(v) > 1}
    single = len(sig) - len(repeated)

    print("%s" % a.image)
    print("  file placements (every copy of every file) : %d" % len(placed))
    print("  contiguous runs, joining gaps of <= %d blocks : %d"
          % (a.join, len(runs)))
    print("  distinct run contents                      : %d" % len(sig))
    print("    contents that occur once                 : %d" % single)
    print("    contents that occur more than once       : %d" % len(repeated))
    print()

    tot = sum(len(v) for v in repeated.values())
    files_in_rep = len(set(f for k in repeated for f in k))
    print("  the repeated runs hold %d distinct files and are pressed %d times"
          % (files_in_rep, tot))
    print()

    order = sorted(repeated.items(), key=lambda kv: (-len(kv[1]), -len(kv[0])))
    print("  the %d most-repeated runs:" % min(a.show, len(order)))
    for key, insts in order[:a.show]:
        starts = sorted(x[0][0] for x in insts)
        blocks = insts[0][-1][1] - insts[0][0][0]
        print("    pressed %d times, %d files, %d blocks each, at %s"
              % (len(insts), len(key), blocks,
                 ", ".join(str(s) for s in starts)))
        for f in key:
            print("        %s" % f)
        print()

    hist = {}
    for key, insts in sig.items():
        hist[len(insts)] = hist.get(len(insts), 0) + 1
    print("  how often a run's contents are pressed:")
    for n in sorted(hist):
        print("    %d time(s) : %4d distinct run contents" % (n, hist[n]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--raw", type=int, default=2352)
    ap.add_argument("--off", type=int, default=16)
    ap.add_argument("--min-copies", type=int, default=2)
    ap.add_argument("--bands", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--bundles", action="store_true",
                    help="cluster every copy of every file into contiguous "
                         "runs and report the runs that repeat")
    ap.add_argument("--join", type=int, default=4,
                    help="blocks of slack allowed inside one run")
    ap.add_argument("--show", type=int, default=8,
                    help="how many bundles to print in full")
    a = ap.parse_args()

    if a.bundles:
        return bundles(a)

    vol = opera.Volume(a.image, raw=a.raw, off=a.off)
    roots = vol.label.root_copies

    multi = [e for e in vol.files if len(e.copies) >= a.min_copies]
    if not multi:
        print("REFUSED: no file declares %d or more copies" % a.min_copies)
        return 0

    print("%s" % a.image)
    print("  files in the volume            : %d" % len(vol.files))
    print("  files with >= %d copies         : %d"
          % (a.min_copies, len(multi)))
    print("  root directory copies          : %d at %s"
          % (len(roots), ", ".join(str(r) for r in roots)))
    print()

    agree = 0
    disagree = []
    copy_blocks = 0
    copy_bytes = 0
    gaps = []
    band_hits = [0] * len(roots)
    one_per_band = 0
    band_collision = 0
    hist = {}

    for e in multi:
        hashes = []
        for c in range(len(e.copies)):
            raw = vol.img.blocks(e.copies[c], e.block_count)
            hashes.append(hashlib.sha1(raw[:e.byte_count]).hexdigest())
        same = len(set(hashes)) == 1
        if same:
            agree += 1
        else:
            disagree.append((e.path, hashes))

        n = len(e.copies)
        hist[n] = hist.get(n, 0) + 1
        copy_blocks += (n - 1) * e.block_count
        copy_bytes += (n - 1) * e.block_count * 2048

        addrs = sorted(e.copies)
        for i in range(1, len(addrs)):
            gaps.append(addrs[i] - addrs[i - 1])

        bands = [band_of(b, roots) for b in e.copies]
        for b in bands:
            band_hits[b] += 1
        if len(set(bands)) == len(bands):
            one_per_band += 1
        else:
            band_collision += 1

        if a.list:
            print("  %-44s %9d B  %d copies  %s  %s"
                  % (e.path, e.byte_count, n,
                     "identical" if same else "DIFFER",
                     ",".join(str(b) for b in e.copies)))

    if a.list:
        print()

    print("  copies compared, byte for byte:")
    print("    groups whose copies are identical : %d of %d"
          % (agree, len(multi)))
    print("    groups whose copies DIFFER        : %d of %d"
          % (len(disagree), len(multi)))
    for path, hashes in disagree:
        print("      %s" % path)
        for i, h in enumerate(hashes):
            print("        copy %d  %s" % (i, h))
    print()

    print("  the histogram, by declared copy count:")
    for n in sorted(hist):
        print("    %d copies : %3d files" % (n, hist[n]))
    print()

    print("  what the second and later copies cost:")
    print("    blocks : %d" % copy_blocks)
    print("    bytes  : %d" % copy_bytes)
    print("    of the %d-sector track : %.4f %%"
          % (vol.img.sectors, 100.0 * copy_blocks / vol.img.sectors))
    print()

    if gaps:
        gaps.sort()
        print("  the gap between consecutive copies of one file, in blocks:")
        print("    gaps measured : %d" % len(gaps))
        print("    min / median / max : %d / %d / %d"
              % (gaps[0], gaps[len(gaps) // 2], gaps[-1]))
        print("    mean : %.1f" % (sum(gaps) / float(len(gaps))))
        print()

    if a.bands:
        print("  the seven bands the root copies delimit, and what lands in "
              "each:")
        for i, r in enumerate(roots):
            end = roots[i + 1] if i + 1 < len(roots) else vol.img.sectors
            print("    band %d  blocks %6d .. %6d   %4d copies"
                  % (i, r, end - 1, band_hits[i]))
        print("    copies below the first root copy are counted in band 0")
        print()
        print("    files whose copies land one per band : %d of %d"
              % (one_per_band, len(multi)))
        print("    files with two copies in one band    : %d of %d"
              % (band_collision, len(multi)))

    return 0


if __name__ == "__main__":
    sys.exit(main())

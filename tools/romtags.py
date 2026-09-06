#!/usr/bin/env python3
"""romtags.py -- read a 3DO disc's `/rom_tags` and date the pressing.

WHAT THIS FILE IS

`/rom_tags` sits at block 1 of every 3DO disc in this collection, immediately
after the volume label. It is a flat array of 32-byte records, and its size on
the four discs measured here is 96, 128, 128 and 192 bytes -- three, four, four
and six records.

Each record, as derived here:

    +0   u8   0x0f on every record of every disc, 20 of 20
    +1   u8   the record's type
    +2   u16  varies; zero on 17 of 20
    +4   u32  zero on 20 of 20
    +8   u32  field A
    +12  u32  field B
    +16..+31  zero on 20 of 20

TWO OF THE TYPES ARE DERIVED HERE, AND NEITHER IS ASSUMED

**Type 0x02 is the application, and it is named by BLOCK and not by name.**
Field A is the first block of the boot binary and field B is its length in
blocks, and that closes exactly against the file system's own directory entry
on **three of the three discs that carry the record**:

    Slayer          74,291 / 147   ==  /LaunchMe   74,291 / 147
    SSF2T          139,161 / 166   ==  /Launchme  139,161 / 166
    Wolfenstein     42,713 /  47   ==  /launchme   42,713 /  47

Three discs, **three different spellings of the same filename**, one identity
that closes on all three. Crash 'n Burn -- the launch title -- has no 0x02
record at all.

**Type 0x0c carries one 32-bit number and nothing else, and it is a date.**
The value rises monotonically across the four discs. Read as seconds since
**1904-01-01**, the Macintosh epoch, every disc's number falls AFTER that same
disc's own SDK build stamp, which is an independent clock printed in a
different file by a different tool:

    disc            0x0c value      as 1904 epoch        its own SDK stamp
    Crash 'n Burn   0xa8b496ae      1993-09-09 08:15:42  operamath 1993-08-14
    Slayer          0xaa763794      1994-08-16 09:29:56  operamath 1994-05-10
    SSF2T           0xab382bd6      1995-01-10 12:19:34  operamath 1994-05-10
    Wolfenstein 3D  0xac737cff      1995-09-06 16:29:51  startopera 1994-08-06

**Two constraints pick the epoch and both are internal to the objects.** The
first -- the disc date lands after its own SDK stamp -- is passed by 1904,
1970 and 1980 alike, and **saying so is the point**: on its own it settles
nothing. The second is that the gap is under five years, and only 1904 passes
it: the 1970 reading puts every pressing in the 2060s and the 1980 reading in
the 2070s, each about seventy-five years after the toolchain that built it.
The 1900 reading fails the first constraint on four of four, putting Crash 'n
Burn four years before its own SDK. `--epochs` prints both columns.

**This matters because the Opera file system stores no dates at all** -- no
volume timestamp, no per-file mtime -- and three sessions of this collection
have said so and stopped there. The date is not in the file system. It is in
this 128-byte file.

WHAT IS NOT DERIVED: types 0x05, 0x07, 0x0d and 0x10, and the u16 at +2. Their
fields are printed and not named.

usage:
    romtags.py FILE                   one disc's rom_tags
    romtags.py FILE --app LISTING     check the 0x02 record against an
                                      opera.py --list listing
    romtags.py --compare F1 F2 ...    several discs side by side
    romtags.py --epochs               the epoch argument, as a table
    romtags.py --validate             negative controls; must fail
"""
import argparse
import datetime
import os
import re
import struct
import sys

MAC = datetime.datetime(1904, 1, 1)

# The four discs of this collection, as (label, 0x0c value, SDK stamp date).
# The SDK stamps are quoted from the discs' own /System files and each one is
# reproducible with a string search; they are evidence, not decoration.
KNOWN = [
    ("Crash 'n Burn", 0xA8B496AE, datetime.datetime(1993, 8, 14),
     "operamath 'Sat Aug 14 15:11:26 PDT 1993'"),
    ("Slayer", 0xAA763794, datetime.datetime(1994, 5, 10),
     "operamath 'Tue May 10 21:49:54 PDT 1994'"),
    ("SSF2T", 0xAB382BD6, datetime.datetime(1994, 5, 10),
     "operamath 'Tue May 10 21:49:54 PDT 1994'"),
    ("Wolfenstein 3D", 0xAC737CFF, datetime.datetime(1994, 8, 6),
     "startopera 'v 1.27 1994/08/06 00:20:23'"),
]

EPOCHS = [
    ("1900-01-01", datetime.datetime(1900, 1, 1)),
    ("1904-01-01 (Macintosh)", datetime.datetime(1904, 1, 1)),
    ("1970-01-01 (Unix)", datetime.datetime(1970, 1, 1)),
    ("1980-01-01", datetime.datetime(1980, 1, 1)),
]


class Bad(Exception):
    pass


def records(d):
    if len(d) == 0 or len(d) % 32:
        raise Bad("%d bytes is not a whole number of 32-byte records"
                  % len(d))
    out = []
    for i in range(0, len(d), 32):
        e = d[i:i + 32]
        if e[0] != 0x0F:
            raise Bad("record %d begins 0x%02x, not 0x0f" % (i // 32, e[0]))
        w = struct.unpack(">8I", e)
        out.append(dict(index=i // 32, kind=e[1], sub=struct.unpack(">H", e[2:4])[0],
                        a=w[2], b=w[3], words=w, raw=e))
    return out


def show(path):
    with open(path, "rb") as f:
        d = f.read()
    print("%s -- %d bytes, %d records" % (path, len(d), len(d) // 32))
    for r in records(d):
        line = ("  %2d  type 0x%02x  sub 0x%04x   A %10d (0x%x)   B %10d"
                % (r["index"], r["kind"], r["sub"], r["a"], r["a"], r["b"]))
        if r["kind"] == 0x0C:
            line += "   -> %s" % (MAC + datetime.timedelta(seconds=r["a"]))
        if r["kind"] == 0x02:
            line += "   -> boot binary at block %d, %d blocks" % (r["a"], r["b"])
        tail = r["words"][4:]
        if any(tail):
            line += "   tail %s" % " ".join("%08x" % x for x in tail)
        print(line)
    return True


def check_app(path, listing):
    """The 0x02 record against an `opera.py --list` listing, by block."""
    with open(path, "rb") as f:
        recs = records(f.read())
    app = [r for r in recs if r["kind"] == 0x02]
    if not app:
        print("  no type 0x02 record on this disc -- nothing to check")
        return True
    a, b = app[0]["a"], app[0]["b"]
    hit = []
    for line in open(listing, encoding="utf-8", errors="replace"):
        # bytes, blocks, copies, first_block, type, path -- the type column is
        # a repr like b'    ' and contains spaces, so it is skipped
        # non-greedily up to the first slash, which no other column holds.
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+.*?(/.+)$",
                     line.rstrip())
        if m and int(m.group(4)) == a and int(m.group(2)) == b:
            hit.append(m.group(5))
    print("  0x02 says block %d, %d blocks" % (a, b))
    if hit:
        print("  the listing's file at that block with that length: %s"
              % ", ".join(hit))
        return True
    print("  NO FILE in the listing starts at block %d with %d blocks -- the "
          "identity FAILS on this disc" % (a, b))
    return False


def epochs():
    print("THE EPOCH ARGUMENT, and it is settled inside the objects")
    print()
    print("A disc cannot have been mastered before the SDK that built it,")
    print("and each disc's SDK stamp is an independent clock printed by a")
    print("different tool into a different file.")
    print()
    print("Two constraints, and BOTH are needed -- the first alone does not")
    print("separate 1904 from 1970 or 1980:")
    print("  (1) the disc date is AFTER that disc's own SDK stamp;")
    print("  (2) the gap is under five years, because a studio does not ship")
    print("      on a toolchain build it took half a decade to use.")
    print()
    for name, base in EPOCHS:
        ok = near = 0
        print("  epoch %s" % name)
        for label, val, sdk, src in KNOWN:
            try:
                when = base + datetime.timedelta(seconds=val)
                s = when.isoformat(" ")
            except OverflowError:
                s = "overflow"
                when = None
            good = when is not None and when > sdk
            gap = ((when - sdk).days / 365.25) if when is not None else None
            close = good and gap < 5.0
            ok += 1 if good else 0
            near += 1 if close else 0
            print("    %-16s %-21s vs SDK %s   %-9s gap %s"
                  % (label, s, sdk.date(), "after" if good else "NOT after",
                     ("%.1f y" % gap) if gap is not None else "-"))
        print("    -> (1) after the SDK stamp on **%d of 4**" % ok)
        print("    -> (2) and within five years on **%d of 4**" % near)
        print()
    print("Only the Macintosh epoch passes both on four of four, and the 3DO")
    print("SDK of this period was Macintosh-hosted -- which this disc says")
    print("three other ways: CR line endings in /AppStartup, a CR as the byte")
    print("in the four `junk` files, and three sound files left at 22,255 Hz.")
    return True


def compare(paths):
    print("%-34s %6s %7s  %-19s  %s"
          % ("file", "bytes", "records", "0x0c as 1904 epoch", "0x02 block/len"))
    for p in paths:
        with open(p, "rb") as f:
            d = f.read()
        try:
            recs = records(d)
        except Bad as e:
            print("%-34s REFUSED: %s" % (p, e))
            continue
        date = ""
        app = ""
        for r in recs:
            if r["kind"] == 0x0C:
                date = str(MAC + datetime.timedelta(seconds=r["a"]))
            if r["kind"] == 0x02:
                app = "%d / %d" % (r["a"], r["b"])
        # .../<repository>/_work/files/rom_tags -> <repository>
        label = p
        parts = os.path.normpath(p).replace("\\", "/").split("/")
        for seg in reversed(parts):
            if seg.endswith("-doc"):
                label = seg
                break
        print("%-34s %6d %7d  %-19s  %s"
              % (label[:34], len(d), len(recs), date or "-", app or "-"))
    return True


def validate():
    cases = [
        ("an empty file", b""),
        ("33 bytes", b"\x0f" + b"\0" * 32),
        ("a record not beginning 0x0f", b"\x01" + b"\0" * 31),
        ("an AIFF header", b"FORM\x00\x00\x00\x12AIFFCOMM" + b"\0" * 16),
        ("2,048 bytes of iamaduck", b"iamaduck" * 256),
    ]
    ok = True
    for name, data in cases:
        try:
            records(data)
            print("FAIL: %-34s ACCEPTED and should not have been" % name)
            ok = False
        except Bad as e:
            print("ok  : %-34s refused -- %s" % (name, e))
    good = (b"\x0f\x02\x00\x00" + b"\0" * 4 + struct.pack(">II", 74291, 147)
            + b"\0" * 16)
    try:
        r = records(good)
        print("ok  : %-34s accepted, type 0x%02x A=%d B=%d"
              % ("positive control (one 0x02 record)", r[0]["kind"],
                 r[0]["a"], r[0]["b"]))
    except Bad as e:
        print("FAIL: positive control refused -- %s" % e)
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--app", metavar="LISTING")
    ap.add_argument("--compare", nargs="+")
    ap.add_argument("--epochs", action="store_true")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    if a.validate:
        sys.exit(0 if validate() else 1)
    if a.epochs:
        sys.exit(0 if epochs() else 1)
    if a.compare:
        sys.exit(0 if compare(a.compare) else 1)
    if not a.file:
        raise SystemExit("romtags: give a file, --compare, --epochs or "
                         "--validate")
    if os.path.isdir(a.file):
        raise SystemExit("romtags: %r is a directory; give the rom_tags FILE"
                         % a.file)
    ok = show(a.file)
    if a.app:
        ok = check_app(a.file, a.app) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

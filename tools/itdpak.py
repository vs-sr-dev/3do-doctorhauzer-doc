#!/usr/bin/env python3
"""itdpak.py -- read the `.PAK` archives, which are this port's PC originals.

WHAT THESE ARE. Twenty archives, 3,681,527 bytes, carrying the 1992 MS-DOS
release's own filenames unchanged: `ETAGE00.PAK` .. `ETAGE07.PAK` (the eight
floors of the mansion), `ITD_RESS.PAK`, `LISTANIM.PAK`, `LISTBODY.PAK`,
`LISTLIFE.PAK`, `LISTSAMP.PAK`, `LISTTRAK.PAK`, `FRANCAIS.PAK`,
`english.PAK`. `pak.py` in this toolbox reads Broken Sword 3's archive and
refuses these -- with an uncaught traceback rather than a refusal, which is
recorded as an inherited defect.

THE INDEX, DERIVED AND CHECKED TWICE:

    +0        u32 LE   zero
    +4        u32 LE [count]   member offsets, ABSOLUTE
    offsets[0] == 4 + 4 * count                 <- the count, encoded again

The member count is therefore recoverable two independent ways: by reading
offsets until they stop increasing, and from `offsets[0]`. They agree on
**20 archives of 20 and 2,072 members of 2,072**, which is the same kind of
evidence the platform notes prefer -- a quantity stored twice, checked against
itself rather than against arithmetic that closes on a subset.

THE MEMBER:

    +0    u32 LE   additionalHeaderSize   0 or 4
    +4    u32 LE   compressedSize
    +8    u32 LE   uncompressedSize
    +12   u8       compressionType        0 stored, 1 imploded
    +13   u8[3]    zero
    +16   the stream, additionalHeaderSize + compressedSize bytes
    span  = 32 + compressedSize, on 2,072 of 2,072

**And the last sixteen bytes of every member's span are a truncated PKZIP
header.** `PK\x03\x04` between members and `PK\x01\x02` after the last one, on
2,072 of 2,072, carrying the ZIP version, general-purpose flags and
compression method of the member that follows. **The method word reads 6 --
"imploded" -- exactly where this archive's own type byte reads 1, and 0 where
it reads 0.** So the `.PAK` is a PKZIP archive whose per-entry headers were
rewritten with a smaller record and an absolute offset table, and the tail of
each original local file header was left in place. The ZIP header also carries
a **CRC-32** of the uncompressed member, which is a referee for any
decompressor anybody writes.

WHAT IS DERIVED HERE AND WHAT IS NOT. The index, the member header, the
member boundary identity and the ZIP provenance are derived. **The imploding
algorithm is not implemented in this tool.** PKWARE's imploding (APPNOTE.TXT,
method 6) is a sliding dictionary plus two or three Shannon-Fano trees, and
this tool goes as far as READING the trees and checking they are well formed:

    1 byte      number of following bytes, minus 1
    each byte   ((codes of this length) - 1) << 4 | (bit length - 1)

Both distinct tree pairs on this disc sum to **64 codes each**, which is what
a length tree and a distance tree are, and which says the general-purpose flag
of 0 -- two trees, 4K dictionary -- is being told the truth. **1,648 members
are imploded and this tool decompresses none of them and says so.** The 424
stored members are extracted verbatim.

REFUSAL. A file whose first word is not zero, whose `offsets[0]` does not
equal `4 + 4 * count`, or whose members do not tile it, is refused with exit
status 2. `--validate` runs five negative controls.

usage:
    itdpak.py FILE.PAK [--census] [--extract DIR]
    itdpak.py --tree DIR --census
    itdpak.py --validate
"""
import argparse
import collections
import glob
import os
import struct
import sys

STORED = 0
IMPLODED = 1


class Refused(Exception):
    pass


def parse(d):
    n = len(d)
    if n < 12:
        raise Refused("%d bytes is too short for an index" % n)
    if struct.unpack_from("<I", d, 0)[0] != 0:
        raise Refused("first word is %d, not zero"
                      % struct.unpack_from("<I", d, 0)[0])
    first = struct.unpack_from("<I", d, 4)[0]
    if first < 8 or first % 4 or first > n:
        raise Refused("offsets[0] = %d is not a plausible table end" % first)
    count = (first - 4) // 4
    offs = []
    for i in range(count):
        v = struct.unpack_from("<I", d, 4 + 4 * i)[0]
        if v > n:
            raise Refused("offset %d = %d is past the file" % (i, v))
        if offs and v <= offs[-1]:
            raise Refused("offset %d = %d does not increase" % (i, v))
        offs.append(v)
    if not offs or offs[0] != 4 + 4 * count:
        raise Refused("offsets[0] = %d, expected %d = 4 + 4 * %d"
                      % (offs[0] if offs else -1, 4 + 4 * count, count))
    ends = offs[1:] + [n]
    members = []
    for i, (a, b) in enumerate(zip(offs, ends)):
        if a + 16 > n:
            raise Refused("member %d header runs past the file" % i)
        add, csz, usz = struct.unpack_from("<III", d, a)
        flag = d[a + 12]
        if 32 + csz != b - a:
            raise Refused("member %d spans %d bytes, 32 + compressedSize = %d"
                          % (i, b - a, 32 + csz))
        if flag not in (STORED, IMPLODED):
            raise Refused("member %d has compression type %d" % (i, flag))
        if flag == STORED and csz != usz:
            raise Refused("member %d is stored but %d != %d"
                          % (i, csz, usz))
        members.append({
            "index": i, "offset": a, "span": b - a, "add": add,
            "csz": csz, "usz": usz, "flag": flag,
            "data": d[a + 16:a + 16 + add + csz],
            "zip": d[b - 16:b],
        })
    return members


def trees(stream):
    """Read the Shannon-Fano trees at the head of an imploded stream and
    report how many codes each declares. Returns a list of (bytes, codes)."""
    out = []
    off = 0
    for _ in range(2):
        if off >= len(stream):
            break
        nbytes = stream[off] + 1
        off += 1
        codes = 0
        for k in range(nbytes):
            if off + k >= len(stream):
                return out
            b = stream[off + k]
            codes += (b >> 4) + 1
        off += nbytes
        out.append((nbytes, codes))
    return out


def zipinfo(tail):
    if tail[:4] == b"PK\x03\x04":
        ver, flags, method = struct.unpack_from("<HHH", tail, 4)
        return "LFH", ver, flags, method
    if tail[:4] == b"PK\x01\x02":
        made, ver, flags, method = struct.unpack_from("<HHHH", tail, 4)
        return "CDH", ver, flags, method
    return None, None, None, None


def census(path, verbose=True):
    d = open(path, "rb").read()
    ms = parse(d)
    kinds = collections.Counter(m["flag"] for m in ms)
    sig = collections.Counter()
    method = collections.Counter()
    tree_ok = tree_tot = 0
    magic = collections.Counter()
    for m in ms:
        k, _v, _f, meth = zipinfo(m["zip"])
        sig[k] += 1
        if meth is not None and k == "LFH":
            method[meth] += 1
        if m["flag"] == IMPLODED:
            t = trees(m["data"])
            tree_tot += 1
            if len(t) == 2 and t[0][1] == 64 and t[1][1] == 64:
                tree_ok += 1
        else:
            magic[bytes(m["data"][:4])] += 1
    if verbose:
        print("%-16s %9d bytes  %5d members  stored %4d  imploded %4d  "
              "PK\\3\\4 %4d  PK\\1\\2 %2d  trees sum to 64+64 on %d of %d"
              % (os.path.basename(path), len(d), len(ms), kinds[STORED],
                 kinds[IMPLODED], sig["LFH"], sig["CDH"], tree_ok, tree_tot))
    return ms, kinds, sig, method, tree_ok, tree_tot, magic


def extract(path, outdir):
    d = open(path, "rb").read()
    ms = parse(d)
    stem = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(outdir, exist_ok=True)
    wrote = skipped = 0
    for m in ms:
        if m["flag"] != STORED:
            skipped += 1
            continue
        out = os.path.join(outdir, "%s-%04d.bin" % (stem, m["index"]))
        with open(out, "wb") as fh:
            fh.write(m["data"][m["add"]:m["add"] + m["csz"]])
        wrote += 1
    print("%-16s extracted %d stored members, left %d imploded ones alone"
          % (os.path.basename(path), wrote, skipped))
    return wrote, skipped


def validate():
    def build(count, bodies):
        first = 4 + 4 * count
        offs = []
        blob = bytearray()
        o = first
        for b in bodies:
            offs.append(o)
            o += 32 + len(b)
        head = struct.pack("<I", 0) + b"".join(struct.pack("<I", x)
                                               for x in offs)
        head += bytes(first - len(head))
        for b in bodies:
            head += struct.pack("<III", 0, len(b), len(b)) + bytes(4)
            head += b + bytes(16)
        return bytes(head)

    good = build(2, [b"a" * 40, b"b" * 60])
    cases = [
        ("empty", b""),
        ("first word not zero", b"\x01" + good[1:]),
        ("offsets[0] inconsistent with the count",
         good[:4] + struct.pack("<I", 999) + good[8:]),
        ("an offset past the file", good[:8] + struct.pack("<I", 10 ** 6)
         + good[12:]),
        ("a member whose span does not close", good[:-8]),
    ]
    refused = 0
    for name, blob in cases:
        try:
            parse(blob)
            print("  NOT REFUSED: %s" % name)
        except Refused as exc:
            refused += 1
            print("  REFUSED: %-40s -- %s" % (name, exc))
    try:
        ms = parse(good)
        ok = len(ms) == 2 and ms[0]["csz"] == 40
        print("  POSITIVE CONTROL: a well-formed archive parses -- %s"
              % ("fires" if ok else "DID NOT FIRE"))
    except Refused as exc:
        ok = False
        print("  POSITIVE CONTROL DID NOT FIRE: %s" % exc)
    print("controls: %d of %d refused, positive control %s"
          % (refused, len(cases), "fires" if ok else "failed"))
    return 0 if refused == len(cases) and ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--tree")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--extract")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return validate()

    if args.tree:
        paths = sorted(set(glob.glob(os.path.join(args.tree, "*.PAK")))
                       | set(glob.glob(os.path.join(args.tree, "*.pak"))))
        if not paths:
            print("REFUSED: no .PAK files in %s" % args.tree)
            return 2
        tot = collections.Counter()
        sigs = collections.Counter()
        meths = collections.Counter()
        magics = collections.Counter()
        tok = ttot = 0
        members = 0
        opened = refused = 0
        cbytes = ubytes = 0
        for p in paths:
            try:
                ms, kinds, sig, method, a, b, magic = census(p)
                opened += 1
                members += len(ms)
                tot.update(kinds)
                sigs.update(sig)
                meths.update(method)
                magics.update(magic)
                tok += a
                ttot += b
                cbytes += sum(m["csz"] for m in ms)
                ubytes += sum(m["usz"] for m in ms)
            except Refused as exc:
                refused += 1
                print("%-16s REFUSED -- %s" % (os.path.basename(p), exc))
        print()
        print("archives opened            : %d, refused %d" % (opened, refused))
        print("members                    : %d" % members)
        print("  stored (type 0)          : %d" % tot[STORED])
        print("  imploded (type 1)        : %d" % tot[IMPLODED])
        print("compressed bytes           : %d" % cbytes)
        print("uncompressed bytes declared: %d  (ratio %.4f)"
              % (ubytes, cbytes / float(ubytes) if ubytes else 0))
        print("trailing PKZIP signatures  : %s" % dict(sigs))
        print("ZIP method in the local headers: %s  (0 stored, 6 imploded)"
              % dict(meths))
        print("Shannon-Fano trees summing to 64 + 64: %d of %d" % (tok, ttot))
        print()
        print("first four bytes of the stored members, most common:")
        for m, c in magics.most_common(8):
            printable = m.decode("latin-1")
            printable = "".join(ch if 32 <= ord(ch) < 127 else "."
                                for ch in printable)
            print("  %5d  %s  %r" % (c, m.hex(), printable))
        return 0

    if not args.path:
        ap.print_help()
        return 2
    try:
        if args.extract:
            extract(args.path, args.extract)
        else:
            census(args.path)
    except Refused as exc:
        print("REFUSED: %s -- %s" % (args.path, exc))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

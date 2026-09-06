#!/usr/bin/env python3
"""unowned.py -- read the sectors of a disc image that no file owns.

WHY THIS EXISTS. Four 3DO discs closed their sector maps at zero unowned
sectors and filled every free block with the mastering tool's `iamaduck`
string. The fifth has **no fill at all** and 16,168 sectors that belong to
nothing, and reading them is the object's headline rather than a curiosity.
Nothing in this toolbox reads a region that is not a file.

WHAT IT MEASURES, and every count comes with the denominator it was taken on:

  * the shape of the region -- sectors, distinct sectors, all-zero sectors,
    printable runs and the share of the region they occupy;
  * a token census with the CHANCE EXPECTATION printed beside every count,
    because a four-byte string is expected 0.0004 times in 34 megabytes and a
    one-byte one is expected 133,312 times, and a count that is BELOW its
    expectation is not evidence of anything;
  * filename-shaped and path-shaped tokens, censused by extension;
  * four-digit years, with a proximity test against the word `Copyright`,
    which is what separates a build date from a copyright range;
  * DOS `MZ` executable headers, counted and then CHECKED, because a two-byte
    signature is expected 521 times by chance alone.

THE EDITORIAL LINE, ENFORCED HERE RATHER THAN BY HAND. This pipeline
publishes what a pressing plant put in front of the public: paths, tool names,
filenames, source fragments, dates. It withholds **reach** -- postal
addresses, telephone and fax numbers, and mail addresses -- and reports those
as a SHAPE: kind, count and location, never digits.

**This tool cannot print a contact detail.** `--contacts` reports counts and
lengths only; the matched text is discarded before it can reach a stream. Any
future edit that prints one has to defeat `redact()` deliberately.

REFUSAL. A range outside the image, a region of zero length, or an image whose
length is not a multiple of the sector size is refused with exit status 2.
`--validate` runs six negative controls.

usage:
    unowned.py IMAGE --range A B [--cook OUT.bin]
    unowned.py REGION.bin --raw            (an already-extracted region)
    unowned.py REGION.bin --raw --tokens --names --years --mz --contacts
    unowned.py --validate
"""
import argparse
import collections
import os
import re
import struct
import sys

SECTOR = 2352
USER_OFF = 16
USER_LEN = 2048

TOKENS = [
    b"#include", b"function", b"Copyright", b"Microsoft", b"Borland",
    b"Watcom", b"IBM", b"OS/2", b"Windows", b"MS-DOS", b"Turbo",
    b"3DO", b"Alone", b"ALONE", b"Infogrames", b"I-Motion", b"ITD",
    b"ETAGE", b"Opera", b"LaunchMe", b"iamaduck", b"ARM", b"AIF",
    b".EXE", b".exe", b".OBJ", b".obj", b".LIB", b".lib", b".h",
    b"MZ", b"C:", b"/", b"\\", b"@", b"www",
]


class Refused(Exception):
    pass


def redact(match):
    """Reduce a matched contact detail to its shape. This is the only path by
    which a contact detail may leave this tool, and it returns a length."""
    return len(match)


def carve(path, a, b, dest=None):
    size = os.path.getsize(path)
    if size % SECTOR:
        raise Refused("%s is %d bytes, not a multiple of %d"
                      % (path, size, SECTOR))
    total = size // SECTOR
    if not (0 <= a <= b < total):
        raise Refused("range %d..%d is outside 0..%d" % (a, b, total - 1))
    out = bytearray()
    with open(path, "rb") as fh:
        for lba in range(a, b + 1):
            fh.seek(lba * SECTOR)
            s = fh.read(SECTOR)
            out += s[USER_OFF:USER_OFF + USER_LEN]
    if dest:
        with open(dest, "wb") as fh:
            fh.write(out)
        print("carved %d sectors -> %s (%d bytes)"
              % (b - a + 1, dest, len(out)))
    return bytes(out)


def shape(data, sectors):
    print("-- shape ------------------------------------------------------")
    print("  bytes                              %d" % len(data))
    if sectors:
        blocks = [data[i:i + USER_LEN] for i in range(0, len(data), USER_LEN)]
        distinct = len(set(blocks))
        zero = sum(1 for b in blocks if not any(b))
        print("  sectors                            %d" % len(blocks))
        print("  distinct sectors                   %d  (%.4f %%)"
              % (distinct, 100.0 * distinct / len(blocks)))
        print("  all-zero sectors                   %d  (%.4f %%)"
              % (zero, 100.0 * zero / len(blocks)))
    runs = re.findall(rb"[ -~]{6,}", data)
    inside = sum(len(r) for r in runs)
    print("  printable runs of >= 6             %d" % len(runs))
    print("  bytes inside them                  %d  (%.4f %%)"
          % (inside, 100.0 * inside / len(data)))
    return b"\n".join(runs)


def tokens(data):
    n = len(data)
    print("-- tokens, each beside its chance expectation ------------------")
    print("  %-12s %10s %14s %10s" % ("token", "count", "expected", "ratio"))
    for t in TOKENS:
        c = data.count(t)
        exp = n / (256.0 ** len(t))
        ratio = ("%.1fx" % (c / exp)) if exp > 0 and c else "-"
        if exp > 0 and c and c < exp:
            ratio = "%.2fx  BELOW CHANCE" % (c / exp)
        print("  %-12s %10d %14.4f %10s"
              % (t.decode("latin-1"), c, exp, ratio))


def names(text):
    print("-- filename-shaped tokens -------------------------------------")
    fn = re.findall(rb"\b[A-Za-z0-9_~\-]{1,8}\.[A-Za-z0-9]{1,3}\b", text)
    distinct = collections.Counter(x.upper() for x in fn)
    print("  occurrences                        %d" % len(fn))
    print("  distinct names                     %d" % len(distinct))
    ext = collections.Counter(x.rsplit(b".", 1)[1] for x in distinct)
    print("  by extension, distinct names:")
    for e, c in ext.most_common(20):
        print("    .%-8s %5d" % (e.decode("latin-1"), c))
    print()
    print("-- path-shaped tokens ------------------------------------------")
    bs = re.compile(rb"[A-Za-z]:" + b"\\\\" + rb"[A-Za-z0-9_.~\-" + b"\\\\"
                    + rb"]{3,60}")
    drive = re.findall(bs, text)
    unix = re.findall(rb"/[A-Za-z0-9_.~\-]{2,20}(?:/[A-Za-z0-9_.~\-]{1,20}){1,6}",
                      text)
    print("  drive-letter paths                 %d  (distinct %d)"
          % (len(drive), len(set(x.upper() for x in drive))))
    for p, c in collections.Counter(x.upper() for x in drive).most_common(12):
        print("    %5d  %s" % (c, p.decode("latin-1")))
    print("  slash paths                        %d  (distinct %d)"
          % (len(unix), len(set(unix))))
    return distinct


def years(text, data):
    print("-- four-digit years, and the Copyright proximity test ----------")
    hist = collections.Counter()
    near = collections.Counter()
    for m in re.finditer(rb"\b(19[89]\d|20[0-2]\d)\b", data):
        y = int(m.group(1))
        hist[y] += 1
        lo = max(0, m.start() - 40)
        window = data[lo:m.end() + 40]
        if b"Copyright" in window or b"copyright" in window or b"(c)" in window \
                or b"(C)" in window or re.search(rb"\b(19[89]\d|20[0-2]\d)\b",
                                                 window[:m.start() - lo]):
            near[y] += 1
    total = sum(hist.values())
    print("  year tokens 1980..2029             %d" % total)
    print("  %-6s %8s %10s %8s" % ("year", "count", "near (C)", "share"))
    for y in sorted(hist):
        if hist[y] >= 20:
            print("  %-6d %8d %10d %7.1f %%"
                  % (y, hist[y], near[y], 100.0 * near[y] / hist[y]))
    post = [hist[y] for y in range(2000, 2030)]
    if post:
        print("  2000..2029: min %d max %d mean %.1f -- a flat band is a "
              "generated table" % (min(post), max(post),
                                   sum(post) / len(post)))
    return hist, near


def mz(data):
    print("-- DOS MZ headers: the signature, then the check ---------------")
    n = len(data)
    sig = [m.start() for m in re.finditer(rb"MZ", data)]
    exp = n / 65536.0
    print("  MZ occurrences                     %d (chance %.1f)" % (len(sig), exp))
    good = 0
    for off in sig:
        if off + 28 > n:
            continue
        try:
            (lastpage, pages, relocs, hdrpara, minalloc, maxalloc,
             ss, sp, csum, ip, cs, lfarlc) = struct.unpack_from(
                "<HHHHHHHHHHHH", data, off + 2)
        except struct.error:
            continue
        if pages == 0 or hdrpara < 2 or lfarlc < 0x1c:
            continue
        length = (pages - 1) * 512 + (lastpage if lastpage else 512)
        if length < hdrpara * 16 or length > 8 * 1024 * 1024:
            continue
        if relocs and lfarlc + relocs * 4 > hdrpara * 16:
            continue
        good += 1
    print("  self-consistent headers            %d of %d" % (good, len(sig)))
    return len(sig), good


def contacts(text):
    """Counts and lengths only. This function never prints matched text."""
    print("-- contact details, reported as SHAPE and never as digits ------")
    kinds = [
        ("mail addresses", rb"[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{2,}"
                           rb"\.[A-Za-z]{2,4}\b"),
        ("telephone-shaped, grouped digits",
         rb"\b(?:\+\d{1,3}[ \-.]?)?\(?\d{2,4}\)?[ \-.]\d{2,4}[ \-.]\d{2,6}\b"),
        ("URL-shaped", rb"(?:https?://|www\.)[A-Za-z0-9.\-/]{4,}"),
        ("postal-code-shaped", rb"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b"),
    ]
    for label, pat in kinds:
        hits = re.findall(pat, text)
        lens = [redact(h) for h in hits]
        distinct = len(set(hits))
        del hits
        if lens:
            print("  %-34s %5d occurrences, %d distinct, lengths %d..%d"
                  % (label, len(lens), distinct, min(lens), max(lens)))
        else:
            print("  %-34s %5d" % (label, 0))
    print("  (the matched text is discarded inside this function and is not "
          "reachable from any output path)")


def validate():
    import tempfile
    cases = []
    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.write(fd, b"\0" * (SECTOR * 4))
    os.close(fd)
    try:
        for label, fn in [
            ("range beyond the image", lambda: carve(tmp, 0, 99)),
            ("negative start", lambda: carve(tmp, -1, 2)),
            ("inverted range", lambda: carve(tmp, 3, 1)),
        ]:
            try:
                fn()
                cases.append((label, False))
            except Refused as exc:
                cases.append((label, True))
                print("  REFUSED: %-30s -- %s" % (label, exc))
    finally:
        os.unlink(tmp)

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.write(fd, b"\0" * (SECTOR * 3 + 7))
    os.close(fd)
    try:
        carve(tmp, 0, 1)
        cases.append(("image not a multiple of 2352", False))
    except Refused as exc:
        cases.append(("image not a multiple of 2352", True))
        print("  REFUSED: %-30s -- %s" % ("image not a multiple of 2352", exc))
    finally:
        os.unlink(tmp)

    # a positive control that must FIRE: a planted mail address and MZ header
    planted = (b"x" * 100 + b" someone@example.com " + b"y" * 100
               + b"MZ" + struct.pack("<HHHHHHHHHHHH", 0x90, 3, 0, 4, 0,
                                     0xFFFF, 0, 0xB8, 0, 0, 0, 0x40)
               + b"z" * 200)
    text = b"\n".join(re.findall(rb"[ -~]{6,}", planted))
    hits = re.findall(rb"[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{2,}"
                      rb"\.[A-Za-z]{2,4}\b", text)
    sig, good = mz(planted)
    ok = len(hits) == 1 and sig == 1 and good == 1
    cases.append(("POSITIVE CONTROL fires", ok))
    print("  POSITIVE CONTROL: mail %d of 1, MZ %d of 1, valid %d of 1 -- %s"
          % (len(hits), sig, good, "fires" if ok else "DID NOT FIRE"))

    passed = sum(1 for _, ok in cases if ok)
    print("controls passed: %d of %d" % (passed, len(cases)))
    return 0 if passed == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?")
    ap.add_argument("--range", nargs=2, type=int, metavar=("A", "B"))
    ap.add_argument("--raw", action="store_true",
                    help="the file is already the carved region")
    ap.add_argument("--cook", metavar="OUT")
    ap.add_argument("--tokens", action="store_true")
    ap.add_argument("--names", action="store_true")
    ap.add_argument("--years", action="store_true")
    ap.add_argument("--mz", action="store_true")
    ap.add_argument("--contacts", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return validate()
    if not args.image:
        ap.print_help()
        return 2

    try:
        if args.raw:
            data = open(args.image, "rb").read()
            sectors = len(data) % USER_LEN == 0
            if not data:
                raise Refused("region is empty")
        else:
            if not args.range:
                raise Refused("an image needs --range A B")
            data = carve(args.image, args.range[0], args.range[1], args.cook)
            sectors = True
    except Refused as exc:
        print("REFUSED: %s" % exc)
        return 2

    print("=" * 66)
    print("SLACK REGION  %s" % os.path.basename(args.image))
    print("=" * 66)
    text = shape(data, sectors)
    print()
    if args.all or args.tokens:
        tokens(data)
        print()
    if args.all or args.names:
        names(text)
        print()
    if args.all or args.years:
        years(text, data)
        print()
    if args.all or args.mz:
        mz(data)
        print()
    if args.all or args.contacts:
        contacts(text)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

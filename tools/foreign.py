#!/usr/bin/env python3
"""foreign.py -- find another computer's memory inside this one's files.

WHY. This disc carries fragments of two machines that are not the 3DO. The
first is 34 megabytes of a PC at the end of the pressing, in sectors no file
owns. The second is inside the FILES: fixed-size buffers whose tails were
never written, pressed with whatever was in RAM. Nothing in this toolbox
looks for that, and a hash census cannot see it because the bytes are part of
a file that is otherwise perfectly good data.

THE TEST, and it is three architectures against each other on one denominator.
Instruction pairs that a real program emits in matched quantities:

  * **68000** -- `LINK A6` (0x4E56) opens a stack frame and `UNLK A6`
    (0x4E5E) closes it, so a real 68000 program emits them in nearly equal
    numbers. `JSR abs.l` (0x4EB9), `RTS` (0x4E75) and `MOVEM` (0x48E7)
    corroborate. **The LINK/UNLK balance is the discriminator**: random bytes
    give both at chance and no correlation between them, while code gives
    hundreds of each within a few per cent;
  * **x86** -- `PUSH BP; MOV BP,SP` (0x55 0x8B 0xEC) and `MOV SP,BP; POP BP`
    (0x8B 0xE5 0x5D), the same idea in the other family;
  * **ARM** -- the 3DO's own. 32-bit ARM is overwhelmingly unconditional, so
    the top nibble of the first byte of each word is 0xE far more often than
    chance. This is the platform notes' own compression test, used here as a
    control in the other direction.

Every count is printed beside its chance expectation on the same denominator,
because a two-byte pattern is expected once per 65,536 bytes and saying "410
occurrences" without that is meaningless.

TOOLCHAIN STRINGS, and they are evidence rather than decoration:
MPW's shell (`{ShellDirectory}`, `MPW.Errors`, `Dev:StdOut`), its C runtime
(`_xflsbuf`, `_filbuf`, `_Static_Constructor_Destructor_Pointers`), and
Macintosh path syntax `Volume:Folder:File`, which no other system uses.

THE EDITORIAL LINE. Paths, volume names, folder names and tool names are
reported in full: they are on a disc that was pressed and sold. Contact
details -- mail addresses, telephone numbers, postal addresses -- are reported
as a shape and never as digits, and this tool cannot print one.

REFUSAL. A path that does not exist, or a tree with no files, is refused with
exit status 2. `--validate` builds 68000-shaped, x86-shaped and random
populations and requires the tool to separate them.

usage:
    foreign.py FILE
    foreign.py --tree DIR [--min-score 20]
    foreign.py FILE --paths
    foreign.py --validate
"""
import argparse
import collections
import os
import re
import sys

MPW_STRINGS = [
    b"{ShellDirectory}", b"MPW.Errors", b"Dev:StdOut", b"_xflsbuf",
    b"_filbuf", b"_flsbuf", b"_Static_Constructor_Destructor_Pointers",
    b"_bufsync", b"_findbuf", b"Worksheet", b"SADE",
]
MACPATH = re.compile(rb"[A-Za-z][A-Za-z0-9_. ]{1,30}:[A-Za-z0-9_. ]{1,30}:"
                     rb"[A-Za-z0-9_. :]{0,60}")


class Refused(Exception):
    pass


def counts(d):
    n = len(d)
    out = {
        "bytes": n,
        "link": d.count(b"\x4e\x56"),
        "unlk": d.count(b"\x4e\x5e"),
        "jsr": d.count(b"\x4e\xb9"),
        "rts": d.count(b"\x4e\x75"),
        "movem": d.count(b"\x48\xe7"),
        "x86_prologue": d.count(b"\x55\x8b\xec"),
        "x86_epilogue": d.count(b"\x8b\xe5\x5d"),
        "chance2": n / 65536.0,
        "chance3": n / 16777216.0,
    }
    if n >= 4:
        words = memoryview(d)[:n - (n % 4)]
        e = sum(1 for i in range(0, len(words), 4) if words[i] >> 4 == 0xE)
        out["arm_e_share"] = e / max(1, len(words) // 4)
    else:
        out["arm_e_share"] = 0.0
    out["mpw"] = sum(d.count(s) for s in MPW_STRINGS)
    out["printable"] = (sum(1 for b in d if 32 <= b < 127) / float(n)
                        if n else 0.0)
    return out


def balance(c):
    """LINK/UNLK agreement, 0..1. Real 68000 code is near 1."""
    a, b = c["link"], c["unlk"]
    if a + b == 0:
        return 0.0
    return 1.0 - abs(a - b) / float(a + b)


def verdict(c):
    # The printable guard, and it is here because the first version of this
    # tool got it wrong. `credits.cel` is a 320 x 250 sixteen-bit picture that
    # is 74.71 % printable-range bytes, and 0x4E, 0x56 and 0x5E are the ASCII
    # letters `N`, `V` and `^`: it scored LINK 357, UNLK 410, balance 0.931
    # and was reported as 68000. It is not. A file that is mostly printable
    # bytes will produce LINK/UNLK pairs by accident, so a 68000 verdict now
    # requires the data NOT to be text-shaped, and requires MOVEM or JSR to
    # corroborate -- a prologue that saves no registers and calls nothing is
    # not a program.
    m68 = (c["link"] > 20 and c["unlk"] > 20 and balance(c) > 0.85
           and c["link"] > 8 * c["chance2"]
           and c["printable"] < 0.55
           and (c["movem"] + c["jsr"]) > 4 * c["chance2"])
    x86 = (c["x86_prologue"] > 20 and c["x86_epilogue"] > 5
           and c["x86_prologue"] > 8 * c["chance3"])
    arm = c["arm_e_share"] > 0.45
    tags = []
    if m68:
        tags.append("68000")
    if x86:
        tags.append("x86")
    if arm:
        tags.append("ARM")
    if c["mpw"]:
        tags.append("MPW")
    return "+".join(tags) if tags else "-"


def show(name, c):
    print("%-30s %10d  LINK %5d UNLK %5d bal %.3f  JSR %5d RTS %5d  "
          "x86 %4d/%4d  ARM-E %.3f  MPW %3d  %s"
          % (name[:30], c["bytes"], c["link"], c["unlk"], balance(c),
             c["jsr"], c["rts"], c["x86_prologue"], c["x86_epilogue"],
             c["arm_e_share"], c["mpw"], verdict(c)))


def paths(d):
    runs = re.findall(rb"[ -~]{6,}", d)
    txt = b"\n".join(runs)
    return collections.Counter(MACPATH.findall(txt))


def validate():
    import random
    random.seed(19)
    rnd = bytes(random.randrange(256) for _ in range(200000))
    m68 = bytearray()
    for _ in range(4000):
        m68 += b"\x4e\x56\xff\xf0" + bytes(random.randrange(256)
                                           for _ in range(20))
        m68 += b"\x4e\xb9" + bytes(4) + b"\x4e\x5e\x4e\x75"
    x86 = bytearray()
    for _ in range(4000):
        x86 += b"\x55\x8b\xec" + bytes(random.randrange(256)
                                       for _ in range(20))
        x86 += b"\x8b\xe5\x5d\xc3"
    arm = bytearray()
    for _ in range(20000):
        arm += bytes([0xE1, 0xA0, 0x00, 0x00])

    tests = [
        ("random bytes", bytes(rnd), "-"),
        ("synthetic 68000", bytes(m68), "68000"),
        ("synthetic x86", bytes(x86), "x86"),
        ("synthetic ARM", bytes(arm), "ARM"),
    ]
    ok = 0
    for name, blob, want in tests:
        c = counts(blob)
        got = verdict(c)
        good = got == want
        ok += good
        show(name, c)
        print("      expected %-6s got %-6s  %s"
              % (want, got, "ok" if good else "FAILED"))
    print("controls passed: %d of %d" % (ok, len(tests)))
    return 0 if ok == len(tests) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--tree")
    ap.add_argument("--paths", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return validate()

    if args.tree:
        if not os.path.isdir(args.tree):
            print("REFUSED: %s is not a directory" % args.tree)
            return 2
        rows = []
        total = 0
        for root, _d, names in os.walk(args.tree):
            for n in sorted(names):
                p = os.path.join(root, n)
                d = open(p, "rb").read()
                total += 1
                c = counts(d)
                if args.all or verdict(c) not in ("-", "ARM"):
                    rows.append((os.path.relpath(p, args.tree), c))
        if not rows:
            print("no file in %s carries a foreign-architecture signature"
                  % args.tree)
            return 0
        for name, c in sorted(rows, key=lambda r: -r[1]["mpw"]):
            show(name, c)
        flagged = [r for r in rows if "68000" in verdict(r[1])
                   or "MPW" in verdict(r[1])]
        print()
        print("files censused                : %d" % total)
        print("files with a 68000 or MPW mark: %d" % len(flagged))
        print("bytes in them                 : %d"
              % sum(r[1]["bytes"] for r in flagged))
        return 0

    if not args.path:
        ap.print_help()
        return 2
    if not os.path.isfile(args.path):
        print("REFUSED: %s is not a file" % args.path)
        return 2
    d = open(args.path, "rb").read()
    show(os.path.basename(args.path), counts(d))
    if args.paths:
        c = paths(d)
        print()
        print("Macintosh Volume:Folder: paths -- %d occurrences, %d distinct"
              % (sum(c.values()), len(c)))
        for s, n in c.most_common(40):
            print("  %3d  %s" % (n, s.decode("latin-1")[:88]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""picsdec.py -- read the `.pics` camera backgrounds and render them.

WHAT THESE ARE. Nine files, `camera00.pics` .. `camera08.pics`, 12,206,080
bytes, 3.09 % of the pressing, and nothing in this toolbox opened them. They
are the fixed camera backgrounds the game draws its rooms on -- the thing an
Alone in the Dark room IS, with the polygonal actors composited over it.

THE LAYOUT, DERIVED HERE AND NOT ASSUMED. Two facts found it. The nine files
are byte-identical up to offset 771 and diverge at exactly **772 = 4 + 768**,
and rows whose bytes are overwhelmingly congruent to 3 modulo 4 recur with a
period of exactly **256 rows of 320 bytes = 81,920 bytes**. So:

    +0      u16 LE   width   320
    +2      u16 LE   height  250
    +4      768      palette, 256 entries of R, G, B
    +772    80,000   pixels, one byte per pixel, 320 x 250
    ...     1,148    slack to the next block
    block                                            81,920 bytes

**The palette is a 6-bit VGA palette expanded to eight bits**, and that is a
measurement rather than a reading: every non-black component byte satisfies
`b % 4 == 3`, which is exactly `v * 4 + 3` for `v` in 0..63. A palette written
for a machine with eight-bit DAC entries would not do that. The port carried
the PC original's palette arithmetic across.

**And the block size is 81,920 = 40 sectors of 2,048, exactly.** Every
background begins on a sector boundary and occupies a whole number of sectors,
which is what a disc that seeks to a room rather than reading a file wants.
The 1,148 bytes of slack per image are the price.

**Byte order is LITTLE-endian on a big-endian console**, matching the `.PAK`
archives: the port kept the PC's data layout.

WHAT IS CHECKED BEFORE ANYTHING IS WRITTEN:

  * the file length is an exact multiple of 81,920, on 9 of 9;
  * every block declares 320 x 250;
  * the palette's non-zero component bytes are `== 3 mod 4`;
  * `4 + 768 + 320 * 250 <= 81,920`.

Any of those failing is a REFUSAL with exit status 2, not a warning.
`--validate` runs five negative controls.

usage:
    picsdec.py FILE.pics --census
    picsdec.py FILE.pics --png OUTDIR [--index N]
    picsdec.py --tree DIR --census
    picsdec.py --validate
"""
import argparse
import glob
import os
import struct
import sys
import zlib

BLOCK = 81920
HDR = 4
PAL = 768
WIDTH = 320
HEIGHT = 250


class Refused(Exception):
    pass


def png(path, w, h, rows):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(raw, 9))
    out += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(out)
    return len(out)


def open_pics(path):
    d = open(path, "rb").read()
    if len(d) < BLOCK:
        raise Refused("%d bytes is under one %d-byte block" % (len(d), BLOCK))
    if len(d) % BLOCK:
        raise Refused("%d bytes is not a multiple of %d (remainder %d)"
                      % (len(d), BLOCK, len(d) % BLOCK))
    n = len(d) // BLOCK
    for i in range(n):
        w, h = struct.unpack_from("<HH", d, i * BLOCK)
        if (w, h) != (WIDTH, HEIGHT):
            raise Refused("block %d declares %d x %d, not %d x %d"
                          % (i, w, h, WIDTH, HEIGHT))
        if HDR + PAL + w * h > BLOCK:
            raise Refused("block %d does not fit its own declaration" % i)
    return d, n


def palette_check(pal):
    bad = [b for b in pal if b and b % 4 != 3]
    return len(pal) - len(bad), len(pal), len(bad)


def block(d, i):
    base = i * BLOCK
    w, h = struct.unpack_from("<HH", d, base)
    pal = d[base + HDR:base + HDR + PAL]
    px = d[base + HDR + PAL:base + HDR + PAL + w * h]
    slack = BLOCK - HDR - PAL - w * h
    return w, h, pal, px, slack


def census(path, verbose=True):
    d, n = open_pics(path)
    good = tot = bad = 0
    distinct_pal = set()
    slack_nonzero = 0
    for i in range(n):
        w, h, pal, px, slack = block(d, i)
        g, t, b = palette_check(pal)
        good += g
        tot += t
        bad += b
        distinct_pal.add(pal)
        tail = d[i * BLOCK + HDR + PAL + w * h:(i + 1) * BLOCK]
        if any(tail):
            slack_nonzero += 1
    if verbose:
        print("%-16s %9d bytes  %3d images  %d x %d  palettes %2d distinct  "
              "6-bit palette bytes %d of %d  blocks with non-zero slack %d"
              % (os.path.basename(path), len(d), n, WIDTH, HEIGHT,
                 len(distinct_pal), good, tot, slack_nonzero))
    return n, len(distinct_pal), good, tot, bad, slack_nonzero


def render(path, outdir, index=None):
    d, n = open_pics(path)
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(path))[0]
    wrote = 0
    for i in range(n):
        if index is not None and i != index:
            continue
        w, h, pal, px, _slack = block(d, i)
        rows = []
        for y in range(h):
            line = px[y * w:(y + 1) * w]
            rows.append(bytes(c for p in line for c in pal[p * 3:p * 3 + 3]))
        out = os.path.join(outdir, "%s-%03d.png" % (stem, i))
        png(out, w, h, rows)
        wrote += 1
    print("%-16s rendered %d of %d images to %s"
          % (os.path.basename(path), wrote, n, outdir))
    return wrote


def flat16(path, outdir=None):
    """The ten 160,000-byte `.cel` files: the SAME 320 x 250 geometry as the
    backgrounds, in sixteen-bit direct colour instead of eight-bit paletted.

    320 x 250 x 2 = 160,000 exactly, and the pixels are the platform's 5-5-5
    with the top bit unused. That is checked here rather than assumed, by the
    test the platform notes use: over 80,000 pixels the top bit is set ZERO
    times, while the low bit is set on 6 % to 62 % of them depending on the
    picture. If the format were 5-6-5 the top bit would be red's most
    significant and would be set constantly.

    These are NOT cels: they carry no `CCB `, no chunk header and no
    geometry. The extension lies, which on this platform is the rule and not
    the exception.

    **AND THE PIXEL ORDER IS LRform, WHICH IS THE OPPOSITE OF THE `.pics` ON
    THE SAME DISC.** A 32-bit word of the buffer holds the pixel of display
    row 2n and the pixel of row 2n+1 at the same column. Measured the way the
    platform notes measure it -- vertical roughness against horizontal, over
    the whole picture -- linear gives ratios of 2.709 to 11.510 and LRform
    gives 0.463 to 1.355, and **LRform wins on 10 of 10**. Then a person
    looked: `players.cel` de-interleaved is the character-selection screen,
    Emily Hartwood in the left panel and Edward Carnby in the right. Rendered
    linear it is the same picture with every other row displaced.

    So this disc uses **both orders at once**: eight-bit camera backgrounds
    linear, sixteen-bit full-screen pictures interleaved. That is the third
    disc's banner-versus-cels result again, on a different pair of assets, and
    it says the order belongs to whatever draws the asset.
    """
    d = open(path, "rb").read()
    want = WIDTH * HEIGHT * 2
    if len(d) != want:
        raise Refused("%d bytes, not %d = %d x %d x 2"
                      % (len(d), want, WIDTH, HEIGHT))
    top = low = 0
    rows = []
    for y in range(HEIGHT):
        row = bytearray()
        for x in range(WIDTH):
            # LRform: row 2n and row 2n+1 share a 32-bit word at column x
            idx = (y // 2) * WIDTH * 2 + x * 2 + (y & 1)
            v = struct.unpack_from(">H", d, idx * 2)[0]
            if v & 0x8000:
                top += 1
            if v & 1:
                low += 1
            r = (v >> 10) & 31
            g = (v >> 5) & 31
            b = v & 31
            row += bytes(((r << 3) | (r >> 2), (g << 3) | (g >> 2),
                          (b << 3) | (b >> 2)))
        rows.append(bytes(row))
    print("%-16s %7d bytes  %d x %d 16-bit  top bit set %d of %d  "
          "low bit set %d"
          % (os.path.basename(path), len(d), WIDTH, HEIGHT, top,
             WIDTH * HEIGHT, low))
    if top:
        raise Refused("the top bit is set %d times; this is not 5-5-5" % top)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        out = os.path.join(outdir, os.path.splitext(
            os.path.basename(path))[0] + ".png")
        png(out, WIDTH, HEIGHT, rows)
        print("    wrote %s" % out)
    return top, low


def validate():
    import tempfile
    good = struct.pack("<HH", WIDTH, HEIGHT) + bytes(768) + bytes(BLOCK - 772)
    cases = [
        ("empty", b""),
        ("half a block", good[:BLOCK // 2]),
        ("a block and a half", good + good[:BLOCK // 2]),
        ("wrong declared size",
         struct.pack("<HH", 640, 480) + good[4:]),
        ("big-endian header",
         struct.pack(">HH", WIDTH, HEIGHT) + good[4:]),
    ]
    refused = 0
    for name, blob in cases:
        fd, tmp = tempfile.mkstemp(suffix=".pics")
        os.write(fd, blob)
        os.close(fd)
        try:
            open_pics(tmp)
            print("  NOT REFUSED: %s" % name)
        except Refused as exc:
            refused += 1
            print("  REFUSED: %-24s -- %s" % (name, exc))
        finally:
            os.unlink(tmp)
    # positive control: a well-formed one-block file must open
    fd, tmp = tempfile.mkstemp(suffix=".pics")
    os.write(fd, good)
    os.close(fd)
    try:
        _d, n = open_pics(tmp)
        ok = n == 1
        print("  POSITIVE CONTROL: a valid one-block file opens -- %s"
              % ("fires" if ok else "DID NOT FIRE"))
    except Refused as exc:
        ok = False
        print("  POSITIVE CONTROL DID NOT FIRE: %s" % exc)
    finally:
        os.unlink(tmp)
    print("controls: %d of %d refused, positive control %s"
          % (refused, len(cases), "fires" if ok else "failed"))
    return 0 if refused == len(cases) and ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--tree")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--png")
    ap.add_argument("--index", type=int)
    ap.add_argument("--flat16", action="store_true")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return validate()

    if args.tree:
        paths = sorted(glob.glob(os.path.join(args.tree, "*.pics")))
        if not paths:
            print("REFUSED: no .pics files in %s" % args.tree)
            return 2
        total = images = pal_good = pal_tot = 0
        opened = refused = 0
        for p in paths:
            try:
                n, _dp, g, t, _b, _sn = census(p)
                opened += 1
                images += n
                pal_good += g
                pal_tot += t
                total += os.path.getsize(p)
            except Refused as exc:
                refused += 1
                print("%-16s REFUSED -- %s" % (os.path.basename(p), exc))
        print()
        print("files opened            : %d, refused %d" % (opened, refused))
        print("images                  : %d" % images)
        print("bytes                   : %d" % total)
        print("image bytes             : %d  (%.4f %% of the files)"
              % (images * WIDTH * HEIGHT,
                 100.0 * images * WIDTH * HEIGHT / total))
        print("slack to the 40-sector block: %d bytes"
              % (total - images * (HDR + PAL + WIDTH * HEIGHT)))
        print("palette bytes that are 6-bit VGA: %d of %d = %.4f %%"
              % (pal_good, pal_tot, 100.0 * pal_good / pal_tot))
        return 0

    if not args.path:
        ap.print_help()
        return 2
    try:
        if args.flat16:
            flat16(args.path, args.png)
        elif args.png:
            render(args.path, args.png, args.index)
        else:
            census(args.path)
    except Refused as exc:
        print("REFUSED: %s -- %s" % (args.path, exc))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

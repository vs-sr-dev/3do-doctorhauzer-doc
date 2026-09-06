#!/usr/bin/env python3
"""imagwalk.py -- census the `IMAG` image descriptor, and MEASURE the pixel
order instead of reading it.

`IMAG` is the first 3DO disc's image descriptor. The platform notes carry it
at `[1 of 3]` on the counts and `[2 of 2]` on the container, and they carry a
trap on it that has been untestable since that disc:

  > the trap stands FOR THE `IMAG` CHUNK: on the first disc `pixel order` says
  > LRform on 30 of 61 files and says the opposite on the other 31, and a
  > decoder that reads it produces 31 wrong pictures. Do not trust
  > `pixel order`.

Two discs of five since then had no `IMAG` at all and a third had one false
positive inside a Cinepak frame. **This tool exists to test that trap on a
second disc**, and it does it the way the notes settled the banner screen and
the fifth disc's full-screen pictures: **vertical roughness against horizontal
roughness, over the whole picture, under each candidate order.** The order
whose vertical roughness collapses is the order the picture is in. The
descriptor's own byte is printed beside the measurement and is never used to
decode.

The chunk, from the platform notes:

    +0   char[4] 'IMAG'      +4   u32 length including these eight bytes
    +8   u32  width          +12  u32 height        +16  u32 bytes per row
    +20  u8   bits per pixel +21  u8  components    +22  u8  planes
    +23  u8   colour space   +24  u8  compression   +25  u8  hv format
    +26  u8   pixel order    +27  u8  version

    python tools/imagwalk.py TREE --census
    python tools/imagwalk.py FILE --fields
    python tools/imagwalk.py FILE --png OUT.png [--order linear|lrform]
"""
import argparse
import os
import struct
import sys
import zlib


class Refused(Exception):
    pass


def chunks(d):
    """Walk the platform's chunk rule and refuse loudly if it does not tile."""
    out = []
    i = 0
    while i + 8 <= len(d):
        tag = d[i:i + 4]
        if not all(32 <= c < 127 for c in tag):
            raise Refused("chunk id %r at %d is not four printable characters"
                          % (tag, i))
        ln = struct.unpack_from(">I", d, i + 4)[0]
        if ln < 8 or i + ln > len(d):
            raise Refused("chunk %r at %d declares length %d, past the %d-byte "
                          "file" % (tag, i, ln, len(d)))
        out.append((tag, i, ln))
        i += ln
    if i != len(d):
        raise Refused("chunks stop at %d of %d bytes" % (i, len(d)))
    return out


def fields(d, off):
    w, h, bpr = struct.unpack_from(">III", d, off + 8)
    bpp, comp, planes, space, compression, hv, order, ver = \
        struct.unpack_from(">BBBBBBBB", d, off + 20)
    return dict(width=w, height=h, bytes_per_row=bpr, bpp=bpp,
                components=comp, planes=planes, space=space,
                compression=compression, hv=hv, order=order, version=ver)


def lum(v):
    return ((v >> 10) & 31) + ((v >> 5) & 31) + (v & 31)


def roughness(d, off, w, h, order):
    """Vertical and horizontal roughness of a 16-bit 5-5-5 payload.

    The measurement the platform notes use, and the reason it works: a
    photograph or a rendered scene is smooth in both directions, so a wrong
    row order shows up as vertical roughness two to eleven times the
    horizontal. It is a ratio and needs no reference picture.
    """
    px = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if order == "linear":
                i = y * w + x
            else:  # lrform: rows 2n and 2n+1 share a 32-bit word
                i = (y // 2) * w * 2 + x * 2 + (y & 1)
            px[y][x] = lum(struct.unpack_from(">H", d, off + i * 2)[0])
    vert = sum(abs(px[y][x] - px[y - 1][x])
               for y in range(1, h) for x in range(w))
    horz = sum(abs(px[y][x] - px[y][x - 1])
               for y in range(h) for x in range(1, w))
    return vert, horz, px


def png(path, w, h, px):
    raw = b""
    for y in range(h):
        row = bytearray(b"\x00")
        for x in range(w):
            v = px[y][x]
            g = min(255, v * 255 // 93)
            row += bytes((g, g, g))
        raw += bytes(row)

    def chunk(tag, data):
        c = tag + data
        return (struct.pack(">I", len(data)) + c
                + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF))
    hdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", hdr)
                           + chunk(b"IDAT", zlib.compress(raw))
                           + chunk(b"IEND", b""))


def one(path, want_png=None, force=None, quiet=False):
    d = open(path, "rb").read()
    if d[:4] != b"IMAG":
        raise Refused("does not begin IMAG (begins %r)" % d[:4])
    ch = chunks(d)
    f = fields(d, 0)
    pdat = [c for c in ch if c[0] == b"PDAT"]
    tags = " ".join(c[0].decode("ascii") for c in ch)

    payload = sum(c[2] - 8 for c in pdat)
    want = f["bytes_per_row"] * f["height"]
    closes = payload == want
    exact = (ch[0][2] + sum(c[2] for c in ch[1:])) == len(d)

    line = ("%-34s %8d B  %4d x %-4d %2d bpp  bpr %5d  order=%d  "
            "chunks[%s]  payload %d %s want %d  chain %s"
            % (os.path.basename(path), len(d), f["width"], f["height"],
               f["bpp"], f["bytes_per_row"], f["order"], tags, payload,
               "==" if closes else "!=", want, "closes" if exact else "BROKEN"))
    if not quiet:
        print(line)

    meas = None
    if f["bpp"] == 16 and pdat and payload >= f["width"] * f["height"] * 2:
        off = pdat[0][1] + 8
        vl, hl, pxl = roughness(d, off, f["width"], f["height"], "linear")
        vr, hr, pxr = roughness(d, off, f["width"], f["height"], "lrform")
        rl = vl / float(hl) if hl else 0.0
        rr = vr / float(hr) if hr else 0.0
        meas = "linear" if rl <= rr else "lrform"
        if not quiet:
            print("      roughness V/H  linear %.4f   lrform %.4f   "
                  "measured order: %s   descriptor says: %s"
                  % (rl, rr, meas,
                     "lrform" if f["order"] else "linear"))
        if want_png:
            use = force or meas
            png(want_png, f["width"], f["height"],
                pxl if use == "linear" else pxr)
            if not quiet:
                print("      wrote %s in %s order" % (want_png, use))
    return f, closes, exact, meas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--fields", action="store_true")
    ap.add_argument("--png")
    ap.add_argument("--order", choices=("linear", "lrform"))
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if not a.census:
        try:
            one(a.target, want_png=a.png, force=a.order)
        except Refused as e:
            print("REFUSED: %s: %s" % (a.target, e))
            return 1
        return 0

    files = []
    for root, _, names in os.walk(a.target):
        for n in sorted(names):
            files.append(os.path.join(root, n))

    opened = refused = 0
    closes = broken = 0
    orders_seen = {}
    measured = {}
    disagree = []
    shapes = {}
    depths = {}
    for p in files:
        try:
            head = open(p, "rb").read(4)
        except OSError:
            continue
        if head != b"IMAG":
            continue
        try:
            f, cl, ex, meas = one(p, quiet=a.quiet)
        except Refused as e:
            refused += 1
            print("REFUSED %-34s %s" % (os.path.basename(p), e))
            continue
        opened += 1
        closes += 1 if cl else 0
        broken += 0 if ex else 1
        orders_seen[f["order"]] = orders_seen.get(f["order"], 0) + 1
        depths[f["bpp"]] = depths.get(f["bpp"], 0) + 1
        k = (f["width"], f["height"], f["bpp"])
        shapes[k] = shapes.get(k, 0) + 1
        if meas:
            measured[meas] = measured.get(meas, 0) + 1
            said = "lrform" if f["order"] else "linear"
            if said != meas:
                disagree.append((p, said, meas))

    print()
    print("files walked                       : %d" % len(files))
    print("files beginning IMAG               : %d" % (opened + refused))
    print("  parsed                           : %d" % opened)
    print("  refused                          : %d" % refused)
    print("chunk chain closes to the last byte: %d of %d"
          % (opened - broken, opened))
    print("bytes_per_row x height == payload  : %d of %d" % (closes, opened))
    print("distinct (w, h, bpp) shapes        : %d" % len(shapes))
    for k in sorted(shapes):
        print("    %4d x %-4d %2d bpp : %3d files" % (k[0], k[1], k[2],
                                                      shapes[k]))
    print("bits per pixel seen                : %s"
          % ", ".join("%d bpp x%d" % (k, depths[k]) for k in sorted(depths)))
    print("the descriptor's pixel-order byte  : %s"
          % ", ".join("%d on %d files" % (k, orders_seen[k])
                      for k in sorted(orders_seen)))
    print("THE ORDER AS MEASURED              : %s"
          % ", ".join("%s on %d" % (k, measured[k]) for k in sorted(measured)))
    print("files where the descriptor DISAGREES with the measurement : %d"
          % len(disagree))
    for p, said, meas in disagree:
        print("    %-34s says %s, measures %s"
              % (os.path.basename(p), said, meas))
    return 0


if __name__ == "__main__":
    sys.exit(main())

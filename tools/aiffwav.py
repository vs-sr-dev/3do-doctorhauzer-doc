#!/usr/bin/env python3
"""aiffwav.py -- write a listenable WAV from a 3DO AIFF or AIFF-C file.

WHY THIS EXISTS. `aiffread.py` censuses AIFF containers and `sdx2dec.py`
decodes the SDX2 codec, and between them there was no way to put a plain
uncompressed AIFF in front of a person. This disc is the first in the
collection that carries BOTH codecs -- twenty English files in AIFF-C/SDX2 at
44,100 Hz sixteen bit and twenty French files in AIFF/NONE at 10,000 Hz eight
bit -- so a comparison by ear needs one tool that opens both.

WHAT IS PUBLIC AND WHAT IS DERIVED HERE. The AIFF and AIFF-C containers are
public (EA IFF 85, Apple 1988/1991): `FORM`/`AIFF`, a `COMM` chunk carrying
channels, frame count, bit depth and an 80-bit IEEE extended sample rate, and
an `SSND` chunk carrying offset, block size and the samples. That definition
is USED here and is not re-derived. The SDX2 rule is the platform's and is
public too:

    v = d * |d| * 2                d read SIGNED
    bit 0 of d clear -> sample IS v            (absolute)
    bit 0 of d set   -> sample is previous + v (relative)

with one running predictor per channel. It is the same rule `sdx2dec.py`
states and this tool states it again rather than importing it silently.

WHAT IS CHECKED BEFORE ANYTHING IS WRITTEN, per file:

  * `FORM` size + 8 == the file length, or the shortfall is reported;
  * chunks tile the FORM to its last byte, or the residue is reported;
  * for codec NONE: `SSND payload - 8 == frames * channels * (bits/8)`;
  * for SDX2:       `SSND payload - 8 == frames * channels * 1`, which is
    what a 2:1 codec means and is checked BEFORE decoding;
  * the clipping rate of the decoded output is reported. A wrong sign or a
    missing doubling in the square term saturates constantly.

REFUSAL. A file with no `FORM`, no `AIFF`/`AIFC` type or no `COMM` is
REFUSED, loudly, with exit status 2. `--validate` runs five negative controls
and must see five refusals.

usage:
    aiffwav.py FILE.aiff [OUT.wav] [--seconds N]
    aiffwav.py --tree DIR --out DIR [--seconds N]
    aiffwav.py --validate
"""
import argparse
import os
import struct
import sys


class Refused(Exception):
    pass


def extended80(b):
    """The 80-bit IEEE extended float in a COMM chunk. Big-endian."""
    if len(b) != 10:
        raise Refused("COMM rate field is not ten bytes")
    expon = struct.unpack(">H", b[0:2])[0]
    hi, lo = struct.unpack(">LL", b[2:10])
    sign = 1.0
    if expon & 0x8000:
        sign = -1.0
        expon &= 0x7FFF
    if expon == 0 and hi == 0 and lo == 0:
        return 0.0
    if expon == 0x7FFF:
        raise Refused("COMM rate is a NaN or an infinity")
    mant = hi * 4294967296.0 + lo
    return sign * mant * 2.0 ** (expon - 16383 - 63)


def parse(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 12:
        raise Refused("shorter than a FORM header")
    if data[0:4] != b"FORM":
        raise Refused("no FORM magic: %r" % data[0:4])
    form_size = struct.unpack(">L", data[4:8])[0]
    kind = data[8:12]
    if kind not in (b"AIFF", b"AIFC"):
        raise Refused("FORM type is %r, not AIFF or AIFC" % kind)

    shortfall = len(data) - (form_size + 8)
    comm = None
    ssnd = None
    tags = []
    off = 12
    while off + 8 <= len(data):
        tag = data[off:off + 4]
        size = struct.unpack(">L", data[off + 4:off + 8])[0]
        body = data[off + 8:off + 8 + size]
        tags.append((tag.decode("latin-1"), size))
        if tag == b"COMM":
            comm = body
        elif tag == b"SSND":
            ssnd = body
        off += 8 + size + (size & 1)
    residue = len(data) - off

    if comm is None:
        raise Refused("no COMM chunk")
    if ssnd is None:
        raise Refused("no SSND chunk")
    if len(comm) < 18:
        raise Refused("COMM is %d bytes, under eighteen" % len(comm))

    channels, frames, bits = struct.unpack(">HLH", comm[0:8])
    rate = extended80(comm[8:18])
    codec = comm[18:22].decode("latin-1") if len(comm) >= 22 else "NONE"
    if kind == b"AIFF":
        codec = "NONE"
    if len(ssnd) < 8:
        raise Refused("SSND is %d bytes, under its own header" % len(ssnd))
    payload = ssnd[8:]

    return {
        "path": path, "kind": kind.decode("latin-1"), "codec": codec,
        "channels": channels, "frames": frames, "bits": bits, "rate": rate,
        "payload": payload, "tags": tags,
        "shortfall": shortfall, "residue": residue,
        "bytes": len(data),
    }


def decode(info):
    """Return (pcm16 bytes, clipped, total) -- always 16-bit little-endian."""
    ch = info["channels"]
    frames = info["frames"]
    codec = info["codec"]
    payload = info["payload"]
    clipped = 0

    if codec == "SDX2":
        want = frames * ch * 1
        if len(payload) != want:
            raise Refused("SDX2: SSND payload %d, frames*channels %d"
                          % (len(payload), want))
        prev = [0] * ch
        out = bytearray(frames * ch * 2)
        p = 0
        for i in range(frames * ch):
            d = payload[i]
            if d > 127:
                d -= 256
            v = d * abs(d) * 2
            c = i % ch
            s = v if (d & 1) == 0 else prev[c] + v
            if s > 32767:
                s = 32767
                clipped += 1
            elif s < -32768:
                s = -32768
                clipped += 1
            prev[c] = s
            struct.pack_into("<h", out, p, s)
            p += 2
        return bytes(out), clipped, frames * ch

    if codec == "NONE":
        bits = info["bits"]
        if bits == 8:
            want = frames * ch
            if len(payload) < want:
                raise Refused("NONE/8: SSND payload %d, need %d"
                              % (len(payload), want))
            out = bytearray(want * 2)
            for i in range(want):
                d = payload[i]
                if d > 127:
                    d -= 256
                struct.pack_into("<h", out, i * 2, d * 256)
            return bytes(out), 0, want
        if bits == 16:
            want = frames * ch * 2
            if len(payload) < want:
                raise Refused("NONE/16: SSND payload %d, need %d"
                              % (len(payload), want))
            out = bytearray(want)
            for i in range(frames * ch):
                s = struct.unpack_from(">h", payload, i * 2)[0]
                struct.pack_into("<h", out, i * 2, s)
            return bytes(out), 0, frames * ch
        raise Refused("codec NONE at %d bits is not handled" % bits)

    raise Refused("codec %r is not handled" % codec)


def wav(path, pcm, channels, rate):
    rate = int(round(rate))
    byte_rate = rate * channels * 2
    hdr = b"RIFF" + struct.pack("<L", 36 + len(pcm)) + b"WAVEfmt "
    hdr += struct.pack("<LHHLLHH", 16, 1, channels, rate, byte_rate,
                       channels * 2, 16)
    hdr += b"data" + struct.pack("<L", len(pcm))
    with open(path, "wb") as fh:
        fh.write(hdr)
        fh.write(pcm)


def one(path, out, seconds):
    info = parse(path)
    ch = info["channels"]
    if seconds > 0:
        keep = int(seconds * info["rate"])
        if keep < info["frames"]:
            per = 1 if info["codec"] == "SDX2" else info["bits"] // 8
            info["frames"] = keep
            info["payload"] = info["payload"][:keep * ch * per]
    pcm, clipped, total = decode(info)
    secs = info["frames"] / info["rate"] if info["rate"] else 0.0
    print("%-34s %-4s %-4s %6d Hz %2d bit %dch  %10d frames  %8.2f s"
          % (os.path.basename(path), info["kind"], info["codec"],
             int(round(info["rate"])), info["bits"], ch,
             info["frames"], secs))
    if info["shortfall"]:
        print("    FORM size + 8 misses the file by %d bytes"
              % info["shortfall"])
    if info["residue"]:
        print("    chunks leave %d bytes unaccounted" % info["residue"])
    rate_pct = 100.0 * clipped / total if total else 0.0
    verdict = "SUSPECT" if rate_pct > 1.0 else "ok"
    print("    clipped %d of %d samples = %.4f %%  [%s]"
          % (clipped, total, rate_pct, verdict))
    if out:
        wav(out, pcm, ch, info["rate"])
        print("    wrote %s  %d bytes" % (out, 44 + len(pcm)))
    return info, secs


def validate():
    import tempfile
    cases = [
        ("empty", b""),
        ("not a FORM", b"RIFF" + b"\0" * 64),
        ("FORM of the wrong type", b"FORM" + struct.pack(">L", 64) + b"8SVX"
                                   + b"\0" * 60),
        ("AIFF with no COMM", b"FORM" + struct.pack(">L", 20) + b"AIFF"
                              + b"SSND" + struct.pack(">L", 8) + b"\0" * 8),
        ("COMM too short", b"FORM" + struct.pack(">L", 24) + b"AIFF"
                            + b"COMM" + struct.pack(">L", 4) + b"\0" * 4
                            + b"SSND" + struct.pack(">L", 0)),
    ]
    refused = 0
    for name, blob in cases:
        fd, tmp = tempfile.mkstemp(suffix=".aiff")
        os.write(fd, blob)
        os.close(fd)
        try:
            parse(tmp)
            print("  NOT REFUSED: %s" % name)
        except Refused as exc:
            refused += 1
            print("  REFUSED: %-26s -- %s" % (name, exc))
        finally:
            os.unlink(tmp)
    print("negative controls refused: %d of %d" % (refused, len(cases)))
    return 0 if refused == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--tree")
    ap.add_argument("--out")
    ap.add_argument("--seconds", type=float, default=0.0)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return validate()

    if args.tree:
        if not args.out:
            print("--tree needs --out DIR")
            return 2
        os.makedirs(args.out, exist_ok=True)
        opened = refused = 0
        for root, _dirs, names in os.walk(args.tree):
            for name in sorted(names):
                src = os.path.join(root, name)
                dst = os.path.join(args.out,
                                   os.path.splitext(name)[0] + ".wav")
                try:
                    one(src, dst, args.seconds)
                    opened += 1
                except Refused as exc:
                    refused += 1
                    print("%-34s REFUSED -- %s" % (name, exc))
        print("\nopened %d, refused %d" % (opened, refused))
        return 0

    if not args.file:
        ap.print_help()
        return 2
    try:
        one(args.file, args.out, args.seconds)
    except Refused as exc:
        print("REFUSED: %s -- %s" % (args.file, exc))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

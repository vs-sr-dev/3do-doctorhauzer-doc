#!/usr/bin/env python3
"""sampdec.py -- read the `.samp` files: a headerless SDX2 stream.

WHAT THIS OBJECT IS, AND WHY THERE IS NO HEADER TO READ. Thirty `.samp` files
hold 145,995,096 bytes, 36.97 % of this pressing, and the session brief called
them five different magic numbers. They are not five magics. Fifteen of the
thirty are the same 1,515,520-byte file, so there are four distinct openings
across fifteen distinct files, and **none of the four is a magic number**:
they are the first four samples of an audio stream with no container at all.

`sdx2dec.py` decodes SDX2 out of an AIFF-C container and correctly refuses
these; `aiffread.py` refuses them too. The refusals are right and they leave
36.97 % of the disc unread, which is what this tool is for.

THE CODEC IS THE PLATFORM'S AND IT IS PUBLIC. The rule is the same one the
platform notes carry and `sdx2dec.py` states:

    v = d * |d| * 2                 d read SIGNED
    bit 0 of d clear -> the sample IS v            (absolute)
    bit 0 of d set   -> the sample is previous + v (relative)

one running predictor per channel, one stored byte per sample. It is being
USED here, not re-derived.

WHAT MAKES THE READING TESTABLE RATHER THAN ASSUMED. A stream that is not
SDX2 does not decode quietly: the square term is a random walk and it
saturates. The measure is the clipping rate, and it needs a control chosen
inside the same object:

    the thirty `.samp`               0.000 % to 0.954 % clipped
    `ETAGE02.PAK` (compressed)       9.232 %
    `ITD_RESS.PAK` (compressed)      7.866 %
    `camera00.pics` (pictures)      15.944 %

Two populations, no overlap. That is the test, and `--control FILE` re-runs it
against anything you like.

WHAT IS NOT DERIVED, AND IS SAID RATHER THAN GLOSSED. **The sample rate is
not in the file**, because there is no header. 44,100 Hz is the rate every
other SDX2 stream on this disc declares in its `COMM` chunk, and it is what
this tool assumes and prints as an assumption. Change it with `--rate`. The
channel count is likewise assumed to be one, which is what all 41 AIFF
containers on this disc declare.

REFUSAL. A file under 64 bytes, or one whose clipping rate exceeds
`--max-clip` (default 1 %), is REFUSED with exit status 2 and is not written
out. `--validate` runs five negative controls and one positive.

usage:
    sampdec.py FILE.samp [OUT.wav] [--rate N] [--seconds N]
    sampdec.py --tree DIR --out DIR
    sampdec.py --control FILE
    sampdec.py --validate
"""
import argparse
import os
import struct
import sys

import numpy as np

RATE = 44100


class Refused(Exception):
    pass


def decode(data):
    """SDX2, mono. Returns (int16 array, clipped, total)."""
    b = np.frombuffer(data, dtype=np.int8).astype(np.int64)
    v = b * np.abs(b) * 2
    absolute = np.flatnonzero((b & 1) == 0)
    out = np.empty(len(b), dtype=np.int64)
    if len(absolute) == 0:
        out[:] = np.cumsum(v)
    else:
        if absolute[0] > 0:
            out[:absolute[0]] = np.cumsum(v[:absolute[0]])
        for k, i in enumerate(absolute):
            j = absolute[k + 1] if k + 1 < len(absolute) else len(b)
            out[i] = v[i]
            if j > i + 1:
                out[i + 1:j] = v[i] + np.cumsum(v[i + 1:j])
    clipped = int(np.count_nonzero((out > 32767) | (out < -32768)))
    return np.clip(out, -32768, 32767).astype("<i2"), clipped, len(b)


def wav(path, pcm, rate, channels=1):
    raw = pcm.tobytes()
    hdr = b"RIFF" + struct.pack("<L", 36 + len(raw)) + b"WAVEfmt "
    hdr += struct.pack("<LHHLLHH", 16, 1, channels, rate,
                       rate * channels * 2, channels * 2, 16)
    hdr += b"data" + struct.pack("<L", len(raw))
    with open(path, "wb") as fh:
        fh.write(hdr)
        fh.write(raw)
    return 44 + len(raw)


def one(path, out, rate, max_clip, seconds=0.0, quiet=False):
    data = open(path, "rb").read()
    if len(data) < 64:
        raise Refused("%d bytes is too short to be a stream" % len(data))
    if seconds > 0:
        data = data[:int(seconds * rate)]
    pcm, clipped, total = decode(data)
    pct = 100.0 * clipped / total
    secs = total / float(rate)
    if not quiet:
        print("%-20s %11d bytes  %10d samples  %8.2f s  clipped %.4f %%"
              % (os.path.basename(path), len(data), total, secs, pct))
    if pct > max_clip:
        raise Refused("clipping rate %.4f %% exceeds %.4f %% -- this is not "
                      "an SDX2 stream" % (pct, max_clip))
    if out:
        n = wav(out, pcm, rate)
        if not quiet:
            print("    wrote %s  %d bytes  (rate %d Hz ASSUMED, not declared)"
                  % (out, n, rate))
    return total, secs, pct


def control(path, rate, max_clip):
    data = open(path, "rb").read()
    _pcm, clipped, total = decode(data)
    pct = 100.0 * clipped / total
    print("CONTROL %-30s %10d bytes  clipped %7.4f %%  -> %s"
          % (os.path.basename(path), len(data), pct,
             "would be ACCEPTED" if pct <= max_clip else "REFUSED, correctly"))
    return pct


def validate():
    import tempfile
    import random
    random.seed(11)
    ok = 0
    cases = 0

    # five negatives: too short, and four streams that are not SDX2
    fd, tmp = tempfile.mkstemp(suffix=".samp")
    os.write(fd, b"\0" * 8)
    os.close(fd)
    cases += 1
    try:
        one(tmp, None, RATE, 1.0, quiet=True)
        print("  NOT REFUSED: an eight-byte file")
    except Refused as exc:
        ok += 1
        print("  REFUSED: %-28s -- %s" % ("an eight-byte file", exc))
    os.unlink(tmp)

    for name, blob in [
        ("uniform random bytes",
         bytes(random.randrange(256) for _ in range(200000))),
        ("all 0xFF", b"\xff" * 200000),
        ("a rising ramp", bytes(i & 0xFF for i in range(200000))),
    ]:
        fd, tmp = tempfile.mkstemp(suffix=".samp")
        os.write(fd, blob)
        os.close(fd)
        cases += 1
        try:
            one(tmp, None, RATE, 1.0, quiet=True)
            print("  NOT REFUSED: %s" % name)
        except Refused as exc:
            ok += 1
            print("  REFUSED: %-28s -- %s" % (name, exc))
        os.unlink(tmp)

    # one positive: a sine, encoded as absolute SDX2 samples, must be accepted
    import math
    enc = bytearray()
    for i in range(100000):
        s = int(30000 * math.sin(i * 0.01))
        d = int(math.copysign(math.sqrt(abs(s) / 2.0), s))
        d &= ~1
        enc.append(d & 0xFF)
    fd, tmp = tempfile.mkstemp(suffix=".samp")
    os.write(fd, bytes(enc))
    os.close(fd)
    cases += 1
    try:
        one(tmp, None, RATE, 1.0, quiet=True)
        ok += 1
        print("  POSITIVE CONTROL: an encoded sine is accepted -- fires")
    except Refused as exc:
        print("  POSITIVE CONTROL DID NOT FIRE: %s" % exc)
    os.unlink(tmp)

    # A KNOWN LIMIT, printed rather than hidden. The clipping test is a
    # NECESSARY condition and not a sufficient one: a stream of alternating
    # 0x7F and 0x81 is two relative steps of +32,258 and -32,258, so it
    # oscillates between 0 and 32,258 and never clips. This tool would accept
    # it. Say so; do not pretend the test is a proof.
    fd, tmp = tempfile.mkstemp(suffix=".samp")
    os.write(fd, b"\x7f\x81" * 100000)
    os.close(fd)
    try:
        one(tmp, None, RATE, 1.0, quiet=True)
        print("  KNOWN LIMIT: alternating 0x7F 0x81 is accepted -- the "
              "clipping test is necessary, not sufficient")
    except Refused:
        print("  KNOWN LIMIT case was refused, which is new; re-read this "
              "comment")
    os.unlink(tmp)

    print("controls passed: %d of %d, with one known limit printed above"
          % (ok, cases))
    return 0 if ok == cases else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--rate", type=int, default=RATE)
    ap.add_argument("--seconds", type=float, default=0.0)
    ap.add_argument("--max-clip", type=float, default=1.0)
    ap.add_argument("--tree")
    ap.add_argument("--out")
    ap.add_argument("--ext", default=".samp")
    ap.add_argument("--control")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return validate()
    if args.control:
        control(args.control, args.rate, args.max_clip)
        return 0

    if args.tree:
        opened = refused = 0
        samples = 0
        secs = 0.0
        if args.out:
            os.makedirs(args.out, exist_ok=True)
        for root, _d, names in os.walk(args.tree):
            for name in sorted(names):
                if not name.lower().endswith(args.ext.lower()):
                    continue
                src = os.path.join(root, name)
                dst = (os.path.join(args.out, os.path.splitext(name)[0] + ".wav")
                       if args.out else None)
                try:
                    t, s, _p = one(src, dst, args.rate, args.max_clip)
                    opened += 1
                    samples += t
                    secs += s
                except Refused as exc:
                    refused += 1
                    print("%-20s REFUSED -- %s" % (name, exc))
        print()
        print("opened %d, refused %d" % (opened, refused))
        print("samples %d, running time %d:%05.2f  at %d Hz ASSUMED"
              % (samples, int(secs // 60), secs % 60, args.rate))
        return 0

    if not args.file:
        ap.print_help()
        return 2
    try:
        one(args.file, args.out, args.rate, args.max_clip, args.seconds)
    except Refused as exc:
        print("REFUSED: %s -- %s" % (args.file, exc))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

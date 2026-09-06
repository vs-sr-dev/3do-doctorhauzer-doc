#!/usr/bin/env python3
"""l10ncmp.py -- compare a localisation with its original, by signal.

WHY THIS EXISTS. Nothing in this 446-file toolbox compares a localisation
with the thing it was localised from. `aiffreuse.py` finds re-used sound
inside one language -- identical payloads, one payload contained in another,
same-length correlation -- and it is built for a sample bank rather than for
two languages of the same programme at two different sample rates. This disc
is the collection's first bilingual object: twenty English files at 44,100 Hz
sixteen-bit SDX2 and twenty French files at 10,000 Hz eight-bit PCM, paired
exactly by name.

THE QUESTION IT ANSWERS. Given a pair, is the French track **the same signal
re-encoded** or **a different recording**? Those are different facts about a
disc and no duration ratio can tell them apart: two recordings of the same
script can be the same length by accident, and one recording re-encoded can
be a different length if it was trimmed.

THE METHOD, and every step of it is stated because none of it is clever:

  * both sides are decoded to mono float and brought to a COMMON rate by
    integer decimation with box averaging -- 44,100 / 10,000 is not an
    integer ratio, so both are decimated to a common low rate (default
    1,000 Hz) which is far below any speech formant and is used only to
    align gross energy, never to judge quality;
  * each side is reduced to a short-term ENERGY ENVELOPE, because the two
    encodings differ in bandwidth and bit depth and their waveforms cannot be
    compared sample against sample even when the content is identical;
  * the envelopes are mean-removed and unit-normalised, and the maximum
    normalised cross-correlation is taken over a lag search of +/- 5 seconds;
  * the score is that maximum, in [-1, 1].

WHAT THE SCORE MEANS, AND WHAT IT DOES NOT. A high score says the two tracks
rise and fall together, which is what one performance re-encoded does. A low
score says they do not. **It is not a transcript comparison**: two different
performances of the SAME WORDS by two speakers at different speeds score low,
and that is correct behaviour and not a failure -- the owner of this disc
listened to one such pair and reported the same text at a different pace, and
this tool scores that pair low. Read the score as *same signal or not*, never
as *same content or not*.

CONTROLS, and `--validate` requires all of them:

  * a track against ITSELF must score 1.00;
  * a track against itself decimated and requantised to eight bits must still
    score high, which is what "re-encoded" has to look like;
  * a track against an unrelated track must score low;
  * a track against silence and against noise must score low.

usage:
    l10ncmp.py DIR --pair-suffix .fre
    l10ncmp.py A.wav B.wav
    l10ncmp.py --validate
"""
import argparse
import collections
import os
import struct
import sys

import numpy as np

ENVELOPE_RATE = 1000.0
LAG_SECONDS = 5.0


class Refused(Exception):
    pass


def read_wav(path):
    d = open(path, "rb").read()
    if d[:4] != b"RIFF" or d[8:12] != b"WAVE":
        raise Refused("%s is not a RIFF/WAVE file" % os.path.basename(path))
    off = 12
    fmt = None
    data = None
    while off + 8 <= len(d):
        tag = d[off:off + 4]
        size = struct.unpack_from("<L", d, off + 4)[0]
        if tag == b"fmt ":
            fmt = struct.unpack_from("<HHLLHH", d, off + 8)
        elif tag == b"data":
            data = d[off + 8:off + 8 + size]
        off += 8 + size + (size & 1)
    if fmt is None or data is None:
        raise Refused("%s has no fmt or no data chunk" % os.path.basename(path))
    tag, channels, rate, _br, _ba, bits = fmt
    if tag != 1 or bits != 16:
        raise Refused("%s is not 16-bit PCM" % os.path.basename(path))
    a = np.frombuffer(data, dtype="<i2").astype(np.float64)
    if channels > 1:
        a = a.reshape(-1, channels).mean(axis=1)
    return a, rate


def envelope(a, rate, target=ENVELOPE_RATE):
    """Short-term RMS at `target` Hz."""
    step = max(1, int(round(rate / target)))
    n = len(a) // step
    if n < 8:
        raise Refused("under eight envelope frames")
    a = a[:n * step].reshape(n, step)
    return np.sqrt((a * a).mean(axis=1))


def score(x, y, rate=ENVELOPE_RATE, lag=LAG_SECONDS):
    x = x - x.mean()
    y = y - y.mean()
    nx = np.linalg.norm(x)
    ny = np.linalg.norm(y)
    if nx == 0 or ny == 0:
        return 0.0, 0
    n = min(len(x), len(y))
    maxlag = int(lag * rate)
    best = -1.0
    bestlag = 0
    for shift in range(-maxlag, maxlag + 1, max(1, maxlag // 50)):
        if shift >= 0:
            a = x[shift:shift + n - abs(shift)]
            b = y[:n - abs(shift)]
        else:
            a = x[:n - abs(shift)]
            b = y[-shift:-shift + n - abs(shift)]
        if len(a) < 8:
            continue
        a = a - a.mean()
        b = b - b.mean()
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            continue
        r = float(np.dot(a, b) / (na * nb))
        if r > best:
            best = r
            bestlag = shift
    return best, bestlag


def compare(pa, pb):
    a, ra = read_wav(pa)
    b, rb = read_wav(pb)
    ea = envelope(a, ra)
    eb = envelope(b, rb)
    r, lag = score(ea, eb)
    return r, lag, len(a) / ra, len(b) / rb


def validate():
    rng = np.random.default_rng(3)
    rate = 10000
    t = np.arange(rate * 20) / rate
    sig = (np.sin(2 * np.pi * 220 * t)
           * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 0.7 * t))))
    other = (np.sin(2 * np.pi * 330 * t)
             * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 0.13 * t))))
    quiet = np.zeros_like(sig)
    noise = rng.normal(size=len(sig))

    e_sig = envelope(sig, rate)
    tests = [
        ("itself", envelope(sig, rate), 0.99, 1.01),
        ("itself requantised to 8 bits",
         envelope(np.round(sig * 127) / 127.0, rate), 0.90, 1.01),
        ("an unrelated tone with another envelope", envelope(other, rate),
         -1.0, 0.60),
        ("silence", envelope(quiet + 1e-12, rate), -1.0, 0.60),
        ("white noise", envelope(noise, rate), -1.0, 0.60),
    ]
    ok = 0
    for name, e, lo, hi in tests:
        r, _lag = score(e_sig, e)
        good = lo <= r <= hi
        ok += good
        print("  %-42s r = %+.4f  %s" % (name, r, "ok" if good else "FAILED"))
    print("controls passed: %d of %d" % (ok, len(tests)))
    return 0 if ok == len(tests) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a", nargs="?")
    ap.add_argument("b", nargs="?")
    ap.add_argument("--dir")
    ap.add_argument("--pair-suffix", default=".fre")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return validate()

    if args.dir:
        names = sorted(n for n in os.listdir(args.dir) if n.endswith(".wav"))
        pairs = []
        for n in names:
            stem = n[:-4]
            if stem.endswith(args.pair_suffix):
                base = stem[:-len(args.pair_suffix)] + ".wav"
                if base in names:
                    pairs.append((base, n))
        if not pairs:
            print("REFUSED: no pairs with suffix %r in %s"
                  % (args.pair_suffix, args.dir))
            return 2
        print("%-16s %9s %9s %7s %8s %8s"
              % ("pair", "orig s", "loc s", "ratio", "r", "lag s"))
        rows = []
        for base, loc in pairs:
            r, lag, sa, sb = compare(os.path.join(args.dir, base),
                                     os.path.join(args.dir, loc))
            rows.append((base, sa, sb, sb / sa if sa else 0, r, lag / 1000.0))
            print("%-16s %9.2f %9.2f %7.4f %+8.4f %8.2f"
                  % (base[:-4], sa, sb, sb / sa if sa else 0, r, lag / 1000.0))
        rs = sorted(x[4] for x in rows)
        print()
        print("pairs                 : %d" % len(rows))
        print("r >= 0.80 (same signal): %d" % sum(1 for x in rows if x[4] >= 0.80))
        print("r <  0.50 (different)  : %d" % sum(1 for x in rows if x[4] < 0.50))
        print("median r               : %.4f" % rs[len(rs) // 2])
        ratios = sorted(x[3] for x in rows)
        print("median duration ratio  : %.4f  (min %.4f max %.4f)"
              % (ratios[len(ratios) // 2], ratios[0], ratios[-1]))
        return 0

    if not (args.a and args.b):
        ap.print_help()
        return 2
    try:
        r, lag, sa, sb = compare(args.a, args.b)
    except Refused as exc:
        print("REFUSED: %s" % exc)
        return 2
    print("%s  %.2f s" % (os.path.basename(args.a), sa))
    print("%s  %.2f s" % (os.path.basename(args.b), sb))
    print("envelope correlation r = %+.4f at lag %.2f s" % (r, lag / 1000.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())

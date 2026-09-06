#!/usr/bin/env python3
"""aiffreuse.py -- find sound RE-USE that a hash census cannot see.

WHY

`hashall.py` finds files with the same SHA-1. On this disc that is four pairs
of creature voices out of forty-three files, and the answer *"forty-three
creatures, thirty-nine recordings"* is what a hash census produces.

It is too low, and the person who owns the disc heard why before any tool did:
two files that sound identical are not byte-identical because one carries 512
bytes more silence, and a third is the same growl at a different pitch. A hash
is exact and sound is not.

THREE TESTS, IN INCREASING ORDER OF WEAKNESS, EACH REPORTED SEPARATELY

  1. **identical payload** -- the SSND sample data is byte-for-byte equal.
     This is what a hash finds, restated on the payload rather than the file so
     that a differing container cannot hide it.

  2. **contained payload** -- one file's whole sample data occurs VERBATIM
     inside another's, at any offset. Exact, and it catches the same recording
     saved with different leading or trailing silence. `bytes.find` does it.

  3. **same recording, different level** -- the two payloads are the same
     length and their sample-level Pearson correlation is at least
     `--r` (default 0.99). A correlation that high between two 8-bit signals
     of tens of thousands of samples is not something two different recordings
     do; the tool also prints the best scalar gain `k` such that `a ~ k*b`, so
     that "a re-encode at a different level" is visible as a number.

AND ONE MEASUREMENT THAT IS DELIBERATELY NOT A TEST

  **envelope correlation.** The RMS envelope in `--windows` windows, computed
  after trimming leading and trailing near-silence and normalised to unit peak,
  correlated between every pair. It is scale- and length-invariant, so it is
  the only one of these that can see a sound re-used at a DIFFERENT PITCH --
  and it is far too generous to be a test: on this disc the median pair of
  unrelated growls scores 0.30 and some unrelated pairs reach 0.90.

  It is printed as a ranked list and **nothing is concluded from it alone**.
  Its job is to say where to look, and every pair it ranks highly that the
  three exact tests do not confirm is reported as UNCONFIRMED, with its
  sample-level correlation beside it so the reader can see how weak the
  evidence is. On this disc the sample-level correlation of those pairs is
  about 0.02, which is nothing.

usage:
    aiffreuse.py TREE                       the three tests plus the ranking
    aiffreuse.py TREE --windows 128 --r 0.99
    aiffreuse.py TREE --top 20
    aiffreuse.py --validate                 negative controls; must fail
"""
import argparse
import hashlib
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sdx2dec import read_aifc                          # noqa: E402

try:
    import numpy as np
except ImportError:                                    # pragma: no cover
    np = None

MIN_BYTES = 1000          # below this a "containment" is chance, not re-use


def load(tree):
    out = []
    for dp, dn, fn in os.walk(tree):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            try:
                ch, fr, bits, rate, codec, ss = read_aifc(p)
            except Exception:
                continue          # not audio: the .dsp files refuse here too
            rel = "/" + os.path.relpath(p, tree).replace(os.sep, "/")
            out.append(dict(path=rel, data=bytes(ss), bits=bits, rate=rate,
                            ch=ch, codec=codec))
    return out


def envelope(data, bits, n):
    x = np.frombuffer(data, dtype=np.int8 if bits == 8 else "<i2")
    x = x.astype(np.float64)
    thr = 2.0 if bits == 8 else 512.0
    nz = np.nonzero(np.abs(x) > thr)[0]
    if len(nz):
        x = x[nz[0]:nz[-1] + 1]
    if len(x) < n:
        return None
    idx = (np.arange(n + 1) * len(x) / n).astype(int)
    e = np.array([np.sqrt((x[idx[i]:idx[i + 1]] ** 2).mean())
                  if idx[i + 1] > idx[i] else 0.0 for i in range(n)])
    m = e.max()
    return e / m if m else e


def corr(a, b):
    x = a - a.mean()
    y = b - b.mean()
    d = (np.sqrt((x * x).sum() * (y * y).sum()))
    return float((x * y).sum() / d) if d > 0 else 0.0


def samples(f):
    return np.frombuffer(f["data"],
                         dtype=np.int8 if f["bits"] == 8 else "<i2"
                         ).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree", nargs="?")
    ap.add_argument("--windows", type=int, default=128)
    ap.add_argument("--r", type=float, default=0.99)
    ap.add_argument("--top", type=int, default=14)
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()

    if a.validate:
        sys.exit(0 if validate() else 1)
    if not a.tree:
        raise SystemExit("aiffreuse: give a TREE or --validate")
    if not os.path.isdir(a.tree):
        raise SystemExit("aiffreuse: %r is not a directory" % a.tree)
    if np is None:
        raise SystemExit("aiffreuse: numpy is required for the envelope and "
                         "correlation measures")

    fs = load(a.tree)
    print("audio files read              : %d" % len(fs))
    if len(fs) < 2:
        raise SystemExit("aiffreuse: fewer than two audio files")
    print("distinct payload SHA-1        : %d"
          % len(set(hashlib.sha1(f["data"]).hexdigest() for f in fs)))
    print()

    tier1 = []
    tier2 = []
    tier3 = []
    for x, y in itertools.combinations(fs, 2):
        da, db = x["data"], y["data"]
        if da == db:
            tier1.append((x, y))
            continue
        lo, hi = (x, y) if len(da) <= len(db) else (y, x)
        if len(lo["data"]) >= MIN_BYTES:
            k = hi["data"].find(lo["data"])
            if k >= 0:
                tier2.append((lo, hi, k))
                continue
        if len(da) == len(db) and x["bits"] == y["bits"]:
            sa, sb = samples(x), samples(y)
            r = corr(sa, sb)
            if r >= a.r:
                g = float((sa @ sb) / (sb @ sb)) if (sb @ sb) else 0.0
                tier3.append((x, y, r, g))

    print("1. IDENTICAL PAYLOAD, byte for byte              : %d pairs"
          % len(tier1))
    for x, y in tier1:
        print("     %7d B   %-40s = %s"
              % (len(x["data"]), x["path"], y["path"]))
    print()
    print("2. ONE PAYLOAD VERBATIM INSIDE ANOTHER           : %d pairs"
          % len(tier2))
    for lo, hi, k in tier2:
        print("     %7d B   %-40s inside %s at offset %d"
              % (len(lo["data"]), lo["path"], hi["path"], k))
    print()
    print("3. SAME LENGTH, sample correlation >= %.3f       : %d pairs"
          % (a.r, len(tier3)))
    for x, y, r, g in tier3:
        print("     %7d B   %-40s ~ %s   r=%.6f  gain k=%.5f"
              % (len(x["data"]), x["path"], y["path"], r, g))
    print()
    exact = set()
    for x, y in tier1:
        exact.add((x["path"], y["path"]))
    for lo, hi, k in tier2:
        exact.add(tuple(sorted((lo["path"], hi["path"]))))
    for x, y, r, g in tier3:
        exact.add(tuple(sorted((x["path"], y["path"]))))
    print("PAIRS CONFIRMED BY AN EXACT TEST                 : **%d**"
          % len(exact))
    print()

    env = {}
    for f in fs:
        e = envelope(f["data"], f["bits"], a.windows)
        if e is not None:
            env[f["path"]] = e
    ranked = []
    for p, q in itertools.combinations(sorted(env), 2):
        ranked.append((corr(env[p], env[q]), p, q))
    ranked.sort(reverse=True)
    med = ranked[len(ranked) // 2][0]
    print("ENVELOPE RANKING -- A HINT, NOT A TEST")
    print("  %d files, %d pairs, %d RMS windows"
          % (len(env), len(ranked), a.windows))
    print("  median pair %.4f  -- an unrelated pair of growls scores this,"
          % med)
    print("  which is why nothing below is a finding on its own.")
    byname = dict((f["path"], f) for f in fs)
    for c, p, q in ranked[:a.top]:
        key = tuple(sorted((p, q)))
        if key in exact:
            tag = "confirmed exactly"
            extra = ""
        else:
            x, y = byname[p], byname[q]
            sa, sb = samples(x), samples(y)
            m = min(len(sa), len(sb))
            extra = "  sample r=%.4f on the overlap" % corr(sa[:m], sb[:m])
            tag = "UNCONFIRMED"
        print("    %.4f  %-34s %-34s  %s%s"
              % (c, os.path.basename(p), os.path.basename(q), tag, extra))
    sys.exit(0)


def validate():
    """Negative controls on the three exact tests. Each MUST fail to fire."""
    if np is None:
        print("FAIL: numpy is not available")
        return False
    ok = True
    rng = np.random.default_rng(1994)
    a = rng.integers(-100, 100, 20000).astype(np.int8).tobytes()
    b = rng.integers(-100, 100, 20000).astype(np.int8).tobytes()
    cases = [
        ("two independent noise signals are not identical", a != b),
        ("neither contains the other verbatim",
         a.find(b) < 0 and b.find(a) < 0),
        ("their sample correlation is under 0.99",
         abs(corr(np.frombuffer(a, dtype=np.int8).astype(float),
                  np.frombuffer(b, dtype=np.int8).astype(float))) < 0.99),
    ]
    for name, good in cases:
        print("%s: %s" % ("ok  " if good else "FAIL", name))
        ok = ok and good
    # positive controls: each test must fire on a case built to trip it
    c = a[:15000]
    pos = [
        ("identical payload detected", a == a),
        ("containment detected", a.find(c) == 0),
        ("a scaled copy correlates above 0.99",
         corr(np.frombuffer(a, dtype=np.int8).astype(float),
              np.frombuffer(a, dtype=np.int8).astype(float) * 0.5) > 0.99),
    ]
    for name, good in pos:
        print("%s: POSITIVE CONTROL -- %s" % ("ok  " if good else "FAIL", name))
        ok = ok and good
    return ok


if __name__ == "__main__":
    main()

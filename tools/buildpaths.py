#!/usr/bin/env python3
"""buildpaths.py -- the file paths of machines that no longer exist.

A path found inside a binary is not a path: it is a *finding*. It names a
directory on a machine that built or authored the file, in a year, and it is
one of the few things on a disc that points outwards. This collection keeps
them, and the rule about "no absolute paths in the repository" explicitly does
not apply to them, because they do not resolve on the machine that wrote the
document -- they resolve on nobody's machine.

Two shapes are looked for, because this disc was built on both kinds of
machine:

  DOS/Windows   a drive letter, a colon, a backslash, then path characters
  Macintosh     a volume name, a colon, then a colon-separated path with no
                leading slash -- the form "Macintosh HD:Work:thing"

The Macintosh form is far looser than the DOS one and would match ordinary
prose, so it is required to have at least two colons, no spaces around them,
and a plausible volume name. Every hit is printed with its file so it can be
checked by hand; nothing here is aggregated without the evidence beside it.

    python tools/buildpaths.py _work/iso _work/hfs
    python tools/buildpaths.py _work/iso --tsv notes/buildpaths.tsv
"""
import argparse
import os
import re
from collections import Counter, defaultdict

DOS = re.compile(rb"[A-Za-z]:[\\/](?:[A-Za-z0-9_~!@#$%^&()\-+=\[\]{}';. ]"
                 rb"{1,40}[\\/]){1,8}[A-Za-z0-9_~\-. ]{1,40}")
MAC = re.compile(rb"[A-Z][A-Za-z0-9 _\-]{1,28}:(?:[A-Za-z0-9 _\-.]{1,32}:)"
                 rb"{1,6}[A-Za-z0-9 _\-.]{1,32}")

NOISE = re.compile(rb"^(?:https?|ftp|mailto|HKEY|SOFTWARE)", re.I)

# A PlayOnline manifest line, which is NOT a Macintosh path.
#
# Final Fantasy XI carries four manifests whose every line reads
#   <22 characters of a permuted base64 alphabet>:<size>:<relative path>
# e.g.  gOysRARnQQMz60s5dpn37T:219402:FTABLE.DAT
# Read by the Mac rule -- volume:folder:file -- each of those 126,899 lines
# is a Macintosh path with a volume called `gOysRARnQQMz60s5dpn37T`, and on
# this object that produced 99,881 findings of which not one was real.  The
# discriminator is that the SECOND component is nothing but digits, which a
# volume-and-folder path essentially never is, and the first is exactly 22
# characters of that alphabet.
#
# This is not a bug in the Mac rule.  It is two formats that happen to
# separate their fields with the same byte, and the fix names the other
# format rather than weakening the rule.
#
# The first version of this repair anchored at the start of the string with
# `^[0-9A-Za-z@_]{22}:[0-9]+:` and removed 38,299 of them -- and left 69,677.
# It failed because the Mac rule requires its first component to begin with
# an UPPERCASE letter, so it does not match the line from its start: it
# matches from the first uppercase letter INSIDE the 22-character hash, and
# produces `IJt:48:ROM` from a line whose hash happens to contain `IJt` near
# its end.  Anchoring was the wrong idea.  The signature that actually
# separates the two formats is positional and unanchored: in a manifest line
# the component BETWEEN the two colons is nothing but digits, and in a
# volume:folder:file path it essentially never is.
MANIFEST_LINE = re.compile(rb"^[0-9A-Za-z@_]{22}:[0-9]+:")
MANIFEST_MID = re.compile(rb":[0-9]+:")

# Rule 0: no change to a file without an assertion that the pattern it
# targets was really there.  If this ever stops matching, the repair below
# is silently doing nothing and the tool must say so rather than print a
# smaller number.
assert MANIFEST_LINE.match(b"gOysRARnQQMz60s5dpn37T:219402:FTABLE.DAT"), \
    "the manifest-line pattern this repair removes does not match the " \
    "line it was written for"
assert not MANIFEST_LINE.match(b"Macintosh HD:Work:thing"), \
    "the manifest-line pattern also swallows a real Macintosh path"
assert MANIFEST_MID.search(b"IJt:48:ROM"), \
    "the mid-string manifest pattern does not match the fragment that " \
    "69,677 false positives were actually made of"
assert not MANIFEST_MID.search(b"Macintosh HD:Work:thing"), \
    "the mid-string manifest pattern also swallows a real Macintosh path"
assert not MANIFEST_MID.search(b"Data:Games:Disk 2:readme"), \
    "a Macintosh path with a digit in a folder name is being rejected"

MANIFEST_REJECTED = Counter()


RUN = re.compile(rb"(.)\1\1\1")            # any byte four times in a row
ALPHA3 = re.compile(rb"[A-Za-z]{3}")
VOWELS = b"aeiouAEIOU"


def language_like(s):
    """The single test that separates a path from compressed rubbish.

    Both path shapes match inside Cinepak and JPEG data -- colons and
    backslashes are ordinary bytes there -- and no list of exceptions will fix
    that. What does fix it is that a path is made of *words*: it has vowels,
    it has a run of at least three letters, and it does not repeat one
    character four times. Applying those three, and nothing else, takes this
    disc from 1,488 matches to 74, and every one of the 74 can be read.
    """
    if RUN.search(s):
        return False
    if not ALPHA3.search(s):
        return False
    letters = [c for c in s if 65 <= c <= 90 or 97 <= c <= 122]
    if len(letters) < 6:
        return False
    v = sum(1 for c in letters if c in VOWELS)
    return v / len(letters) >= MIN_VOWELS


MIN_VOWELS = 0.15          # set by --min-vowels; 0.15 is the value fifteen
                           # other objects were measured with and is the
                           # default, so this tool's history stays comparable.
                           # Broken Sword 3 is the first object whose most
                           # informative build path -- the PDB path in its
                           # executable's CodeView record, twenty letters and
                           # two vowels -- is thrown away by it.


ALLOW_MIXED = False        # set by --mixed-separators; default preserves the
                           # behaviour fifteen other objects were measured with


def looks_dos(s):
    if len(s) < 8:
        return False
    if b"\\" in s and b"/" in s and not ALLOW_MIXED:
        # The rule used to read "no real DOS path mixes the two separators; a
        # match that does came out of binary data that happened to contain
        # both", and on fifteen objects that was true. Deadly Premonition
        # falsifies it 14,328 times: its archive index is built by pasting a
        # constant `D:\programmer_PC\main\` in front of a relative list that
        # uses forward slashes, so every path in it reads
        # `D:\programmer_PC\main\UPDATA/BG/BG.PRM`. The filter is kept off by
        # default so the number stays comparable with the other fifteen, and
        # --mixed-separators turns it off when the object is known to do this.
        return False
    if s.count(b"\\") + s.count(b"/") < 2:
        return False
    return language_like(s)


def looks_mac(s):
    if MANIFEST_LINE.match(s):
        MANIFEST_REJECTED["manifest line"] += 1
        return False
    if MANIFEST_MID.search(s):
        MANIFEST_REJECTED["manifest line fragment"] += 1
        return False
    if b"::" in s or s.startswith(b" ") or s.endswith(b":"):
        return False
    if NOISE.match(s):
        return False
    if b"  " in s:
        return False
    parts = s.split(b":")
    if len(parts) > 6 or len(parts[-1]) < 2:
        return False
    return language_like(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--tsv")
    ap.add_argument("--max-bytes", type=int, default=64 * 1024 * 1024)
    ap.add_argument("--min-vowels", type=float, default=0.15,
                    help="vowel fraction a match must reach to be called a "
                         "path; 0.15 is the historical default")
    ap.add_argument("--mixed-separators", action="store_true",
                    help="accept paths that mix the two separators; off by "
                         "default so the count stays comparable")
    a = ap.parse_args()
    global ALLOW_MIXED, MIN_VOWELS
    ALLOW_MIXED = a.mixed_separators
    MIN_VOWELS = a.min_vowels
    if MIN_VOWELS != 0.15:
        print("!! --min-vowels %.3f: this is NOT the 0.15 fifteen other objects"
              " were measured with; the count below is not comparable with theirs"
              % MIN_VOWELS)

    hits = []
    nfiles = 0
    nbytes = 0
    for root in a.roots:
        for dp, dn, fn in os.walk(root):
            for f in sorted(fn):
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, root).replace(os.sep, "/")
                sz = os.path.getsize(p)
                if sz == 0:
                    continue
                with open(p, "rb") as fh:
                    d = fh.read(min(sz, a.max_bytes))
                nfiles += 1
                nbytes += len(d)
                for m in DOS.finditer(d):
                    s = m.group(0)
                    if looks_dos(s):
                        hits.append((root, rel, m.start(), "DOS",
                                     s.decode("latin-1")))
                for m in MAC.finditer(d):
                    s = m.group(0)
                    if looks_mac(s):
                        hits.append((root, rel, m.start(), "Mac",
                                     s.decode("latin-1")))

    print("files searched : %d" % nfiles)
    print("bytes searched : %d" % nbytes)
    print()
    print("rejected as a PlayOnline manifest line, not a Macintosh path :")
    print("   whole line   : %d" % MANIFEST_REJECTED["manifest line"])
    print("   fragment     : %d" % MANIFEST_REJECTED["manifest line fragment"])
    if sum(MANIFEST_REJECTED.values()) == 0:
        print("  (the repair fired zero times on this object -- either it")
        print("   carries no such manifest, or the repair has stopped working)")
    print()
    kinds = Counter(h[3] for h in hits)
    print("paths found    : %d   (%s)"
          % (len(hits), ", ".join("%s %d" % kv for kv in kinds.most_common())))
    print("distinct strings: %d" % len(set(h[4] for h in hits)))
    print("files carrying at least one : %d" % len(set((h[0], h[1]) for h in hits)))
    print()

    for kind in ("DOS", "Mac"):
        sub = [h for h in hits if h[3] == kind]
        if not sub:
            continue
        print("=" * 74)
        print("%s-shaped paths: %d hits, %d distinct"
              % (kind, len(sub), len(set(h[4] for h in sub))))
        c = Counter(h[4] for h in sub)
        for s, n in c.most_common(60):
            where = sorted(set(h[1] for h in sub if h[4] == s))[:2]
            print("  %3d  %-58s  %s" % (n, s[:58], ", ".join(where)[:60]))
        print()
        roots_ = Counter(h[4].split(":")[0].upper() for h in sub)
        print("  by volume / drive letter:")
        for r, n in roots_.most_common(20):
            print("    %-24s %5d" % (r, n))
        print()

    if a.tsv:
        with open(a.tsv, "w", encoding="utf-8", newline="") as fh:
            fh.write("root\tpath\toffset\tkind\tstring\n")
            for h in hits:
                fh.write("%s\t%s\t%d\t%s\t%s\n" % h)
        print("wrote %s" % a.tsv)


if __name__ == "__main__":
    main()

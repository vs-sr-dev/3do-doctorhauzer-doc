#!/usr/bin/env python3
"""manifest.py -- the sleeve against the bytes, entry by entry.

The back of this disc's sleeve prints a list: five sections, thirty-two named
products, a version number on almost every one, and a small Italian flag on
thirteen. That is a **statement of contents made by the publisher**, and no
other object in this collection has one. This tool is the machinery for
checking it, and nothing in it is disc-specific except the table at the bottom,
which is transcribed from a photograph of the card and is the only part that
comes from outside the image.

For each claim it reports three independent witnesses and does not merge them:

  filename   the version token in the file's own name, if any
  version    the VS_VERSIONINFO FileVersion / ProductVersion of the PE, if any
  language   the VS_VERSIONINFO translation code page, plus any `ita`/`_IT`
             token in a name, plus the presence of an Italian-named
             subdirectory

A claim is `confirmed` when at least one witness agrees to the precision the
sleeve prints, `partial` when a witness agrees to less precision than the
sleeve prints, and `unwitnessed` when nothing in the bytes speaks to it. An
`unwitnessed` claim is not a false one: it is a claim this method cannot reach,
and saying so is the point.

    python tools/manifest.py TREE
    python tools/manifest.py TREE --verbose
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe  # noqa: E402

# --- transcribed from png/2-2006.3, the back of the sleeve, at full size ----
# (section, product as printed, version as printed or None, italian flag)
SLEEVE = [
    ("UTILITY", "G-DATA AntiVirusKit 2006", "2006", True),
    ("UTILITY", "ImgBurn", "1.1.0.0", False),
    ("UTILITY", "RegSeeker", "1.45", True),
    ("UTILITY", "Simple File Shredder", "2.6", False),
    ("UTILITY", "SMART Monitor", "2.1", False),
    ("UTILITY", "SpamPal", "1.594", True),
    ("UTILITY", "TrueCrypt", "4.1", False),
    ("CREATIVITA", "Advanced JPEG Compressor", "4.8", False),
    ("CREATIVITA", "AV Bros. Puzzle Pro", "2.0", False),
    ("CREATIVITA", "FineReader Pro", "8.0", True),
    ("CREATIVITA", "ImTOO 3GP Video Converter", "2.1", False),
    ("CREATIVITA", "KPL", None, False),
    ("CREATIVITA", "MyTV ToGo", "3.0.0", False),
    ("CREATIVITA", "Paint Shop Pro X", "X", True),
    ("CREATIVITA", "QuickTime Alternative", "1.67", False),
    ("CREATIVITA", "StudioLine Photo Classic", "3", True),
    ("CREATIVITA", "UnderCoverXP", "1.10", False),
    ("CREATIVITA", "Zwei-Stein Video Editor", "3.01", False),
    ("INTERNET", "ICQ", "5.04", False),
    ("INTERNET", "OE Viewer", "1.2", False),
    ("INTERNET", "Pegasus Mail", "4.31", False),
    ("INTERNET", "WebSite", "5", True),
    ("INDISPENSABILI", "Ad-Aware SE P.Edition", "1.06", True),
    ("INDISPENSABILI", "Acrobat Reader", "5.0.5", True),
    ("INDISPENSABILI", "DivX Play Bundle", "6.0.3", False),
    ("INDISPENSABILI", "Firefox", "1.5", True),
    ("INDISPENSABILI", "IrfanView", "3.97", True),
    ("INDISPENSABILI", "Mozilla Thunderbird", "1.0.7", True),
    ("INDISPENSABILI", "Orphan Remover", "1.7.5", False),
    ("INDISPENSABILI", "Winamp", "5.12", False),
    ("INDISPENSABILI", "XviD", "1.0.3", False),
    ("INDISPENSABILI", "ZipGenius", "6.0.2.1060", False),
    ("GIOCHI", "4 giochi di strategia gratuiti", None, False),
    ("GIOCHI", "Manuale di Grand Chess Master", None, True),
]

# which directory on the disc each sleeve entry is taken to name. This mapping
# is a reading, not a measurement, and it is written out so it can be argued
# with.
DIRS = {
    "G-DATA AntiVirusKit 2006": "Utility/Gdata2006",
    "ImgBurn": "Utility/ImgBurn",
    "RegSeeker": "Utility/RegSeeker",
    "Simple File Shredder": "Utility/SimpleFileShredder",
    "SMART Monitor": "Utility/SMARTMonitor",
    "SpamPal": "Utility/SpamPal",
    "TrueCrypt": "Utility/TrueCrypt",
    "Advanced JPEG Compressor": "Creativita/AdvancedJPEG",
    "AV Bros. Puzzle Pro": "Creativita/AVBrosPuzzle",
    "FineReader Pro": "Creativita/FineReader8",
    "ImTOO 3GP Video Converter": "Creativita/ImTOO3GP",
    "KPL": "Creativita/KPL",
    "MyTV ToGo": "Creativita/MyTVToGo",
    "Paint Shop Pro X": "Creativita/PSPX",
    "QuickTime Alternative": "Creativita/QuickTimeAlternative",
    "StudioLine Photo Classic": "Creativita/PhotoClassic3",
    "UnderCoverXP": "Creativita/UnderCoverXP",
    "Zwei-Stein Video Editor": "Creativita/ZweiSteinVideo",
    "ICQ": "Internet/ICQ",
    "OE Viewer": "Internet/OEView",
    "Pegasus Mail": "Internet/PegasusMail",
    "WebSite": "Internet/WebSite5",
    "Ad-Aware SE P.Edition": "indispensabili/Ad-Aware",
    "Acrobat Reader": "indispensabili/AcrobatReader",
    "DivX Play Bundle": "indispensabili/DivX",
    "Firefox": "indispensabili/Firefox",
    "IrfanView": "indispensabili/IrfanView",
    "Mozilla Thunderbird": "indispensabili/MozillaThunderbird",
    "Orphan Remover": "indispensabili/OrphansRemover",
    "Winamp": "indispensabili/winamp",
    "XviD": "indispensabili/XviD",
    "ZipGenius": "indispensabili/ZipGenius",
    "4 giochi di strategia gratuiti": "giochi",
    "Manuale di Grand Chess Master": "giochi/Manualegiococompleto",
}

ITA = re.compile(r"(?:^|[^a-z])(ita|italian[oa]?|_it|-it)(?:[^a-z]|$)", re.I)


def digits(s):
    return re.sub(r"[^0-9]", "", s or "")


def listing(tree, rel):
    d = os.path.join(tree, rel.replace("/", os.sep))
    out = []
    if not os.path.isdir(d):
        return out
    for dp, _dn, fn in os.walk(d):
        for f in fn:
            p = os.path.join(dp, f)
            out.append((os.path.relpath(p, tree).replace(os.sep, "/"),
                        os.path.getsize(p)))
    return out


def versions_of(tree, files):
    """VS_VERSIONINFO strings for every PE in this product, plus code pages."""
    vers = []
    langs = set()
    for rel, _size in files:
        if not rel.lower().endswith((".exe", ".dll", ".sys", ".ocx")):
            continue
        try:
            p = pe.PE(os.path.join(tree, rel.replace("/", os.sep)))
            vi = p.versioninfo()
        except Exception:
            continue
        if not vi:
            continue
        fixed = vi.get("fixed") or {}
        for k in ("fileversion", "productversion"):
            if fixed.get(k):
                vers.append((rel, str(fixed[k])))
        # the StringFileInfo block arrives as a flat key/value sequence; the
        # language/codepage id is the 8-hex-digit member of it.
        strings = vi.get("strings") or []
        for i, s in enumerate(strings):
            if not isinstance(s, str):
                continue
            low = s.lower()
            if low in ("fileversion", "productversion") and i + 1 < len(strings):
                vers.append((rel, str(strings[i + 1])))
            if re.fullmatch(r"[0-9A-Fa-f]{8}", s):
                langs.add(s.lower())
    return vers, langs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

    print("sleeve entries transcribed : %d" % len(SLEEVE))
    print("of which carry a version   : %d"
          % sum(1 for r in SLEEVE if r[2]))
    print("of which carry an Italian flag : %d"
          % sum(1 for r in SLEEVE if r[3]))
    print()
    print("%-30s %-11s %-9s %-10s %s"
          % ("sleeve entry", "claims", "version", "italian", "witness"))
    print("-" * 100)

    conf = part = unw = 0
    ita_conf = ita_unw = 0
    for section, name, ver, ita in SLEEVE:
        rel = DIRS.get(name)
        files = listing(a.tree, rel) if rel else []
        if not files:
            print("%-30s %-11s %-9s %-10s %s" % (name[:30], ver or "-",
                                                 "NO FILES", "", rel))
            unw += 1
            continue
        names = " ".join(f for f, _s in files)
        vers, langs = versions_of(a.tree, files)
        vertext = " ".join(v for _f, v in vers)

        vd = digits(ver)
        verdict = "unwitnessed"
        witness = ""
        if ver:
            if vd and vd in digits(names):
                verdict = "confirmed"
                witness = "filename"
            elif vd and vd in digits(vertext):
                verdict = "confirmed"
                witness = "version resource"
            else:
                short = vd[:2]
                if short and (short in digits(names) or short in digits(vertext)):
                    verdict = "partial"
                    witness = "filename/resource, less precise"
        else:
            verdict = "no claim"
        if verdict == "confirmed":
            conf += 1
        elif verdict == "partial":
            part += 1
        elif verdict == "unwitnessed":
            unw += 1

        itav = ""
        if ita:
            if ITA.search(names):
                itav = "confirmed (name)"
                ita_conf += 1
            elif any(x.startswith("0410") for x in langs):
                itav = "confirmed (langid 0410)"
                ita_conf += 1
            else:
                itav = "unwitnessed"
                ita_unw += 1

        print("%-30s %-11s %-9s %-10s %s"
              % (name[:30], ver or "-", verdict[:9], itav[:10],
                 witness or (files[0][0][:44] if files else "")))
        if a.verbose:
            for f, s in sorted(files)[:6]:
                print("      %-70s %10d" % (f, s))
            for f, v in vers[:6]:
                print("      version %-30s %s" % (v, f))

    print()
    versioned = sum(1 for r in SLEEVE if r[2])
    print("versions claimed  %d : confirmed %d, partial %d, unwitnessed %d"
          % (versioned, conf, part, unw))
    flagged = sum(1 for r in SLEEVE if r[3])
    print("italian flags     %d : confirmed %d, unwitnessed %d"
          % (flagged, ita_conf, ita_unw))


if __name__ == "__main__":
    main()

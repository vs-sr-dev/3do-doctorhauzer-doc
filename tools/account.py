"""account.py -- where every byte of the object is, once the containers are open.

Seventeen containers hold 99.9337 % of this installation.  Until they were read
the only accounting possible was by file name.  This one is by member: table,
member payload, and the padding between members, which is a real number here
because VT7A aligns every member to 4,096 bytes and most members are small.

    all <root>            the full accounting, and the checks that must close
    thesis <root>         recorded sound and film, on both denominators

    python tools/account.py all "<root>"
"""
import os
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vt7a import read_table as vt_table, extent, VT7A   # noqa: E402
from aufs import read_table as aufs_table, OSA          # noqa: E402

DISK = None


def gather(root):
    rows = []
    for arch in VT7A:
        p = os.path.join(root, arch)
        n, ver, m2, count, recs = vt_table(p)
        table = 16 + 16 * count
        payload = sum(extent(r) for r in recs)
        rows.append({"file": arch, "kind": "VT7A", "bytes": n,
                     "members": count, "table": table, "payload": payload,
                     "slack": n - table - payload,
                     "raw": sum(r[2] for r in recs)})
    for name in OSA:
        p = os.path.join(root, name)
        n, count, recs = aufs_table(p)
        table = 8 + 12 * count
        payload = sum(r[2] for r in recs)
        rows.append({"file": name, "kind": "AUFS", "bytes": n,
                     "members": count, "table": table, "payload": payload,
                     "slack": n - table - payload, "raw": payload})
    return rows


def all_(root):
    rows = gather(root)
    disk = 0
    for f in sorted(os.listdir(root)):
        p = os.path.join(root, f)
        if os.path.isfile(p):
            disk += os.path.getsize(p)
    print("the object on disk : %d bytes" % disk)
    print()
    print("%-22s %-5s %14s %8s %10s %14s %13s %8s"
          % ("file", "kind", "bytes", "members", "table", "member payload",
             "slack", "slack %"))
    print("-" * 104)
    t = collections.Counter()
    for r in rows:
        print("%-22s %-5s %14d %8d %10d %14d %13d %7.3f %%"
              % (r["file"], r["kind"], r["bytes"], r["members"], r["table"],
                 r["payload"], r["slack"], 100.0 * r["slack"] / r["bytes"]))
        for k in ("bytes", "members", "table", "payload", "slack", "raw"):
            t[k] += r[k]
    print("-" * 104)
    print("%-22s %-5s %14d %8d %10d %14d %13d %7.3f %%"
          % ("the seventeen", "", t["bytes"], t["members"], t["table"],
             t["payload"], t["slack"], 100.0 * t["slack"] / t["bytes"]))
    print()
    print("check: table + payload + slack = bytes  ->  %s"
          % ("OK" if t["table"] + t["payload"] + t["slack"] == t["bytes"]
             else "FAILS"))
    print()
    other = disk - t["bytes"]
    print("the containers      : %14d   %8.4f %% of the object"
          % (t["bytes"], 100.0 * t["bytes"] / disk))
    print("everything else     : %14d   %8.4f %%   (16 files)"
          % (other, 100.0 * other / disk))
    print()
    print("inside the containers:")
    print("   member payload   : %14d   %8.4f %% of the object"
          % (t["payload"], 100.0 * t["payload"] / disk))
    print("   index tables     : %14d   %8.4f %%"
          % (t["table"], 100.0 * t["table"] / disk))
    print("   slack, 4096-byte alignment and tail padding")
    print("                    : %14d   %8.4f %%"
          % (t["slack"], 100.0 * t["slack"] / disk))
    print()
    print("uncompressed size of everything stored inside them: %d" % t["raw"])
    print("   compression ratio over the payload : x %.4f"
          % (t["raw"] / float(t["payload"])))
    return 0


SOUND = {"movie.vt7a": "film and its soundtrack",
         "music.vt7a": "music",
         "sfx.vt7a": "effects"}


def thesis(root):
    rows = gather(root)
    disk = sum(os.path.getsize(os.path.join(root, f))
               for f in os.listdir(root)
               if os.path.isfile(os.path.join(root, f)))
    unused = [r for r in rows if r["file"] == "graphics_720.vt7a"][0]["bytes"]
    av = 0
    print("%-22s %28s %16s" % ("archive", "what it is", "bytes"))
    for r in rows:
        if r["file"] in SOUND:
            print("%-22s %28s %16d" % (r["file"], SOUND[r["file"]], r["payload"]))
            av += r["payload"]
    osa = sum(r["payload"] for r in rows if r["kind"] == "AUFS")
    print("%-22s %28s %16d" % ("the ten .osa", "recorded speech", osa))
    av += osa
    print("-" * 68)
    print("%-22s %28s %16d" % ("together", "", av))
    print()
    print("denominator A, the disk                 : %14d   -> %8.4f %%"
          % (disk, 100.0 * av / disk))
    print("denominator B, the disk minus the")
    print("               resolution not in use    : %14d   -> %8.4f %%"
          % (disk - unused, 100.0 * av / (disk - unused)))
    print()
    print("the same figure counted by whole files rather than by member:")
    byfile = sum(os.path.getsize(os.path.join(root, f))
                 for f in list(SOUND) + OSA)
    print("   %d   -> %.4f %%   (difference %d bytes: index tables and slack)"
          % (byfile, 100.0 * byfile / disk, byfile - av))
    return 0


def main():
    cmd, root = sys.argv[1], sys.argv[2]
    if cmd == "all":
        return all_(root)
    if cmd == "thesis":
        return thesis(root)
    print(__doc__)


if __name__ == "__main__":
    main()

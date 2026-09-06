#!/usr/bin/env python3
"""exepack.py -- identify, validate and unpack a Microsoft EXEPACK image.

Why this exists. `popcorn.exe` of POP-CORN (LACRAL software, 1988) shows four
indicators that are usually written down as "packed": 405 blocks of 256 bytes
and 405 distinct ones, entropy 6.1130, zero relocations in 103 KB, and an
entry point 360 bytes from the end of the file. Eight packer names were
searched for -- `LZ09`, `LZ91`, `PKLITE`, `diet`, `EXEPACK`, `RJSX`, `WWPACK`,
`TINYPROG` -- and all eight occurred zero times.

**Seven of those eight are strings a packed file really does contain. The
eighth is not.** `EXEPACK` is the name of Microsoft's tool; it appears in the
tool, not in its output. What an EXEPACK'd image contains is the two bytes
`RB` at a computed position and the error string `Packed file is corrupt`,
and a search for the tool's name finds neither. A check that cannot fire is
not a check.

WHAT IS ACTUALLY ON DISC

An EXEPACK'd MZ has, immediately before its entry point, a header of 16 or 18
bytes ending in the ASCII signature `RB`, then the unpacker stub, then the
error string, then padding to end of file:

    offset  size  field           meaning
    +0       2    real_ip         the original program's IP
    +2       2    real_cs         the original program's CS, relative
    +4       2    mem_start       unused by the unpacker
    +6       2    exepack_size    bytes from this header to end of file
    +8       2    real_sp         the original SS:SP
    +10      2    real_ss
    +12      2    dest_len        unpacked image size, in PARAGRAPHS
    +14      2    skip_len        18-byte variant only
    +16/+14  2    signature       0x4252, ASCII 'RB'

The signature's last byte sits at `entry - 1`, so `RB` occurring anywhere else
in the file proves nothing -- two bytes turn up by chance in 100 KB. This tool
tests the POSITION, which is the difference between an identification and a
coincidence.

THE COMPRESSION IS RUN-LENGTH AND THAT MATTERS

EXEPACK is not an LZ packer. It stores literal runs verbatim and only collapses
repeats, so an EXEPACK'd image keeps its text legible and lands around 6 bits
of entropy rather than the 7.9 an LZ packer produces. **The 512 readable French
strings in `popcorn.exe` are not evidence against packing; they are what this
particular packer looks like.** That reasoning was the thing this tool was
written to settle.

The packed stream is read BACKWARDS from just below the header, past a run of
0xFF padding, as a sequence of commands:

    cmd = src[p]; p -= 1
    length = u16 at src[p-1:p+1]; p -= 2
    cmd & 0xFE == 0xB0 : fill  -- one byte follows; write it `length` times
    cmd & 0xFE == 0xB2 : copy  -- copy `length` bytes, descending
    cmd & 0x01         : this was the last command

    python exepack.py FILE...              identify and validate
    python exepack.py --unpack FILE OUT    write the unpacked load image
    python exepack.py --refuse FILE...     assert NOT EXEPACK; exit 1 if one is

Standard library only. It reads the object and writes only where told to, and
it never executes anything.
"""

import argparse
import os
import struct
import sys

SIG = 0x4252  # 'RB'
ERRMSG = b"Packed file is corrupt"


class NotExepack(Exception):
    pass


def mz_facts(data):
    if len(data) < 32 or data[:2] not in (b"MZ", b"ZM"):
        raise NotExepack("not an MZ image")
    (e_cblp, e_cp, e_crlc, e_cparhdr, _mn, _mx, e_ss, e_sp, _ck,
     e_ip, e_cs, _lfarlc, _ov) = struct.unpack_from("<13H", data, 2)
    hdr = e_cparhdr * 16
    declared = ((e_cp - 1) * 512 + e_cblp) if e_cblp else e_cp * 512
    return {
        "hdr": hdr,
        "declared": declared,
        "residue": len(data) - declared,
        "reloc": e_crlc,
        "entry": hdr + e_cs * 16 + e_ip,
        "cs": e_cs, "ip": e_ip, "ss": e_ss, "sp": e_sp,
    }


def parse(data):
    """Return the EXEPACK facts, or raise NotExepack with a stated reason."""
    m = mz_facts(data)
    entry = m["entry"]
    if not (32 < entry <= len(data)):
        raise NotExepack("entry point %d is outside the file" % entry)
    if data[entry - 2:entry] != b"RB":
        raise NotExepack("no 'RB' at entry-2 (found %r)"
                         % data[max(0, entry - 2):entry])

    # 18-byte header first: if its exepack_size accounts for exactly the tail
    # from the header start to EOF, that is the variant. Otherwise 16.
    facts = None
    for hlen in (16, 18):
        start = entry - hlen
        if start < m["hdr"]:
            continue
        f = struct.unpack_from("<%dH" % (hlen // 2), data, start)
        if f[-1] != SIG:
            continue
        size = f[3]
        if size == len(data) - start:
            facts = (hlen, start, f)
            break
    if facts is None:
        raise NotExepack("'RB' at entry-2 but no header whose exepack_size "
                         "closes on the file length -- refusing to guess")
    hlen, start, f = facts
    out = {
        "mz": m,
        "hdr_len": hlen,
        "hdr_off": start,
        "real_ip": f[0], "real_cs": f[1], "mem_start": f[2],
        "exepack_size": f[3], "real_sp": f[4], "real_ss": f[5],
        "dest_len_par": f[6],
        "skip_len": f[7] if hlen == 18 else None,
        "dest_bytes": f[6] * 16,
        "packed_from": m["hdr"],
        "packed_to": start,
        "errmsg": data.count(ERRMSG),
        "tail": len(data) - start,
    }
    out["packed_bytes"] = out["packed_to"] - out["packed_from"]
    out["ratio"] = (out["dest_bytes"] / float(out["packed_bytes"])
                    if out["packed_bytes"] else 0.0)
    out.update(parse_tail(data, entry, start))
    return out


def parse_tail(data, entry, hdr_off):
    """Account for every byte from the EXEPACK header to end of file.

    The MZ header of an EXEPACK'd image declares zero relocations, which is
    what made `popcorn.exe` look strange in the first place. The relocations
    have not gone away: EXEPACK moves them into its own table after the error
    message, as sixteen groups -- one per 0x1000 of segment -- each a u16
    count followed by that many u16 offsets. Parsing it is the difference
    between "zero relocations, which is unusual" and "zero in the MZ header
    and thirty-five in the packer's own table, which is normal".
    """
    msg = data.find(ERRMSG, entry)
    res = {"stub_bytes": None, "msg_off": msg, "reloc_entries": None,
           "reloc_groups": [], "tail_residue": None}
    if msg < 0:
        return res
    res["stub_bytes"] = msg - entry
    q = msg + len(ERRMSG)
    total = 0
    groups = []
    for g in range(16):
        if q + 2 > len(data):
            return res
        n = struct.unpack_from("<H", data, q)[0]
        q += 2
        if q + 2 * n > len(data):
            return res
        if n:
            groups.append((g, n))
        q += 2 * n
        total += n
    res["reloc_entries"] = total
    res["reloc_groups"] = groups
    res["tail_residue"] = len(data) - q
    res["hdr_off"] = hdr_off
    return res


def unpack(data, facts):
    """Run the backwards RLE. Raises on any command byte it cannot name."""
    src = bytearray(data[facts["packed_from"]:facts["packed_to"]])
    p = len(src) - 1
    while p >= 0 and src[p] == 0xFF:
        p -= 1
    if p < 0:
        raise NotExepack("packed region is all 0xFF")
    out = bytearray(facts["dest_bytes"])
    q = len(out)
    fills = copies = 0
    while True:
        if p < 2:
            raise NotExepack("ran off the front of the packed region")
        cmd = src[p]
        p -= 1
        length = src[p - 1] | (src[p] << 8)
        p -= 2
        op = cmd & 0xFE
        if op == 0xB0:
            if p < 0:
                raise NotExepack("fill command with no byte after it")
            b = src[p]
            p -= 1
            if q - length < 0:
                raise NotExepack("fill of %d underruns the destination"
                                 % length)
            q -= length
            out[q:q + length] = bytes([b]) * length
            fills += 1
        elif op == 0xB2:
            if p - length + 1 < 0 or q - length < 0:
                raise NotExepack("copy of %d underruns a buffer" % length)
            q -= length
            for i in range(length):
                out[q + length - 1 - i] = src[p - i]
            p -= length
            copies += 1
        else:
            raise NotExepack("unknown command byte 0x%02X at %d" % (cmd, p + 3))
        if cmd & 1:
            break
    return bytes(out), {"fills": fills, "copies": copies,
                        "unwritten_head": q, "src_left": p + 1}


def report(path, data):
    f = parse(data)
    m = f["mz"]
    print("=== %s ===" % path)
    print("  file bytes                 : %d" % len(data))
    print("  MZ header / declared / res : %d / %d / %+d"
          % (m["hdr"], m["declared"], m["residue"]))
    print("  relocations in MZ header   : %d" % m["reloc"])
    print("  entry point                : %04X:%04X = file offset %d "
          "(%d from EOF)" % (m["cs"], m["ip"], m["entry"],
                             len(data) - m["entry"]))
    print("  EXEPACK header             : %d bytes at %d, signature 'RB' at "
          "%d" % (f["hdr_len"], f["hdr_off"], f["hdr_off"] + f["hdr_len"] - 2))
    print("  exepack_size               : %d, and %d - %d = %d  -- closes"
          % (f["exepack_size"], len(data), f["hdr_off"], f["tail"]))
    print("  original CS:IP  SS:SP      : %04X:%04X  %04X:%04X"
          % (f["real_cs"], f["real_ip"], f["real_ss"], f["real_sp"]))
    print("  dest_len                   : %d paragraphs = %d bytes"
          % (f["dest_len_par"], f["dest_bytes"]))
    print("  skip_len                   : %s" % f["skip_len"])
    print("  packed region              : [%d, %d) = %d bytes"
          % (f["packed_from"], f["packed_to"], f["packed_bytes"]))
    print("  compression ratio          : %.4f  (unpacked over packed)"
          % f["ratio"])
    print("  'Packed file is corrupt'   : %d occurrence(s), at %d"
          % (f["errmsg"], f["msg_off"]))
    print("  unpacker stub              : %s bytes" % f["stub_bytes"])
    print("  packer relocation table    : %s entries in groups %s"
          % (f["reloc_entries"],
             ", ".join("0x%X000:%d" % (g, n) for g, n in f["reloc_groups"])
             or "-"))
    if f["tail_residue"] is not None:
        print("  tail accounting            : %d hdr + %d stub + %d msg + "
              "%d reloc = %d, residue %+d"
              % (f["hdr_len"], f["stub_bytes"], len(ERRMSG),
                 len(data) - f["hdr_off"] - f["hdr_len"] - f["stub_bytes"]
                 - len(ERRMSG) - f["tail_residue"],
                 f["tail"] - f["tail_residue"], f["tail_residue"]))
    return f


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--unpack", metavar="OUT",
                    help="write the unpacked load image here (one input only)")
    ap.add_argument("--refuse", action="store_true",
                    help="assert none of the inputs is EXEPACK; exit 1 if one is")
    args = ap.parse_args(argv)

    if args.refuse:
        bad = 0
        for p in args.paths:
            with open(p, "rb") as fh:
                data = fh.read()
            try:
                parse(data)
            except NotExepack as e:
                print("%-24s REFUSED: %s" % (os.path.basename(p), e))
            else:
                print("%-24s IS EXEPACK -- CONTROL FAILED" % os.path.basename(p))
                bad += 1
        print("\nexepack.py: %d of %d refused" % (len(args.paths) - bad,
                                                  len(args.paths)))
        return 1 if bad else 0

    if args.unpack and len(args.paths) != 1:
        raise SystemExit("exepack.py: --unpack takes exactly one input")

    ok = 0
    for p in args.paths:
        with open(p, "rb") as fh:
            data = fh.read()
        try:
            f = report(p, data)
        except NotExepack as e:
            print("=== %s ===" % p)
            print("  NOT EXEPACK: %s" % e)
            continue
        ok += 1
        if args.unpack:
            img, stats = unpack(data, f)
            with open(args.unpack, "wb") as out:
                out.write(img)
            print("  unpacked                   : %d bytes to %s"
                  % (len(img), args.unpack))
            print("  fill / copy commands       : %d / %d"
                  % (stats["fills"], stats["copies"]))
            print("  destination bytes never written at the head : %d"
                  % stats["unwritten_head"])
            print("  packed bytes left unread   : %d" % stats["src_left"])
    print()
    print("exepack.py: %d of %d inputs are EXEPACK images" % (ok, len(args.paths)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

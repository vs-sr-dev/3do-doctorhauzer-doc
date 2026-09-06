# 02 — the technical sheet: every line carries the command that makes it again

*Measure: everything below was produced by the command printed beside it, on
`Doctor Hauzer (Japan).chd`, 149,661,045 bytes, sha1
`94a5f18422f811191a472d89e0353a387e7e8c14`.*

**Every command in this repository needs `PYTHONIOENCODING=utf-8` in the
environment.** Three filenames on this disc are Shift-JIS and `opera.py --list`
and `hashall.py` both die on them under the default Windows console codepage,
with `hashall.py` leaving a hash list truncated at 199 records of 366 and no
error a caller would notice. See chapter 17, inherited defect sixteen.

## The container

```
bin/chdman.exe info -i "Doctor Hauzer (Japan).chd"
```

```
File Version    5                    Compression   cdlz, cdzl, cdfl
Logical size    314,078,400          CHD size      149,661,045   ratio 47.7 %
Hunk Size       19,584               Unit Size     2,448
Total Units     128,300              Total Hunks   16,038
SHA1            cd5c04d6bdd2f4284bf5816a009987fb48501239
Data SHA1       7f4e6975faa56aaab5bb4407e6b1b9f7628656bb
Metadata        TRACK:1 TYPE:MODE1_RAW SUBTYPE:NONE FRAMES:128300 PREGAP:0
```

**128,300 units for 128,300 frames — zero padding units.** Across six discs the
counts are 2, 0, 0, 2, 1 and **0**, so two of six do not pad and they are not
the same pair the notes' `[1 of 5]` identified.

```
bin/chdman.exe extractcd -i "..." -o _work/hauzer.cue -ob _work/hauzer.bin
```

```
301,761,600 bytes = 128,300 sectors x 2,352
user area   262,758,400 bytes = 128,300 x 2,048
of a 74-minute CD (333,000 sectors)              38.5285 %
```

## The sectors

```
python tools/mode1.py _work/hauzer.bin --census
```

```
sectors                                     128,300
sync correct 00 FF*10 00                    128,300 / 128,300
mode byte 1                                 128,300 / 128,300  (100.0000 %)
header MSF != LBA + 150                     0
header MSF non-BCD                          0
EDC mismatches (bytes 0..2063)              0 / 128,300
ECC P mismatches                            0
ECC Q mismatches                            0
reserved bytes 2068..2075 non-zero          0 / 128,300
all-zero user sectors                       9,241  (7.2027 %) in 2,579 runs
frame overhead 304 x sectors                39,003,200  (12.9252 %)
```

**Not one sector fails.** What this repository says about the disc is a
statement about a pressing.

## The volume label

```
python tools/opera.py _work/hauzer.bin --selftest --label
```

```
label           CD-ROM              identifier      238494704 (0x0E3723F0)
block size      2,048               blocks declared 128,000
root dir id     659278086           root dir blocks 1
root copies     7  ->  85, 19675, 38475, 57690, 79779, 100363, 109741
label length    128 bytes (the record is 132; see the platform notes, section 2)
```

`128,000 x 2,048 = 262,144,000 = 250 MiB exactly` — the whole-mebibyte rule, a
sixth time. **300 sectors lie past the declared volume and every one is
all-zero**, contiguous at 128,000..128,299.

**The root's seven copies are the first evenly spread layout of six**, at gaps
of 19,590 / 18,800 / 19,215 / 22,089 / 20,584 / 9,378 — after 5+2, 7+0, 6+1,
4+3 and 1+4+2, this one is 1+1+1+1+1+1+1.

## The tree

```
PYTHONIOENCODING=utf-8 python tools/opera.py _work/hauzer.bin --list
PYTHONIOENCODING=utf-8 python tools/opera.py _work/hauzer.bin --extract _work/files
PYTHONIOENCODING=utf-8 python tools/hashall.py _work/files > notes/sha1-all.txt
```

```
files          366        directories    32        bytes  161,346,866
distinct sha1  362        unreadable      0        records in the hash list 366
```

**366 records for 366 files, checked before the list was used for anything.**

Four files share two hashes: `/OrgData/macro/macro400` equals
`/OrgData/macro/macroEnd`, and four one-byte `junk` files under `/System` hold
`\r` and hash `11f4de6b…`, which is the second and third discs' value and not
the first's. **Zero zero-length files**, a fourth confirmation.

## The sector map, which closes

```
python tools/sectormap3do.py _work/hauzer.bin --runs
```

```
file        79,010   61.5822 %        copy    43,970   34.2712 %
dir             40    0.0312 %        dircopy     84    0.0655 %
duck         4,896    3.8161 %        zero       300    0.2338 %
other            0    0.0000 %
            -------
            128,300  100.0000 %       double-claimed blocks: 0
```

## The copies

```
python tools/opercopies.py _work/hauzer.bin
python tools/filecopies.py _work/hauzer.bin --list --bands --bundles
```

```
groups compared        113 (33 directories, 80 files)
second or later copies  44,054 blocks  (43,970 file + 84 directory)
file copies in bytes    90,050,560  = 34.2712 % of the pressing
groups whose copies are byte-identical  79 of 80 files, and the one is /rom_tags
repeated contiguous runs of files       24, pressed 67 times, holding 47 files
```

## `iamaduck`, counted twice

```
python -c "count iamaduck sequentially over _work/hauzer.bin"     1,344,484
per-sector census, sectors that are 256 repetitions                   4,896
per-sector census, sectors with a PARTIAL run           585, holding 91,107
per-sector total                                                  1,344,483
sequential minus per-sector (one match straddling a join)                 1
```

**4,896 pure-fill sectors is the sector map's `duck` bucket exactly.** The other
**585 sectors are blocks the file system owns whose unused tail was never
overwritten** — the round-up slack in files' last blocks and the space past
`first_free_byte` in directory blocks. That is the platform notes' *count the
all-zero sectors twice* lesson, transferred to the fill, and it is the
difference between "4,896 sectors of fill" and "1.34 million occurrences".

## The fill arithmetic, which closes to zero sectors

The notes' rule is that the fill is the complement of the sectors the file
system uses. On this disc the sum needs a **fourth** term the earlier discs did
not have:

```
how full: 161,346,866 / 262,758,400                          61.4050 %
round-up slack in files' last blocks  79,010 - 161,346,866/2,048 = 227.35 sectors
the index: 40 directories + 84 directory copies                    124
FILE SECOND COPIES                                              43,970   <- new
the zero tail past the declared volume                             300
                                                                --------
                                                                44,621.35

predicted fill = 100 - 61.4050 - 44,621.35/128,300 x 100  =  3.8161 %
measured fill  = 4,896 / 128,300                          =  3.8161 %
difference                                                =  0.0000 points
                                                          =  0.00 sectors
```

## `/rom_tags`, read as a block and not as a file

```
python tools/romtags.py _work/files/rom_tags
```

The directory entry declares **128 bytes** and the block holds **six records,
192 bytes** — types `0x10` and `0x05` lie past the declared end, exactly the
trap the platform notes carry at `[1 of 4]`. Read from the block:

```
      copy 0 (block 1)                  copy 1 (block 226)
0x0d  A 1          B 5,168              A 0xffffff20   B 5,168
0x07  A 5          B 79,692             A 0xffffff24   B 79,692
0x0c  A 0xa9d42b59 B 0                  identical -- the signing pass leaves it
0x02  A 120,667    B 121                identical
0x10  A 69         B 2,912              A 0xffffff64   B 2,912
0x05  A 126,134    B 131,072            A 0x0001ebd5   B 131,072
+224  64 bytes of high entropy          wholly different from copy 0
```

**Four identities, all exact:**

```
0x0c  0xa9d42b59 = 2,849,254,233 s from 1904-01-01  =  1994-04-15 11:30:33
0x07  B 79,692   == /System/Kernel/os_code           79,692   FIFTH distinct value
0x10  B 2,912    == /System/Kernel/misc_code          2,912
0x02  A/B 120,667 / 121 == /launchme's directory entry, exactly
0x05  A 126,134  == /signatures' first block 126,135 minus one   FIFTH of five
0x0d  B 5,168    vs /System/Kernel/boot_code 5,050   miss +118   FOURTH of four
```

## The executables

```
python tools/aifcensus.py _work/files
```

```
AIF images                      36        SWI &11 at 0x10       36 of 36
entry point 0x100               36 of 36  flags at 0x30 == 32   36 of 36
image base == 0                 36 of 36  debug size == 0       36 of 36
reloc target == ro + rw + debug  35 of 36
the one exception               /OrgData/program/sramtools, at ro + rw + 4
compressed images                4 of 36  -- AUDIOFOLIO GRAPHIX eventbroker shell
  stub lengths                   392 (x2), 456 (x2)
  the two populations are disjoint on both statistics : True
by directory   (root) 1   /OrgData 1   /System 34
```

## The audio

```
python tools/aiffread.py _work/files
python tools/thesis3do.py _work/files 128300 128000
python tools/streamaudit.py _work/files/OrgData/stream --census --resync
```

```
music, 12 AIFF-C, SDX2                45,410,350 B sample data   17:09.71
effects, 48 AIFF, codec NONE               638,903                0:57.94
the SDK's sinewave, 1 AIFF                   8,820                0:00.10
56 .dsp refused for having no COMM -- they are FORM 3INS instruments
inside the eight films, SDX2 22,050 Hz stereo  21,553,152          8:08.73
                                          ----------
ALL RECORDED SOUND                        67,611,225 = 25.7313 % of the user area
```

## The collection

```
python tools/sdkdiff.py _work/files <neighbour>/_work/files
python tools/crossall.py notes/sha1-all.txt --collection <root> --skip 3do-doctorhauzer-doc
```

```
neighbour                       identical  changed  only A  only B
Crash 'n Burn      1993-09-09         45       48       9       1
AD&D Slayer        1994-08-16         38       63       1      15
Alone in the Dark  1994-12-19         38       63       1      16
SSF2T              1995-01-10         38       63       1      15
Wolfenstein 3D     1995-09-06         32       43      27      51

repositories swept  85      my distinct sha1  362
CROSSINGS           56 of 362 = 15.5 %, and 56 of the 56 are under /System
empty-file sha1 among mine : no      (the trap: 32 occurrences in 12 repositories)
```

## The refusals, which are measurements

```
iso9660.py --vd          descriptors : 0, and it exits 0 (inherited defect 12)
picsdec.py --tree        REFUSED: no .pics files
itdpak.py --tree         REFUSED: no .PAK files
sampdec.py --tree        opened 0, refused 0 -- no .samp files
foreign.py --tree        no file carries a foreign-architecture signature
aiffread.py              56 .dsp correctly refused for having no COMM
ccbread.py census        36 files do not chain, and 33 of them are the rooms
protscan.py --all-files  eleven markers, 0 hits; positive control fires on 339
```

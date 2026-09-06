# 09 — the executables: an SDK older than four of five, and the exception is the studio's

*Measure: 36 ARM Image Format images, the five header identities on 36 of 36;
the relocation target on 35 of 36 and the one exception named; four compressed
images, the same four as the 1993 launch title; `/System` 102 files, 45 of them
byte-identical with the launch title and 38 with each of the other four.*

## The header, on a sixth disc

```
python tools/aifcensus.py _work/files
```

```
AIF images                       36
SWI &11 at 0x10                  36 of 36
entry point 0x100 from the BL    36 of 36
flags at 0x30 == 32              36 of 36
image base at 0x28 == 0          36 of 36
debug size at 0x1C == 0          36 of 36
reloc target == ro + rw + debug  35 of 36
```

**Entry point 0x100 holds on 36 of 36 here**, against the platform notes'
running 164 of 164 over the first three discs, and it remains the strongest
single number that document carries. **Thirty-six is the smallest
image count of the six** — against 34, 93, 37, 41 and 41 — which is what an
older, smaller `/System` gives.

## The relocation exception, and it is named

The platform notes' open question 11 asks whether the `ro + rw + 4` anomaly is
always the title's own binary. It had two points: on the fourth disc 3DO's 38
images were 38 of 38 on the rule and the studio's 3 were 1 of 3; on the fifth,
3DO's 38 were 38 of 38 and the studio's exception was `/playmovie`.

```
the one image whose BL at offset 4 does not point at ro + rw + debug:

  /OrgData/program/sramtools    target 61,360   ro + rw + debug 61,356   diff +4
```

**`sramtools` is the studio's**, in the studio's own directory, and the
thirty-four `/System` images are 34 of 34 on the rule. **Three discs, three
confirmations, and zero exceptions among 110 SDK images.** The question can be
stated as an answer: *the exception is a property of how a studio invoked the
linker, and it has never once been an SDK image.*

`sramtools` is 68,108 bytes and it is the save-game utility — `/launchme` holds
`/nvram/RH_HAUZERJ`, and chapter 13 takes that up.

## Compression, decided structurally

The platform notes are emphatic that the size relation is not a test and that
the `BL` at offset 0 plus the appended decompressor is:

```
path                       stored   stub    entropy   cond=E share
/System/Folios/AUDIOFOLIO   38,160   456      7.015     0.149
/System/Folios/GRAPHIX      24,152   456      6.965     0.124
/System/Tasks/eventbroker   16,252   392      7.019     0.131
/System/Tasks/shell         20,596   392      6.972     0.173

images with a stub, uncompressed : 0 of 32   (must be 0)
entropy   compressed 6.9653..7.0189   uncompressed 4.9518..6.1984
cond=E    compressed 0.1236..0.1730   uncompressed 0.5641..0.7846
the two populations are disjoint on both statistics : True
```

**Four of thirty-six, and all four are operating-system components.** Six discs,
six studios, and **not one has compressed a single one of its own binaries** —
`/launchme` and `/OrgData/program/sramtools` both carry the `e1 a0 00 00` NOP at
offset 0.

**And the four are exactly the launch title's four.** Crash 'n Burn compresses
`AUDIOFOLIO`, `GRAPHIX`, `eventbroker` and `shell`; so does this disc.
`OPERAMATH` is **not** compressed here, where it is on the second, fourth and
fifth discs. The platform notes carry `OPERAMATH` compressed-then-not-then-
compressed at `[1 of 3]`; the fourth value is *not compressed*, and it agrees
with the 1993 disc rather than with the 1994-95 group.

## `/System` is an SDK version and it dates the pressing four ways

```
python tools/sdkdiff.py _work/files <neighbour>/_work/files
```

```
A = Doctor Hauzer, 102 files, 403,961 bytes

neighbour                       identical  changed  only A  only B
Crash 'n Burn      1993-09-09         45       48       9       1
AD&D Slayer        1994-08-16         38       63       1      15
Alone in the Dark  1994-12-19         38       63       1      16
SSF2T              1995-01-10         38       63       1      15
Wolfenstein 3D     1995-09-06         32       43      27      51
```

**The closest neighbour is the 1993 launch title, and the three discs that share
one SDK drop are all exactly equidistant at 38 and 63.** That is what a
1994-04-15 pressing should look like and it is an independent confirmation of
the `0x0c` date from a completely different measurement.

The `/System` file count is a clock of its own:

```
Crash 'n Burn      1993-09-09     94
Doctor Hauzer      1994-04-15    102
AD&D Slayer        1994-08-16    116
Alone in the Dark  1994-12-19    117
SSF2T              1995-01-10    116
Wolfenstein 3D     1995-09-06    126
```

**Six points, and this disc's 102 lands between 94 and 116 exactly where its
date says.** With the instrument bank's 53, 56, 63, 63, 63, 77 (chapter 08) and
the `os_code` series below, that is **three independent monotone series** that
all place this disc second.

## `os_code`, a fifth distinct value, and it lands in order

The platform notes record that `/rom_tags` record `0x07` carries
`/System/Kernel/os_code`'s size in its `+12` word, on four discs of four.

```
                   record 0x07 field B     /System/Kernel/os_code
Crash 'n Burn      1993-09-09    78,852              78,852
Doctor Hauzer      1994-04-15    79,692              79,692    <- FIFTH value
AD&D Slayer        1994-08-16    85,896              85,896
Alone in the Dark  1994-12-19    85,896              85,896
SSF2T              1995-01-10    85,896              85,896
Wolfenstein 3D     1995-09-06   115,520             115,520
```

**Five of five exact, and the fifth distinct value falls between the launch
title's and the 1994-95 group's** — 78,852 < 79,692 < 85,896 — in the position
the pressing date demands. Nothing in `os_code` knows what date is in
`/rom_tags`; two unrelated numbers agree on the ordering.

`0x10` field B is **2,912** and `/System/Kernel/misc_code` is **2,912** — a
fourth exact match. And `0x0d` field B is 5,168 against `boot_code`'s 5,050:

```
                   record 0x0d field B     boot_code      miss
Crash 'n Burn                  2,076         2,076           0
SSF2T                          5,168         5,050        +118
AD&D Slayer                    5,168         5,050        +118
Alone in the Dark              5,168         5,050        +118
Doctor Hauzer                  5,168         5,050        +118
Wolfenstein 3D                                            -1,744
```

**A constant miss of exactly +118 on four discs of six**, which the platform
notes call a field with a fixed overhead in it rather than a coincidence — the
launch title matches exactly and Wolfenstein 3D misses the other way. This disc
makes the +118 group four, and it does so on an SDK **eight months older** than
the other three in that group, so whatever the 118 bytes are, they are not a
property of one SDK drop.

`0x05` field A is 126,134 and `/signatures` begins at block **126,135** — the
off-by-one *last block before* shape, now **five of five**.

## `/System` names are upper case in copy 0, and it is not an older convention

The pre-briefing noted that this disc writes `OPERAMATH`, `GRAPHIX`,
`AUDIOFOLIO`, `ALLOCATE`, `CHKNVRAM`, `GDBUG` where later discs write lower
case, and asked whether that is an earlier naming convention.

**It is not, and the platform notes already answer it.** The case fold lives in
the directory *copies*: copy 0 holds the upper-case letter and copies 1 and 2
hold the folded form, on 272 of 272 differing bytes on the third disc and on 206
of 207 on the second. Measured here, over all 33 directory groups:

```
/System/Folios     copy at 44,136    26 differing bytes,  26 are a case bit
/System/Programs   copy at 44,139   154 differing bytes, 154 are a case bit
/System/Scripts    copy at 44,141    10 differing bytes,  10 are a case bit
                                    ---                  ---
                                    190                  190
```

**190 of 190 differing bytes are a case bit, and copy 0 holds the upper case on
every one.** Three directory groups plus `/rom_tags` is four groups that
disagree, which is `opercopies.py`'s count of four exactly. So the upper case is not an SDK generation — it is copy 0, on every
disc that has been looked at, and reading a single copy is what makes it look
like a convention.

## The SDK's own build stamp, and it is inside a compressed image

```
@(#) over the whole 301,761,600-byte track : 1   (chance expectation 0.0703)
```

The one occurrence is in `/System/Folios/GRAPHIX`, which is one of the four
compressed images, so the string is interleaved with compression escapes and
reads as damage:

```
@(#). gra.hx.   .    .  2..45.72  . 04/.06/9. 2.:57:.42 sBan.pot.1__ZD
```

The shape is unmistakable next to the three discs that ship an uncompressed
`operamath`:

```
neighbours   @(#) operamath.dev    21.10.603  05/10/94 21:49:54 stan port1_3
this disc    @(#) graphix          2?.45.72   04/06/9?  2?:57:42 stan port1_?
```

**Name, version, date, time, the login `stan`, the port tag `port1_`.** The
readable part of the date is `04/06/9` with the year digit destroyed by a
compression escape, against the `05/10/94` the three 1994-95 discs share. **This
is a sixth value on the what-string count** — 0, 7, 2, 7, 7 and **1** — and one
occurrence in one file is what a `/System` of 102 files gives where a `/System`
of 116 gives seven in six files.

**The four compiler names are still zero.** `Norcroft` 0, `armcc` 0, `armasm` 0,
`armlink` 0 over 301,761,600 bytes, so the fifth disc's single `armlink` — found
inside a buffer of a Macintosh's uninitialised memory — remains the only one in
the collection.

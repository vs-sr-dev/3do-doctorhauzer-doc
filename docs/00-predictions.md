# 00 — predictions: written before the disc was opened, and left where they fall

*Measure: 366 files, 161,346,866 bytes, 128,300 sectors of a 74-minute CD's
333,000. Every figure below names its denominator.*

This is the fifty-seventh session of this pipeline and the sixth 3DO disc. The
rule that governs this file has not changed: **the predictions are written
before anything is opened, they are scored afterwards by a command, and the
wrong ones are left visible.**

**What was read before a clause was written.** `3do-platformnotes-doc/3do-platform-notes.md`
at commit `7fc9840`, **all of it**, measured at **2,881 lines** by `wc -l` and
not the 2,867 the session brief states — the first correction of the day and it
is against the brief. Reading it saved four predictions outright: the 128-vs-132
label question, the 1904 epoch, the `0x02` block identity and the fixed +224
offset of the signature are all closed in that document and are not re-litigated
here.

**What was measured before these predictions were written, on the brief's own
instruction, and is therefore worth ZERO points.** The brief's task 0 orders
`cvidmovie.py` run on the eight films and frames sent to the owner before
anything else, because his answer arrives while the predictions are still being
typed. That was done. **Everything it produced is in §A.0 and no clause below
may claim it.**

---

## §A — the pre-briefing, which is worth nothing

Everything in this section arrived in `_pre\` already measured. It is reported
because rule 1 requires it to be reported and it scores zero.

**The container.** One CHD, file version 5, `cdlz cdzl cdfl`, logical size
314,078,400, hunk size 19,584, unit size 2,448, **128,300 total units for
128,300 frames — zero padding units**, CHD size 149,661,045, ratio 47.7 %.
One track, `MODE1_RAW`, `SUBTYPE:NONE`, `PREGAP:0`, **no audio track**. The
file's own sha1 is `94a5f18422f811191a472d89e0353a387e7e8c14`.

**The size.** 128,300 / 333,000 = **38.5285 %** of a 74-minute CD, fifth of six
by size, between Slayer's 45.4474 % and Wolfenstein 3D's 17.0276 %.

**The sector map, which closes.** `file` 79,010 (61.5822 %), `copy` **43,970**
(34.2712 %), `dir` 40, `dircopy` 84, `duck` 4,896 (3.8161 %), `zero` 300,
**`other` 0**, total 128,300, double-claimed 0.

**The copies, which are the session.** `opercopies.py`: 113 groups of which
**80 are files**, 61,529 blocks read, **44,054 second-or-later copies =
90,222,592 bytes = 34.3367 %**, four groups disagree. The histogram is
286 / 24 / 13 / 13 / 18 / 2 / 10 for one to seven copies.

**The label.** `CD-ROM`, identifier `0x0E3723F0`, block size 2,048, **128,000
blocks declared = 250 MiB exactly**, root dir 1 block, **7 root copies at 85,
19675, 38475, 57690, 79779, 100363, 109741**, label length 128 bytes.

**The tree.** 366 files, 32 directories, 161,346,866 bytes, **362 distinct
sha1**, 0 unreadable — and `opera.py --list` and `hashall.py` both crash without
`PYTHONIOENCODING=utf-8`, leaving a hash list truncated at 199 records of 366.

**The extensions.** 145 with none (95,544,005 B), 12 `.aifc`, 75 `.img`, 39
`.bin`, 1 `.IMG`, 9 `.AIFF`, 4 `.anim`, 56 `.dsp`, 6 `.scp`, 3 `.TXT`, 6
`.cel`, 3 `.message`, 1 `.aiff`, 3 `.rom`, 1 `.list_no`, 1 `.list`, 1
`.script`.

**The audio.** 17:09.71 of music in 12 files, 0:57.94 of effects in 48, one
8,820-byte SDK AIFF. **The date.** `/rom_tags` type `0x0c` = `0xa9d42b59` =
**1994-04-15 11:30:33** under the 1904 epoch, second-oldest of six.

**The executables.** 36 ARM AIF images, the five header identities 36 of 36,
**the relocation exception is `ro + rw + 4` on 1 of 36**, four compressed.

**The neighbours.** `sdkdiff.py` gives **45 identical with the 1993 launch
title and 38 with each of the other four**. `crossall.py --skip` gives **56 of
362 distinct hashes**. `account3do.py` gives `bytes in files` **61.4050 %**
with three `?` buckets totalling 8.59 %.

**The refusals.** `iso9660.py` refuses with `descriptors : 0` and exits 0;
`picsdec.py`, `itdpak.py`, `sampdec.py` all refuse; `foreign.py` reports **no
file carries a foreign-architecture signature**.

## §A.0 — the films, opened before the predictions on the brief's orders

**Worth zero. No clause below scores on any of it.**

`cvidmovie.py --census` on all eight `/OrgData/stream` files. **All eight
declare compression `cvid`.** Seven chain to the last byte; **`TRDS` fails with
`bad chain at 7995388`** of its 8,683,520 bytes.

```
EDDS   260x200  declared  313   measured 2,149   3,250 mb/frame,  978 of 2,149 full
GODS   260x200  declared  131   measured   131                     131 of   131 full
MESDS  290x210  declared  525   measured   848   strips sum to 212,  0 of   848 full
OPDS   300x160  declared  767   measured 2,594                     2,594 of 2,594 full
PADDS  320x240  declared   11   measured    11                        11 of    11 full
SLDS   290x210  declared  585   measured   585   strips sum to 212,  0 of   585 full
STDS   290x210  declared  330   measured   330   strips sum to 212,  0 of   330 full
TRDS   -- does not chain --
```

**The 8,683,682-byte gap in `account3do.py`'s Data Streamer bucket is closed by
arithmetic and it is the film that does not chain**: `TRDS` is 8,683,520 bytes
and `stream.scp` is 162, and 8,683,520 + 162 = **8,683,682 exactly**.

Frames were rendered and sent to the owner. **`OPDS` is the opening titles and
credits it**; **`GODS` renders `GAME OVER`**; **`PADDS` is an eleven-frame
controller tutorial drawn over a Panasonic pad**; **`MESDS` is the prologue
narration, Japanese prose delivered as Cinepak video**; **`SLDS` is the
approach to the mansion**. The owner has answered on the editorial questions and
his answers are recorded in `docs/19`.

---

## The calibration, re-derived by summing rather than copied

The series of *predicted minus obtained* on open clauses, over fifteen objects:

```
+10.5  +7.5  +5.0  +2.0  -14.0  -2.0  +9.0  0.0  +19.75  +5.25  -4.10
-3.40  +9.30  +1.05  -2.50
```

Summed here rather than taken from the brief: **43.35**, mean **+2.8900** over
fifteen, amplitude **33.75** from -14.00 to +19.75, and **five negatives of
fifteen**. All four agree with the brief.

**No global offset is applied**, and the reason is arithmetic rather than
modesty: the last five deviations are -4.10, -3.40, +9.30, +1.05 and -2.50, so
a correction sized for the +9.30 would have made the next one worse by nine
points.

**One correction to method is applied, and it is the fifteenth object's own
lesson.** A clause that is an arithmetic identity scores 1.00 or 0.00 with
nothing in between; predicting it at 0.85 "for prudence" is not prudence, it is
a guaranteed under-prediction. **Arithmetic clauses below are predicted at 0.95
and marked `method`.**

---

## The inherited clauses — somebody else's measurement, re-tested here

**C01** `method` `inherited` — Every sector of the track passes its own
integrity checks: sync correct on 128,300 of 128,300, header MSF equal to
LBA + 150 on 128,300 of 128,300, zero EDC mismatches, zero ECC P and zero ECC Q
mismatches, and the eight reserved bytes zero on every sector. *Predicted: 0.95*

**C02** `method` `inherited` — Byte order is big-endian on every field of the
volume label and of every directory record, and `block_size` reads 2048
big-endian. *Predicted: 0.95*

**C03** `content` `inherited` — The volume label record is **132 bytes** with
the word at +128 zero, while `opera.py --label` correctly prints 128 because
`last_root_copy` is 6. Two fields, two definitions, four bytes apart, both
right — and this disc does not get a prediction spent on the difference.
*Predicted: 0.95*

**C04** `content` `inherited` — `/rom_tags` type `0x0c` reads
**1994-04-15 11:30:33** under the 1 January 1904 epoch, is identical in both
copies, and is the second-oldest of six. It is cited from the platform notes
and not re-derived. *Predicted: 0.95*

**C05** `method` `inherited` — `/rom_tags` type `0x02` addresses `/launchme` by
block, and field A and field B equal the boot binary's own directory entry
exactly. *Predicted: 0.92*

**C06** `content` `inherited` — `/signatures` is **335,872 bytes**, the sixth
disc of six to the byte, and its contents differ from all five others.
*Predicted: 0.95*

**C07** `content` `inherited` — Sixty-four bytes of high-entropy data sit at
offset **+224 of the `/rom_tags` block**, wholly different between the two
copies, and the `+8` word of records `0x0d`, `0x07` and any `0x10`/`0x05` is
patched between copy 0 and copy 1 while `0x0c` and `0x02` are left alone.
*Predicted: 0.85*

**C08** `method` `inherited` — On the 36 AIF images: `SWI &11` at 0x10, entry
point 0x100 from the `BL` at 0x0C, flags at 0x30 equal 32, image base 0 and
debug size 0, all on 36 of 36. *Predicted: 0.95*

**C09** `method` `inherited` — Sixteen-bit pixels are 5-5-5 with the top bit
unused: over the pixels of any full-screen sixteen-bit image on this disc the
top bit is set **zero** times. *Predicted: 0.88*

**C10** `method` `inherited` — The platform's chunk rule holds: four printable
characters, a big-endian `u32` length **including the eight-byte header**, and
chunks tiling their container to its last byte. *Predicted: 0.90*

**C11** `content` `inherited` — No studio asserts copyright in text anywhere on
this disc, and the studio's name is a picture rather than a string. `Riverhill`
counts 0 in `/launchme` already; the prediction is that it counts 0 over the
whole pressing and that the name is rendered in the films or the `IMAG` files.
*Predicted: 0.80*

**C12** `content` `inherited` — `burst` is 1 and `gap` is 0 on every directory
entry of this disc, including on the eight Data Streamer files — which is
precisely the case that should exercise an interleave parameter and, on three
SDKs already, has not. *Predicted: 0.90*

**C13** `content` `inherited` — The directory copies disagree in the two known
ways and only those: a case bit in directory groups with copy 0 holding the
upper case, and the signing pass in `/rom_tags`. *Predicted: 0.80*

---

## The open clauses — this session's own work

### The copies, which are the object's question

**C14** `method` `open` — The copies of a **file** can be hashed per copy from
the directory record's copy list, and a tool to do it is under sixty lines.
*Predicted: 0.85*

**C15** `content` `open` — The copies of a file are **byte-identical to each
other** on at least 76 of the 80 file groups. The four disagreeing groups
`opercopies.py` already reports are directory groups or `/rom_tags`, not game
data. *Predicted: 0.70*

**C16** `content` `open` — The copies of a multi-copy file are **spread across
the pressing rather than clustered**: for the ten seven-copy files the mean gap
between consecutive copy addresses exceeds 5,000 blocks, matching the root's own
1+1+1+1+1+1+1 layout. *Predicted: 0.65*

**C17** `content` `open` — The number of copies of a file **tracks the root
copy count**: a file with *n* copies has them distributed so that each falls in
a different one of the seven bands the root copies delimit, and no band holds
two copies of one file. *Predicted: 0.40*

**C18** `method` `open` — Without the duplication the pressing would be
128,300 − 43,970 = **84,330 sectors = 25.3243 %** of a 74-minute CD, which
would make it the smallest disc of six but one. *Predicted: 0.95*

**C19** `content` `open` — The duplication is **not correlated with file size**:
the ten seven-copy files span three orders of magnitude (616 bytes to 3,097,280)
and the two six-copy files are among the largest, so size does not order the
histogram. *Predicted: 0.75*

**C20** `content` `open` — The seven-copy set is a **room working set**: the ten
files cover music, room geometry, an interface image and a cursor, and the set
is what one room needs at once rather than what the whole game needs. It will be
demonstrable that they are not simply the ten most-used files. *Predicted: 0.45*

**C21** `content` `open` — This disc is the CD-i result on a 3DO and the reason
is the drive: the duplication buys **seek distance**, and the arithmetic of a
single-speed drive's 153,600 bytes per second against the pressing's length will
support that reading rather than a "scratch insurance" one. *Predicted: 0.40*

### The films

**C22** `content` `open` — `TRDS`'s bytes past 7,995,388 are **not a broken
chunk chain but a tail**: the residue is padding, zero, or a second object, and
the chain up to 7,995,388 is clean. *Predicted: 0.55*

**C23** `content` `open` — The three films that declare 290 × 210 are really
**212 pixels tall**, and 212 is 53 macroblocks of four while 210 is not a
multiple of four — so the `FHDR` height is the display height and the strips
carry the coded height. *Predicted: 0.65*

**C24** `content` `open` — The films carry `SNDS` sound chunks, and the sound
inside the eight films totals **more than 15,000,000 bytes**, which is the
number the thesis column needs and which `thesis3do.py` cannot see.
*Predicted: 0.55*

**C25** `content` `open` — Every film's `SHDR` declares its stream block size as
**20,480 bytes**, and at least six of the eight are a whole number of those
blocks with remainder zero. *Predicted: 0.60*

**C26** `content` `open` — The eight films account for **more than 99 %** of
`/OrgData/stream`'s 93,585,570 bytes once decoded, closing the largest single
unnamed region on the disc. *Predicted: 0.70*

### `IMAG`, which four discs of five did not have

**C27** `method` `open` — On the 76 `IMAG` files the geometry arithmetic closes:
`28 + 8 + bytes_per_row × height` equals the file size on at least 70 of 76.
*Predicted: 0.65*

**C28** `content` `open` — The `pixel order` field **lies on this disc too**: it
disagrees with the order the vertical-against-horizontal roughness test picks on
at least one file of 76, which is the first test of that trap since the first
disc. *Predicted: 0.50*

**C29** `content` `open` — The roughness test picks **linear** on at least 70 of
the 76, because these are images the CEL engine draws rather than buffers the
ROM blits. *Predicted: 0.60*

**C30** `content` `open` — All the `IMAG` headers are **big-endian**, with width
and height reading as sane small numbers big-endian and as absurd ones
little-endian. *Predicted: 0.90*

**C31** `content` `open` — The disc uses three graphics containers at once —
76 `IMAG`, 6 `CCB `, 4 `ANIM` — and **no fourth**: no `BRGR`, no headerless
raster, no `.pics` equivalent, and `celdecode.py` plus `ccbread.py` will
account for every cel-bearing file. *Predicted: 0.55*

### The clone question, as a table

**C32** `content` `open` — `room*.bin`'s leading word is **big-endian**, and the
same test on the `IMAG` headers agrees, so on the byte-order axis this disc is
native to the console and not a port of a little-endian layout. *Predicted: 0.85*

**C33** `content` `open` — The clone table closes on **four or fewer of its
seven axes**, and the axes that close point away from a port: the containers are
the platform's, the byte order is the console's, and the script is plain text
where Alone in the Dark's was compressed inside an archive. *Predicted: 0.50*

**C34** `content` `open` — `/OrgData/item` (2 files, 2 records' worth of bytes)
is **not** an object table in the shape of `OBJETS.ITD`: no 52-byte record
stride, no 292 records, and the object data is somewhere else entirely.
*Predicted: 0.60*

**C35** `content` `open` — The 33 `room*.bin` are **not** eight floor archives:
the count is 33 against Alone in the Dark's 8 `ETAGE`, and the naming
`roomNNN` with the script's `(FnRmmm)` headers says the unit of this game is a
room where the unit of the other is a floor. *Predicted: 0.70*

### The script, and the person named in it

**C36** `method` `open` — The text is **Shift-JIS**, demonstrated by lead-byte
ranges rather than by the disc being Japanese: two-byte sequences with a lead in
0x81–0x9F or 0xE0–0xEF and a trail in 0x40–0xFC account for more than 90 % of
the non-ASCII bytes in `/OrgData/mes/`. *Predicted: 0.80*

**C37** `content` `open` — `MESSAGE1.TXT` and `MES by HAYASHI/floor001.message`
are **not byte-identical** but hold the same messages: the room headers match
and the difference is in the line prefixes and the indentation, so one is a
production form of the other. *Predicted: 0.60*

**C38** `content` `open` — The room ids in the message files are **floor-and-room
keys that cross-reference the 33 `room*.bin`**, and the number of distinct ids
in `/OrgData/mes/` is within five of 33. *Predicted: 0.45*

**C39** `content` `open` — `HAYASHI` is **named by the shipped game itself**, so
the directory name publishes no identity the product does not — the same
structure the platform notes recorded for the fifth disc's build-machine
leftovers. *Predicted: 0.80*

**C40** `method` `open` — `unowned.py --contacts` counts **zero** reachable
contact details — no postal address, no telephone or fax number, no mail
address — over the whole tree, and the count is reported as a count and never as
a value. *Predicted: 0.80*

### The executables and the SDK

**C41** `content` `open` — `/System/Kernel/os_code` is **79,692 bytes**,
matching `/rom_tags` record `0x07` field B exactly, and it is a **fifth distinct
value** after 78,852 / 85,896 / 85,896 / 115,520. *Predicted: 0.88*

**C42** `content` `open` — The single `ro + rw + 4` relocation exception is
**the title's own binary and not an SDK image**, continuing the platform notes'
open question 11 to a third point and its third confirmation. *Predicted: 0.60*

**C43** `content` `open` — The `/System` tree's upper-case names in copy 0 are
the same case-folding behaviour the notes record and **not an older naming
convention**: the later copies write lower case and copy 0 writes upper, exactly
as on five discs. *Predicted: 0.70*

**C44** `content` `open` — The instrument bank's **56** `.dsp` files sit between
the launch title's 53 and the 1994-95 group's 63 and are all `FORM 3INS`, giving
a **sixth point on a monotone series** ordered by pressing date with no
inversion. *Predicted: 0.85*

### User state, accounting, and the collection

**C45** `content` `open` — **No file on this disc is user state.** The save goes
to the console's NVRAM, and a literal `/nvram`-rooted path exists in `/launchme`
as it did on the fifth disc. *Predicted: 0.65*

**C46** `method` `open` — `bytes in files` is 161,346,866 of a 262,758,400-byte
user area = **61.4050 %**, and the 90,222,592 bytes of second copies are stated
explicitly as **inside the user area and outside `bytes in files`** in every
fraction this repository publishes. *Predicted: 0.95*

**C47** `content` `open` — Once the films are decoded, `account3do.py`'s
`UNKNOWN: no format derived` bucket falls **below 4 %** of the user area from
its present 8.0750 %. *Predicted: 0.55*

**C48** `content` `open` — The 21,217,750 unnamed bytes are **mostly
`/OrgData/isearch` and `/OrgData/room`**: those two directories are 7,528,252 +
7,955,696 = 15,483,948 bytes, which is **72.98 %** of the unnamed total.
*Predicted: 0.70*

**C49** `content` `open` — The recorded-sound figure for the thesis column, on
the denominator **all recorded sound over the user area**, lands between
**25 % and 35 %** — above the AIFF-only 17.5324 % because the films carry
sound, and below every neighbour but Crash 'n Burn. *Predicted: 0.50*

**C50** `content` `open` — Of the 56 crossing hashes, **at least 45 are under
`/System`**, because a 102-file `/System` on a 366-file disc is what makes this
disc's 15.5 % crossing rate low where the fifth disc's was 50.2 %.
*Predicted: 0.70*

**C51** `content` `open` — Of the eleven abbreviations the brief lists —
`OrgData`, `isearch`, `EDDS`, `OPDS`, `MESDS`, `TRDS`, `SLDS`, `STDS`, `PADDS`,
`GODS`, `HAUZER`, `HAYASHI` — **at least six are demonstrable from the object
itself** and the rest are named as undemonstrated rather than guessed.
*Predicted: 0.60*

**C52** `content` `open` — `crossall.py`'s empty-file hash trap fires here as
it did before: the sha1 of the empty file appears in the collection and is
reported separately, and this disc's own contribution to it is **zero**, because
this disc has **no zero-length files** — the third confirmation of that rule.
*Predicted: 0.65*

**C53** `content` `open` — The mastering-fill arithmetic can be run on this
disc, which the fifth could not exercise: the three-term sum of round-up slack,
index blocks and the zero tail closes against the gap between how full the disc
is and its 3.8161 % fill **to under two sectors**. *Predicted: 0.45*

**C54** `content` `open` — `/OrgData/isearch`'s 49 files are **one format
repeated**, not 49 unrelated things: they share a leading structure, and the
directory's name expands from the object rather than from a guess.
*Predicted: 0.40*

---

## What this document does not predict

**The pixel order of the `IMAG` files is not predicted as a value**, only as a
disagreement (C28) and a measured winner (C29), because the platform notes are
explicit that the field lies on the one disc that has ever been able to test it
and that the answer is settled by rendering and looking.

**The meaning of the 34 % is not predicted as a mechanism.** C21 predicts which
of two readings the arithmetic will support and is deliberately scored on the
arithmetic rather than on the story. If neither reading is supported the clause
takes 0.00 and the chapter says so.

**Nothing about the 1992 MS-DOS original is predicted**, because it is not here.
The comparison runs against the 3DO port in `3do-aloneinthedark-doc`, which is a
partial proxy, and every row of the table says which object it measured.

---

## The counts, written from the command's output

The clause count and both totals below are `predcount.py`'s, pasted after it
ran and not typed before it:

```
python tools/predcount.py docs/00-predictions.md
```

```
clauses      : 54          method : 12    content : 42
inherited    : 13 clauses, predicted total 11.75
open         : 41 clauses, predicted total 26.68
cross-tab    : inherited method 6, inherited content 7,
               open method 6, open content 35
```

**And it caught this document too, which is the sixth session in a row.** The
paragraph above was first typed as **11.80** and **26.65**, both summed by eye,
and both wrong. The figures now standing are the command's. **The header is
written from the output; the output is not checked against the header.**

`predcount.py` also prints a warning this document has earned: **35 of the 41
open clauses are `content`, which is 85.4 %**, and content clauses on a
container nobody has opened score about 68 %. That is noted and not corrected —
the shape of this object is that almost everything unknown about it is a fact
about contents rather than a method.

**The two totals are never summed.** `inherited` re-tests somebody else's
measurement and `open` is this session's own work; a single number made of both
means nothing.

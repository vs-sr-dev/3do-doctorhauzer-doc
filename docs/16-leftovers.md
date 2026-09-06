# 16 — leftovers: what this session did not close, with how much of it there is

*Measure: 755,956 bytes in files whose format was not derived, 0.4685 % of what
is in files; plus 1,000,592 bytes inside files whose format partly was; plus
three rooms nothing names.*

Rule: a thing goes here when it was **looked at** and did not close, with the
quantity attached. Nothing is here because nobody opened it.

## The room sections that are not derived — 1,000,592 bytes

Every `room*.bin` is a three-word big-endian offset table over four sections, on
33 of 33, and the four sections plus 33 × 12 bytes of header sum to the
directory's 7,955,696 bytes exactly. **Sections 1 and 2 hold 1,066 cels and are
derived. Sections 0 and 3 hold no cel structure and are not.**

```
section 0    797,148 B   10.02 % of the room bytes   0 cels
section 3    203,444 B    2.56 %                     0 cels
             ---------
             1,000,592 B  = 0.3808 % of the user area
```

Section 0 is the same size as section 2 to within 528 bytes aggregated over 33
files, which is the shape of two tables of equal length — one of them the cel
directory for section 1 and the other something parallel. **That is a guess and
it is written as one.** What would close it: a record stride in section 0 that
divides its per-file length and yields a count matching the cels in section 1.

## The four polygon-and-texture files — 322,156 bytes

```
/OrgData/human/HumanPol.bin   188,976 B    48 cels inside
/OrgData/human/HumanTex.bin    63,452
/OrgData/item/ItemPol.bin      23,324      33 cels inside
/OrgData/item/ItemTex.bin      46,404
```

The naming is exactly parallel — `Pol` and `Tex`, actors and items — and the
cels inside them are derived. **The record structure is not**, and that is what
keeps two rows out of chapter 12's clone table. What would close it: a stride
that divides 188,976 and produces a plausible number of actors.

## `/OrgData/macro/` — 39 files, 221,968 bytes

Named `macro001`..`macro012`, `macro201`..`macro216` (with **no `macro214`**),
`macro301`..`macro305`, `macro313`, `macro400`, `macroDemo1`..`3`, `macroEnd`
and `macroXXX`. The numbering shadows the rooms: `macro004` and `room004.bin`
are pressed as one bundle five times (chapter 04). **`macro400` and `macroEnd`
are byte-identical**, which is one of the disc's only two duplicate-content
pairs.

**`macroXXX` is 112 bytes of near-empty binary** and is the literal template
filename `/launchme` completes at run time — the placeholder pressed onto a
retail CD.

Not derived: what a macro is. It is plausibly a room's event script, because the
numbering follows the rooms and the bundles pair them. **Plausibly is not a
measurement.**

## Three rooms nothing names — 369,332 bytes

```
room214.bin    37,648 B     3 cels
room215.bin   256,516 B    26 cels
room216.bin    75,168 B     9 cels
```

`room214`, `room215` and `room216` each occur **exactly three times over the
whole 301,761,600-byte pressing**, which is the number of copies of their own
directory, and nowhere else. `ROOM214`/`215`/`216` in upper case count zero.
Neither `/OrgData/start.script` nor any message file names them. `room216.bin`
is nonetheless pressed **four times**.

**Not decided: whether this is cut content, a debug set, or three rooms reached
by an index this session did not find.** `/OrgData/macro/` has no `macro214`
either, which is consistent with all three readings.

## `$boot/OrgData/menu/game.anim` — one string, zero bytes

Named once in `/launchme`, and the file does not exist. Its four siblings —
`continue.anim`, `opening.anim`, `operation.anim`, `start.anim` — all resolve
exactly. **The first named-and-absent asset this collection has found on a 3DO
disc**, and one string is not a story.

## `/OrgData/font/fontNew.bin` — 36,363 bytes

The Shift-JIS font the in-game message system draws with. Not opened. What would
close it: a glyph stride and a character-code table, and the disc's own script
files are the test set.

## `/signatures` — 335,872 bytes

Sixth disc, sixth time, to the byte, and different in content on six of six.
**The algorithm is unnamed on this platform** and this session did not advance
it beyond confirming the size, the fixed +224 offset of the 512 bits in the
`/rom_tags` block, and the `0x05` off-by-one to `/signatures`' first block.

## The 36 ARM binaries

Excluded by the pipeline's rule against disassembly, and named so that the
exclusion is visible rather than silent. `/launchme` is 246,232 bytes and its
string tables past the 131 path-shaped strings were not read.

## The two decisions, and both were taken

The brief asked that a decision this session could not take be written out as
*this session did not know how to decide, and here is what it would need*. **Both
were taken and neither needs that paragraph:**

- **what the 34 % of copies means** — chapter 04. The unit of duplication is a
  contiguous run of files across directories, 24 runs pressed 67 times, measured
  from the addresses. What is *not* claimed is the drive's behaviour: the
  seek-distance arithmetic is published as arithmetic and the disc's designers'
  reasoning is not asserted;
- **the clone question** — chapter 12. Five axes close, two do not, and on the
  owner's own instruction the two that do not are omitted from the table and
  named beneath it.

## What was NOT run, and it should be said

`rezcel.py` was not run: it is for headless cels and every cel on this disc has
a `CCB ` header, so its subject does not exist here. `slackchain.py` was not
run: this disc has zero unowned sectors and its subject does not exist here
either — though its method, *is this region one object or a heap*, is what the
bundle analysis in chapter 04 does to the copies. `chdhdr.py` and `isodev.py`
were not run and would have added nothing `chdman info` and `iso9660.py --vd`
did not.

**And five tools written for the fifth disc were pointed at this one and all
five refused, correctly**: `picsdec.py` (no `.pics`), `itdpak.py` (no `.PAK`),
`sampdec.py` (no `.samp`), `l10ncmp.py` (no language pairs) and `aiffwav.py`
(not needed). `foreign.py` reports **no file carries a foreign-architecture
signature**, which is a clean negative control on a second disc and is published
as one.

# 04 — the copies: a third of the disc is itself, and the unit is not the file

*Measure: 80 files declare more than one copy; 43,970 sectors — 90,050,560
bytes, 34.2712 % of a 128,300-sector pressing — are second or later copies of
file content; 79 of the 80 groups are byte-identical across every copy; and
twenty-four contiguous runs of files are pressed sixty-seven times between
them.*

Five 3DO discs of five had exactly **two** files with a second copy —
`/Disc label` and `/rom_tags`, the two the console reads before there is a file
system to read them with. The platform notes wrote that up as a rule with a
contrast built into it:

> **The redundancy is in the index, not in the data.** That is the opposite of
> the CD-i result and a difference in kind: CD-i discs duplicated *content* to
> keep a single-speed drive near its working set, and Opera duplicates
> *metadata* so that a scratch cannot cost the volume. — `[2 of 2]`

**This disc is the CD-i result on a 3DO**, and this chapter is what the
measurement says beyond that sentence.

## What the file system declares

```
python tools/opercopies.py _work/hauzer.bin
python tools/filecopies.py _work/hauzer.bin --list
```

```
files in the volume                     366
files declaring more than one copy        80
groups whose copies are byte-identical    79 of 80
groups whose copies DIFFER                 1 of 80   -- /rom_tags
second-or-later copies, in blocks     43,970
                            in bytes  90,050,560     = 34.2712 % of the pressing
```

**The histogram goes to seven and it is not a flat doubling:**

```
1 copy   286 files      2 copies  24      3 copies  13      4 copies  13
5 copies  18            6 copies   2      7 copies  10
```

### The reconciliation, because two tools give two numbers and both are right

`opercopies.py` reports **44,054** blocks and `filecopies.py` reports
**43,970**. The difference is 84 and it is the directory copies:

```
file second copies (filecopies.py)      43,970
directory copies   (sectormap3do.py)        84
                                        ------
                                        44,054   = opercopies.py exactly
```

**The session brief and the pre-briefing both quote 90,222,592 bytes and
34.3367 % as "second copies of files".** They are not: 172,032 of those bytes
are directory blocks. The figure for duplicated **file content** is
**90,050,560 bytes = 34.2712 %**, and it is the `copy` bucket of the sector
map to the sector. Corrected in chapter 17.

## Question one — are the copies identical?

**Nobody had ever asked.** `opercopies.py` compares directory *blocks*; a
file's copies are its own bytes, and on five discs there were only two files to
compare. `filecopies.py` reads each copy as `block_count` blocks from that
copy's declared address and truncates to `byte_count` — exactly how
`opera.py` reads copy 0 — so a difference is a difference in the pressed bytes.

**79 of 80 groups are byte-identical across every copy**, including all ten
seven-copy groups and both six-copy groups.

**The one that differs is `/rom_tags`**, and it differs for the reason the
platform notes already derived: the signing pass. Copy 0 at block 1 carries the
type-specific `+8` words as small integers; copy 1 at block 226 carries them
patched.

```
                     copy 0        copy 1
rec 0 (type 0d)      00000001      ffffff20
rec 1 (type 07)      00000005      ffffff24
rec 4 (type 10)      00000045      ffffff64
rec 5 (type 05)      0001ecb6      0001ebd5
```

**So the duplication is not a versioning artefact and it is not a build
accident.** Eighty files, up to seven copies each, ninety megabytes, and every
byte of every copy agrees. Whatever put them there did it in one pass from one
source.

## Question two — where are the copies?

The addresses are in the directory record, so this is a field read.

```
gaps between consecutive copies of one file, over 231 gaps
  min 12   median 4,060   max 118,890   mean 15,970.4
```

**The root's own seven copies are at 85, 19675, 38475, 57690, 79779, 100363 and
109741** — spread almost evenly across the pressing, where five discs of five
clustered them. Taking those seven as the edges of seven bands:

```
band 0  blocks     85 ..  19674     38 copies
band 1  blocks  19675 ..  38474     28 copies
band 2  blocks  38475 ..  57689     93 copies
band 3  blocks  57690 ..  79778     34 copies
band 4  blocks  79779 .. 100362     24 copies
band 5  blocks 100363 .. 109740      7 copies
band 6  blocks 109741 .. 128299     87 copies
```

**And the prediction this session wrote about that was wrong.** Clause C17
predicted that a file with *n* copies would place them one per band, with no
band holding two copies of one file. It is **17 of 80 one per band and 63 of 80
with a collision**. The bands are not the structure.

## Question three — and this is the answer: the unit of duplication is a RUN

```
python tools/filecopies.py _work/hauzer.bin --bundles
```

Take every copy of every file — 597 placements — sort them by block address,
and join any two that are within four blocks of each other. That gives **192
contiguous runs** with **149 distinct contents**, and then:

```
run contents that occur once             125
run contents that occur more than once    24
the repeated runs hold 47 distinct files and are pressed 67 times
```

**The repeated runs cross directories.** The clearest one:

```
pressed 4 times, 6 files, 105 blocks each, at 41421, 43838, 48091, 64339
    /OrgData/etc/NowLoading.cel
    /OrgData/etc/colcel.cel
    /OrgData/human/HumanPol.bin
    /OrgData/images/image.scp
    /OrgData/mes/mes.scp
    /OrgData/stream/stream.scp
```

Six files from **five different directories**, laid down end to end, and the
whole run pressed four times at four widely separated addresses. And it is
visible in the raw copy lists without any clustering at all — two files that
travel together keep their offset exactly:

```
/OrgData/window/pen.cel      5734, 7432, 57948, 84212, 84236, 119708, 120227
/OrgData/window/cursor.cel   5737, 7435, 57951, 84215, 84239, 119711, 120230
                              +3    +3     +3     +3     +3      +3      +3

/System/Audio/dsp/dcsqxdhalfstereo.dsp  38938, 46527, 84725, 84737, 84759, ...
/System/Audio/dsp/mixer2x2.dsp          38939, 46528, 84726, 84738, 84760, ...
                                          +1     +1     +1     +1     +1
```

**So the duplication is not per-file at all.** The mastering laid down a
*bundle* — a contiguous run of the files some part of the game needs together —
and pressed the whole bundle again wherever it wanted another copy near. The
file's copy count is just how many times its bundle was written.

**That is the CD-i result in its exact form**, and it is worth being precise
about which half of the CD-i finding transfers. The platform notes' contrast
says CD-i discs *duplicated content to keep a single-speed drive near its
working set*. The **content duplication** is measured here. The **working set**
is measured here too, because the bundles cross directories and hold exactly
the kinds of file a scene needs at once. What is **not** measured here is the
drive's behaviour, and this repository does not claim it.

## Question four — what does the seven-copy set correspond to?

The pre-briefing listed four seven-copy files and drew a conclusion from them:
a music track, a room, an interface image, a cursor — *what a room needs at
once*. **There are ten, and the list was filtered.**

```
/OrgData/music/music003.aifc            3,097,280 B
/OrgData/room/room004.bin                 275,656
/OrgData/window/cmd01.img                 153,724
/OrgData/window/note.img                  153,724
/OrgData/window/pen.cel                     4,276
/OrgData/window/cursor.cel                    616
/System/Audio/dsp/dcsqxdhalfstereo.dsp      1,220
/System/Audio/dsp/mixer2x2.dsp                724
/System/Audio/dsp/envelope.dsp                682
/System/Audio/dsp/sampler.dsp                 566
```

**Four of the ten are `/System/Audio/dsp` instrument patches**, which are the
SDK's and not this game's — they are byte-identical with files on five other
3DO discs. The story survives in a better form: the seven-copy set is what the
**audio and interface layer** needs resident, and it includes the audio
folio's own instruments because the folio loads them from the disc.

**Size does not order the histogram.** The ten span 616 bytes to 3,097,280 —
three orders of magnitude — and the two six-copy files are among the largest on
the disc. Clause C19 predicted that and it holds.

## What it cost, and what the disc would have been without it

```
the pressing                        128,300 sectors   38.5285 % of a 74-min CD
second copies of files              -43,970
                                    --------
without them                         84,330 sectors   25.3243 % of a 74-min CD
```

**A quarter of a CD instead of two fifths.** The disc would have been the
second-smallest of the six, between Wolfenstein 3D's 17.0276 % and Slayer's
45.4474 %, and it would still have held every distinct byte it holds now.

And the drive arithmetic, which is the only part of the *why* that can be
computed from this object: a single-speed drive delivers **153,600 bytes per
second**, and the pressing is 128,300 sectors. A worst-case seek across the
whole disc is a seek across 128,300 sectors; with a bundle pressed seven times
at roughly even spacing, the worst-case seek to reach that bundle falls to
about 128,300 / 7 = **18,329 sectors**, a seventh of the distance. **That is
the shape of the trade and it is what the addresses show.** Whether the drive's
actual seek profile made it worth ninety megabytes is not measurable from a
disc image, and this repository does not say it was.

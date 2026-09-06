# 07 — 1,157 cels, 33 rooms, and the cel depth no disc had used

*Measure: 1,157 `CCB ` structures on which both independent encodings of width
and height agree, 1,157 of 1,157; 729 of them at eight bits per pixel; 33 room
files opening with a three-word big-endian offset table, 33 of 33; and
7,955,300 bytes of room sections plus 33 × 12 bytes of header = 7,955,696, the
directory's own total to the byte.*

## Count cels, not files

The platform notes' rule, from the second disc: *a 3DO disc's image count is
meaningless — count cels.* Censusing by signature over the whole tree, and
requiring the notes' own structural identity before counting anything:

```
width  == PRE1 bits 0..9  + 1  == word 16     1,157 of 1,157
height == PRE0 bits 6..15 + 1  == word 17     1,157 of 1,157
```

**Two independent encodings of one quantity agreeing on every occurrence**, on a
sixth disc. That is the check the notes call stronger than arithmetic, because a
wrong field assignment cannot satisfy it, and it is what licenses every number
below.

```
cels found            : 1,157
depths                : 1 bpp x1     8 bpp x729     16 bpp x427
packed (flag bit 9)   : 231 of 1,157
coded (PLUT ptr set)  : 0 of 1,157

by directory:
  /OrgData/room   1,066      /OrgData/human    48      /OrgData/item    33
  /OrgData/etc        4      /OrgData/menu      4      /OrgData/window   2
```

## Eight bits per pixel, which closes an open question

The platform notes have carried this since the second disc and it survived
three more:

> **8 bits per pixel** — the one cel depth no disc has used.

**This disc uses it on 729 cels of 1,157**, which is not a curiosity but the
dominant depth on the object. The six standalone `.cel` files confirm it
individually, and all six decode:

```
python tools/celdecode.py _work/files/OrgData/etc/NowLoading.cel _work/cels --all
```

```
3DOlogo.cel       77 x 155    8 bpp   unpacked   1 of 1 decoded
NowLoading.cel   200 x  21    8 bpp   unpacked   1 of 1 decoded
pen.cel           64 x  64    8 bpp   unpacked   1 of 1 decoded
bg.cel            16 x  16   16 bpp   unpacked   1 of 1 decoded
cursor.cel        16 x  16   16 bpp   unpacked   1 of 1 decoded
colcel.cel         1 x   1   16 bpp   unpacked   1 of 1 decoded
```

**Open question 4 in the platform notes is now answered on every depth the
platform defines.** The second disc supplied 1, 2, 4 and 6 bits per pixel and 3
cels at 16; three discs have supplied 16 in quantity; and **8 arrives here, on
729 cels**. Six depths, six discs, and the list is complete — which means the
question can be closed rather than narrowed, for the first time since it was
written.

**`coded` is zero on 1,157 of 1,157**, which is the surprise inside the
surprise. Every cel on the second disc carried a `PLUT` pointer; not one here
does. On an eight-bit cel a palette is not optional, so the palette is supplied
by whatever draws the cel rather than stored with it — the same division of
labour the notes describe for the pixel order, arriving in a second field.

## The third graphics container, and the disc that has all three

```
python tools/animwalk.py census _work/files
```

```
containers                     : 10       chunks : 49, tiling 127,668 bytes
distinct shapes                : 3
   4  ANIM CCB  XTRA PDAT PDAT PDAT PDAT
   3  CCB  PLUT XTRA PDAT
   3  CCB  XTRA PDAT
ANIM word 2 == the number of PDAT chunks : 4 of 4
ANIM chunk lengths                       : 0x20 on 4 of 4
```

**So this disc uses `IMAG`, bare `CCB ` and `ANIM` at once**, where the first
disc used `IMAG`, the second bare `CCB `, the third a `BRGR` archive, the fourth
`ANIM` and the fifth none of them. Six discs, and the first that does not pick
one.

The fourth disc's single `ANIM` identity — word 2 equals the `PDAT` count —
holds on 4 of 4 here, so it is now measured on two discs.

**And `BRGR` is absent, which took reading the context rather than the
arithmetic.** `BRGR` counts **4** over the 301,761,600-byte track against a
chance expectation of **0.0703**, which by the ratio is a fifty-seven-fold
signal and by the Poisson tail is overwhelming. It is noise anyway: three of the
four are inside Cinepak codebook payloads in `OPDS` and `SLDS` and one is inside
`room202.bin`'s cel data, and none of them is followed by a member count or
anything else an archive header has. **The chance expectation said signal and
the context said noise** — the exact inverse of the notes' `[1 of 2]` about
counting one occurrence against a fractional expectation, and the same
conclusion: the arithmetic is necessary and it is not sufficient.

## How this disc stores a room

The platform notes' open question 14 asks how a 3DO disc stores a room, with
the fifth disc's answer — a forty-sector block the game seeks to — as its only
point. **This is a second answer and it is a different one.**

```
python tools/ccbread.py census _work/files
```

Every one of the 33 `room*.bin` opens with a big-endian word that is a small
number inside the file, and the words after it continue ascending:

```
room001.bin  179,844 B   words:  12,896   161,340   174,240
room002.bin  296,864 B   words:  21,160   268,752   289,916
room305.bin  164,104 B   words:   8,284   151,524   159,812
```

**A strictly ascending offset table that ends at or before the first offset, on
33 of 33.** Three words, twelve bytes, four sections. Read little-endian the
first word of `room001.bin` is 1,613,889,536, which is nine times the file, so
the byte order is not in doubt.

The sections, aggregated over all 33 rooms:

```
section 0    797,148 B   10.02 %   CCB chunks      0
section 1  6,157,032 B   77.40 %   CCB chunks    882
section 2    797,676 B   10.03 %   CCB chunks    184
section 3    203,444 B    2.56 %   CCB chunks      0
           ---------
           7,955,300  + 33 x 12 bytes of header = 7,955,696
```

**7,955,696 is the directory's own byte total for `/OrgData/room`**, so the
four sections and the header account for every byte of every room.

Sections 1 and 2 hold the cels — 1,066 of them, the room's own textures and
sprites. Sections 0 and 3 hold no cel structure at all: section 0 is 10.02 % of the
room bytes and section 3 is 2.56 %, and section 0's aggregate size differs from
section 2's by 528 bytes over 33 files, which is the shape of two tables of the
same length. **Neither is derived and both are counted as unknown**; see
chapter 16.

`ccbread.py census` reports 36 files whose chunk chain does not close, and
**every one of the 33 rooms is among them, correctly** — a room is not a chunk
file, it is an offset table with chunk-bearing sections inside it, and a walker
that starts at byte 0 is right to refuse. That refusal is the measurement.

## What this says next to the fifth disc

```
                        Alone in the Dark (3DO)     Doctor Hauzer
the unit                a floor                     a room
how many                8 ETAGE .PAK archives       33 room*.bin
what is inside          nothing of the platform's   1,066 platform cels
the geometry            a 40-sector block, seeked   a 3-word offset table
the byte order          little-endian, the PC's     big-endian, the console's
```

Two discs, two answers, and they are not variations of one idea. Chapter 12
takes that into the clone question.

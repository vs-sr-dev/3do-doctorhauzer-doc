# 10 — strings: 131 paths, 107 of 366 files named, and one file that is not there

*Measure: every count below carries its chance expectation on its own
denominator; the pressing is 301,761,600 bytes and the file tree is
161,346,866; and 131 path-shaped strings in `/launchme` resolve 105 exactly, 2
case-folded and 24 not at all, with every miss examined individually.*

## Counts, with the expectation printed beside them

The denominator is the **pressing**, because filenames live in directory blocks
and a file-tree search cannot see them. On 301,761,600 bytes a four-byte string
is expected **0.0703** times and a three-byte string **17.9864**.

```
string           count   expected      string        count   expected
Riverhill            0     0.0000      Copyright        28     0.0000
RIVERHILL            0     0.0000      COPYRIGHT         0     0.0000
riverhill            0     0.0000      copyright         0     0.0000
HAUZER               7     0.0000      (C)               4    17.9864
Hauzer               2     0.0000      1994              3     0.0703
hauzer               0     0.0000      @(#)              1     0.0703
HAYASHI              3     0.0000      $Id:              0     0.0703
Matsushita           0     0.0000      APPSCRN           0     0.0000
armlink              0     0.0000      M.K.              0     0.0703
Norcroft             0     0.0000      BRGR              4     0.0703
armcc                0     0.0003      cvid             19     0.0703
armasm               0     0.0000      CVID              0     0.0703
nvram               16     0.0003      Cinepak           0     0.0000
NVRAM               11     0.0003      SDX2             44     0.0703
```

## `Copyright` counts 28 and it is not a copyright

Five discs gave 2, 2, 2, 2 and 3. **Twenty-eight would be a finding if it were
read as a count.** Reading the context instead — thirteen occurrences inside
files, the rest their pressed copies:

```
/System/Folios/OPERAMATH     Copyright 1993 The 3DO Company. All Rights Reserved.
/System/Kernel/boot_code     Copyright 1993 The 3DO Company, All rights reserved.
eleven .img files            ...CPYR....No Copyright....KWRD....No KeyWord...
```

**Eleven of the thirteen are the word used as a FIELD LABEL whose value is
"No Copyright"** — the SDK image tool's placeholder metadata block (chapter 06).
So the real count is **two**, they are both the platform's and not the studio's,
and they are the same two files as on the first and second discs.

**The platform notes' rule survives on a sixth disc, and this disc proves it the
hard way**: `Riverhill` counts zero in all three cases over 301,761,600 bytes,
and the studio's copyright assertion is **painted in pixels** on
`/OrgData/images/CopyRight.img` — `©1994 Riverhill Soft Inc.` and
`©1994 Matsushita Electric Industrial Co.,Ltd.` `Matsushita` as a string counts
zero too, for the same reason.

**`(C)` counts 4 against an expectation of 17.9864**, which is *below* chance —
the exact trap the session brief warns about, and the reason the expectation is
printed on every line whether it helps or not.

## `BRGR` counts 4 and it is still absent

Four occurrences against 0.0703 expected is a fifty-seven-fold ratio and a
Poisson tail small enough to look decisive. Read in context, all four are inside
data:

```
/OrgData/stream/OPDS       inside a Cinepak codebook payload
/OrgData/stream/SLDS       inside a Cinepak codebook payload
/OrgData/room/room202.bin  inside cel data
(the fourth is the pressed copy of one of these)
```

**None is followed by a member count, an offset table, or anything an archive
header has.** The chance expectation said signal and the context said noise —
which is the mirror image of the notes' `[1 of 2]` about ratios below five
occurrences, and the same lesson: the arithmetic is necessary and it is not
sufficient. **`BRGR`, the third disc's archive format, is not on this disc.**

## `APPSCRN` counts zero, and this time that means something

The magic is known, so the search could have found the thing. **Zero over
301,761,600 bytes.** Six discs, and only the third has a banner screen — the
SDK's untouched `FICTIONAL DEVELOPER / BOGUS TITLE` placeholder. *Not found* is
*not present* on a fourth pressing.

## The two-way cross-reference

`/launchme` is 246,232 bytes and, unlike the fifth disc's binary, it ships its
filenames as literals: `$boot` counts 117 and `OrgData` 116.

```
path-shaped strings in /launchme    131
  resolve exactly                   105
  resolve case-folded                 2
  resolve to nothing                 24
files named by /launchme            107 of 366
```

**This is the best resolution rate in the collection** — 105 exact against the
second disc's 38 and the third's 1 — because this studio wrote paths and the
others concatenated them. `$boot/` is the console's own mount alias and the
plain-text tables agree: `/OrgData/images/image.scp` holds
`$boot/OrgData/images/gameover.img` and its neighbours, `/OrgData/stream/stream.scp`
lists the eight films, `/OrgData/effect/Geffect.list` lists the sound effects.

### Every miss, one at a time

The platform notes are explicit that a count of misses is not a finding and that
each must be looked at. All twenty-four:

**Six are the extractor keeping one non-printable byte of context** —
`0$boot/OrgData/images/image.scp`, `T$boot/OrgData/etc/3DOlogo.cel`,
`X$boot/OrgData/images/CopyRight.img`, `p$boot/OrgData/images/operation.img`,
`p$audio/dsp/mixer4x2.dsp`, `Ttmacrodata/earth.img`. Strip the leading byte and
five of the six resolve.

**Three are alias targets** the SDK's own boot script defines: `$audio/dsp/...`
is `$audio`, not a disc path.

**Three are the console's NVRAM and not the disc**: `/nvram/RH_HAUZERJ`,
`/nvram/another`, `/nvram/dummy`. Chapter 13.

**Two are templates the program completes at run time**: `$boot/OrgData/room/roomXXX.bin`
and `macroXXX`. And the disc is charming about it — **`/OrgData/macro/macroXXX`
exists**, 112 bytes of near-empty binary, the placeholder filename pressed onto
a retail CD.

**Eight are English words and interface text with a slash in them**: `I/O`,
`I/O.`, `i/o`, `i/c`, `R/R`, `sending/receiving`, and two four-character
fragments of a false split.

**And two are a directory that does not exist.** `macrodata/macro000` and
`macrodata/earth.img` name a directory `macrodata`, which counts **2** over the
whole pressing — both of them inside `/launchme` — and the disc has
`/OrgData/macro/` with `macro001` upward and no `macro000` at all. That is an
older path scheme left in the binary.

### And one miss does not dissolve

```
$boot/OrgData/menu/game.anim
```

**`/OrgData/menu/` holds `continue.anim`, `opening.anim`, `operation.anim`,
`start.anim` and `title.img`. There is no `game.anim`.** The literal string
`game.anim` counts **1** over the whole 301,761,600-byte pressing, and that one
occurrence is inside `/launchme`.

**The platform notes record zero cut content on three discs of three.** This is
the first named-and-absent asset the collection has found on a 3DO disc: the
program carries the path of a menu animation that was not pressed, in the same
table as four that were. It is one string and it is not a story — the code path
may be unreachable, the file may have been folded into another — but the
measurement is that a name resolves to nothing and its four siblings resolve
exactly.

## The other direction: what nothing names

```
files named by /launchme                       107 of 366
files named by nothing in /launchme            259 of 366
of those, under /System                        102
```

**The 102 `/System` files are named by nothing on the disc because the console
boots from them**, which is the second disc's result on a sixth object. The
remaining 157 are the game's own data addressed by the tables — the room
list, the effect list, the image list, the stream list — which are themselves
plain text and which chapter 11 cross-references to the last file.

And the three rooms **nothing at all names**, in `/launchme` or in any table, are
`room214.bin`, `room215.bin` and `room216.bin`. Chapter 11 measures that on the
pressing and chapter 16 leaves it as a residue.

## The abbreviations, and which ones the object proves

The session brief lists twelve and this chapter adds two the object supplied.
**Eight of the fourteen are demonstrable from the object itself** and six are
not, and this document says which:

```
DS       Data Stream          PROVED -- the platform's own name for the format,
                              and all eight files begin SHDR
GODS     Game Over DS         PROVED -- the film renders the words GAME OVER
OPDS     OPening DS           PROVED -- the film renders the opening titles
PADDS    PAD DS               PROVED -- the film renders a 3DO controller
MESDS    MESsage DS           PROVED -- the film renders the prologue messages,
                              and /OrgData/mes/ holds the same kind of text
追加     tsuika, "additional"  PROVED -- three filenames read 追加MES4/5/6
                              beside floor001..003 in the same directory
HAUZER   the title            PROVED -- CopyRight.img renders "Doctor Hauzer"
                              and OPDS renders the title card
HAYASHI  a person             PROVED -- OPDS credits "Directed by KENICHIRO
                              HAYASHI"

OrgData  ?                    NOT PROVED -- nothing on the disc expands it
isearch  ?                    NOT PROVED -- the 49 files are IMAG pictures of
                              objects being examined, which is consistent with
                              "item search" and does not demonstrate it
EDDS     ?                    NOT PROVED -- the film shows a cave and a shore,
                              which is consistent with an ending and does not
                              demonstrate ED
SLDS     ?                    NOT PROVED
STDS     ?                    NOT PROVED
TRDS     ?                    NOT PROVED
```

**Eight proved of fourteen, counted from the list above.** The three unproved
film names are the ones this
document declines to guess at, and `OrgData` — the name of the directory holding
everything the game owns — is the one nobody can expand from the bytes.

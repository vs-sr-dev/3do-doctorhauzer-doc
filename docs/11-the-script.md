# 11 — the script: the first object in this collection that ships its own writing

*Measure: 13 text files in `/OrgData/mes/`, 102,332 bytes of plain text across
20 files on the disc; 29,796 two-byte sequences of which **29,794 are valid
Shift-JIS pairs, 99.9966 %**; 27 distinct room ids, every one of which names a
room file that exists; and one directory named after a person the game's own
opening titles credit.*

**No previous object in this pipeline — on any platform, across fifty-six
sessions — has shipped its script as readable text.** Alone in the Dark's was
compressed inside a rewritten PKZIP. Super Street Fighter II Turbo's interface
text was drawn in pixels. Wolfenstein 3D had none. This disc has its messages in
files you can open.

This chapter is here because the owner of the machine asked for a chapter about
the writing rather than about the formats, and chose this one.

## Proving the encoding rather than assuming it

The disc is Japanese, which is a reason to suspect Shift-JIS and not a reason to
report it. The test is the lead-byte ranges: a Shift-JIS double-byte character
has a lead in `0x81`–`0x9F` or `0xE0`–`0xEF` and a trail in `0x40`–`0xFC`
excluding `0x7F`.

```
                              bytes   ASCII   valid SJIS pairs   stray high
MESSAGE1.TXT                 12,995   7,971         2,512             0
MESSAGE2.TXT                 11,153   6,953         2,100             0
MESSAGE3.TXT                  3,361   1,577           892             0
mes.scp                      11,409     768         5,320             1
mes_no.scp                   12,585   1,916         5,334             1
_mes.scp                      7,781     543         3,619             0
_mes_no.scp                   9,541   2,303         3,619             0
floor001.message             10,529   5,871         2,329             0
floor002.message              8,857   4,977         1,940             0
floor003.message              2,934   1,194           870             0
(three more, named below)     6,273   3,751         1,261             0
                                             -----------------   ----------
                                                    29,796             2
```

**99.9966 % of the non-ASCII bytes are part of a valid Shift-JIS pair**, and
eleven of the thirteen files decode whole with a Shift-JIS codec and no
exception. The two stray high bytes are in `mes.scp` and `mes_no.scp`, one
each.

**And the encoding is why every path-printing tool in this box dies on this
disc.** Three filenames under `/OrgData/mes/MES by HAYASHI/` are themselves
Shift-JIS:

```
92 c7 89 c1 4d 45 53 34   ->   追加MES4
92 c7 89 c1 4d 45 53 35   ->   追加MES5
92 c7 89 c1 4d 45 53 36   ->   追加MES6
```

**追加 is *tsuika*, "addition" or "supplementary".** So the three are
*supplementary MES 4, 5 and 6* — an expansion the object proves about itself,
in a directory whose other three files are `floor001`, `floor002` and
`floor003`. Under the default Windows console codepage `opera.py --list` and
`hashall.py` both raise `UnicodeEncodeError` on those names, and `hashall.py`
had written **199 records of 366** before dying without an error a caller would
notice. `PYTHONIOENCODING=utf-8` fixes both, and the record count was checked
against the file count before any hash list on this object was used.

## The diff that cost one command

`/OrgData/mes/MESSAGE1.TXT` and `/OrgData/mes/MES by HAYASHI/floor001.message`
open with the same room header. Nobody had compared them.

```
MESSAGE1.TXT      12,995 B   sha1 4fb3217a9c0082a9...
floor001.message  10,529 B   sha1 8ab920458592787f...
byte-identical    : False
```

They are not the same file, and they are the same text:

```
room ids in MESSAGE1.TXT      : 12
room ids in floor001.message  : 12
shared                        : 12
only in one or the other      : 0
```

```
distinct Japanese runs of >= 2 characters
  MESSAGE1.TXT      192          floor001.message   181
  shared            178
  share of floor001's runs that are in MESSAGE1 : 98.34 %
  share of MESSAGE1's runs that are in floor001 : 92.71 %
```

**The difference is the line prefix and nothing else.** The first line of each,
with the Japanese shown as its bytes:

```
MESSAGE1.TXT      ////////////////////////////玄関(F1R001)//////////////////
floor001.message  \t////////////////////////////玄関(F1R001)/////////////////
```

`MESSAGE1.TXT` prefixes its content lines with `//` and `floor001.message`
indents them with a tab. **One is the production form of the other**, and
`MESSAGE1.TXT` is the larger of the two by 2,466 bytes — the extra `//` markers
and the lines they comment out.

玄関 is *genkan*, a Japanese entrance hall. **The room ids are keyed to named
rooms**, and `(F1R001)` is the front door of the house the whole game happens
in.

## The cross-reference, in both directions, and it very nearly closes

The room ids are floor-and-room keys. The floors map to the file numbering as
**F1 → `room0nn`, F2 → `room2nn`, F3 → `room3nn`** — there is no `room1nn` on
the disc at all.

```
distinct room ids in /OrgData/mes/            : 27
  ids that name a room file that exists       : 27 of 27
  ids that name nothing                       : 0

/OrgData/start.script names                   : 28 rooms
  that exist as room*.bin                     : 28 of 28
  named by start.script, absent from the disc : 0
```

**Zero misses in either direction, on both references.** The platform notes
record zero cut content on three discs; this is a fourth, from a completely
different kind of reference — a data table and a script rather than a binary's
string table.

`start.script` is 668 bytes of plain ASCII and it is a room table with
coordinates:

```
ROOM303  303 0 200 0   ROOM305  305 100 200 -600   ROOM002  2 0 200 -400 ...
```

**And three rooms are named by nothing.**

```
union of the two references covers    : 30 of 33 room files
room files named by nothing           : room214.bin, room215.bin, room216.bin
```

Checked on the pressing rather than on the file tree, because the platform
notes are emphatic that a filename lives in a directory block:

```
over the whole 301,761,600-byte track:
  room214   3        room215   3        room216   3
```

**`/OrgData/room` has three directory copies, so three is the floor** — each of
those strings occurs exactly once per copy of its own directory entry and
nowhere else on the disc. `ROOM214`, `ROOM215` and `ROOM216` in upper case
count zero. The three files are **369,332 bytes between them and hold 38 cels** —
37,648 / 256,516 / 75,168 bytes and 3 / 26 / 9 cels — `room216.bin` is pressed
**four times**, and **nothing on the disc names any of them.** They are listed in chapter 16 rather than explained.

## The person the disc names

`/OrgData/mes/MES by HAYASHI/` is a directory named after a member of the team,
and this pipeline's editorial line is that what is on the disc is published.
Here that decision needed no weighing, because **the shipped game names the same
person on screen**:

```
python tools/cvidmovie.py _work/files/OrgData/stream/OPDS --contact sheet.png
```

`/OrgData/stream/OPDS` is the opening film, and among its title cards is

```
                    Directed by
                KENICHIRO HAYASHI
```

with `Programmer MASAHIRO NODA` a few frames later. **The directory publishes no
identity the product does not**, which is exactly the structure the platform
notes recorded for the fifth disc, where a build machine's volume name carried a
first name and the game's own credit sequence carried the full one.

The line this pipeline draws is at **reach**, and only there. Over the whole
262,758,400-byte user area:

```
python tools/unowned.py _work/hauzer.bin --range 0 128299 --contacts
```

```
mail addresses            1 occurrence,  1 distinct, lengths 7..7
telephone-shaped          10 occurrences, 10 distinct, lengths 8..11
URL-shaped                0
postal-code-shaped        4 occurrences, 4 distinct, lengths 8..9
```

**Those are shape matches and this document does not call them contact
details.** The denominator is 262 megabytes of which 116 are Cinepak and SDX2,
and a seven-character mail-shaped run and ten grouped-digit runs across that
much compressed data are what chance produces. The counter discards the matched
text inside the function and it is not reachable from any output path, so the
count is publishable and the values are not — which is the point of writing it
that way. Chapter 13 takes the personal-data question as a whole.

## What the writing is worth measuring for

The disc holds **twelve rooms on floor 1, sixteen on floor 2, five on floor
3**, and the messages cover twenty-seven of the thirty-three. `MESSAGE1.TXT`,
`MESSAGE2.TXT` and `MESSAGE3.TXT` are one file per floor and `floor001`,
`floor002`, `floor003` are the same three under a person's name. **The house is
the game and the script is indexed by the house** — every message the player
can be shown is filed under the room they will be standing in when they see it.

That is a structural fact about how the game was written, it took one diff and
one regular expression to establish, and it is the sort of thing that is only
available because a studio in 1994 shipped a directory it meant to delete.

# 01 — the object: a Japanese 3DO disc that presses a third of itself twice

*Measure: one CHD of 149,661,045 bytes; one `MODE1_RAW` track of 128,300
sectors; a 262,758,400-byte user area; 366 files holding 161,346,866 bytes;
and 43,970 sectors that are second copies of files.*

`Doctor Hauzer`, Riverhill Soft, Japan, pressed **1994-04-15 11:30:33**. A
fully polygonal first- and third-person horror game set in one house. It is the
sixth 3DO disc this pipeline has opened and the second-oldest of the six.

## What it is, in one paragraph

A single-track CD-ROM, Mode 1, 2,048-byte data sectors, no audio track, using
the console's own **Opera** file system and not ISO 9660. 366 files in 32
directories, all of the game's own data under one directory called `/OrgData`
with seventeen subdirectories named for what they hold. Eight Cinepak films
through the platform's Data Streamer, 45 megabytes of SDX2 music, 77 `IMAG`
full-screen images, 1,157 cels, 33 rooms, and the game's script in **plain
Shift-JIS text**.

## The four denominators, and every figure in this repository names one

This disc has **four** denominators where earlier discs had three, and the
fourth is new to the collection:

```
the pressing, in sectors        128,300              = 38.5285 % of a 74-min CD
the user area, in bytes         262,758,400          = 128,300 x 2,048
the volume's own declaration    128,000 blocks       = 262,144,000 = 250 MiB
bytes inside files              161,346,866          = 61.4050 % of the user area
SECOND COPIES OF FILES          90,050,560           = 34.2712 % of the pressing
```

**The decision this repository makes about the fourth, stated once and applied
everywhere.** The 43,970 sectors of second-and-later file copies are **inside
the user area and outside `bytes in files`**. They are real pressed sectors,
they belong to files, and they are not *bytes in files* — a file of 3,097,280
bytes with seven copies contributes 3,097,280 to `bytes in files` and
18,583,552 to the pressing. Every fraction below says which of the two it is a
share of. This is why `bytes in files` is **61.4050 %** here where the fifth
disc's was 91.2301 %, and the difference is not a less full disc.

## What the object keeps, and what it loses

**It keeps** — measured, not assumed:

- **every sector of the pressing.** Sync correct on 128,300 of 128,300, header
  MSF equal to LBA + 150 on 128,300 of 128,300, **zero EDC mismatches, zero
  ECC P and zero ECC Q mismatches**, and the eight reserved bytes zero on every
  sector. What follows is a statement about a pressing and not about a dump;
- **the whole index.** The sector map closes at **zero sectors owned by
  nothing** and zero double claims;
- **the game's script, readable.** 13 files of Shift-JIS text, 29,796 two-byte
  sequences of which 29,794 are valid Shift-JIS pairs;
- **an SDK older than any disc in this collection but the launch title's**;
- **its own copyright notice** — as a picture, not as a string.

**It loses**:

- **190,240 bytes of one film's declared sound.** `/OrgData/stream/TRDS`
  declares 1,552,384 sample bytes in its `SNDS SHDR`; before this session's
  resync a walker found 1,362,144 and stopped. The bytes are there; a
  four-byte defect in the multiplex hides them. See chapter 05;
- **nothing else that has been found.** There are no unowned sectors, no
  zero-length files, no truncated directories and no unreadable file.

## Coverage — what fraction of this disc has a derived format

This is the number that says how much of a session was real, and it is not the
sector map. The sector map says every sector belongs to something; it does not
say anybody knows what.

```
                                                          files       bytes    % user
Data Streamer film (Cinepak), every chunk walked              8    93,585,408  35.6165
AIFF-C container, SDX2 sample data                           12    45,412,116  17.2828
IMAG image, geometry closed, pixel order measured            77    11,830,940   4.5026
room file: a 3-word offset table and 1,066 cels              33     7,955,696   3.0278
AIFF container, codec NONE                                   49       668,316   0.2543
ARM Image Format executable                                  36       568,284   0.2163
/signatures: size and fill measured, content not read         1       335,872   0.1278
cel or animation container                                   10       127,668   0.0486
plain text (Shift-JIS or ASCII)                              18        57,194   0.0218
FORM 3INS DSP instrument                                     56        49,156   0.0187
/rom_tags and /Disc label, derived record by record           2           260   0.0001
NO FORMAT DERIVED                                            64       755,956   0.2877
TOTAL BYTES IN FILES                                        366   161,346,866  61.4050
```

Every one of the 366 files is in exactly one bucket and the column sums to the
directory's own total, so nothing is counted twice.

**Identified: 160,590,910 of 161,346,866 bytes in files = 99.5315 %.** As a
share of the user area that is **61.1173 %**, and that number is not comparable
with the five neighbours' — because on those discs the copies were 0.03 % of
the pressing and here they are 34.27 %.

**Both figures are published and the difference is stated rather than
chosen.** Counting the second copies as what they are — copies of files whose
format is derived — the identified share of the user area is **95.3886 %**,
which is the highest in the collection; counting distinct bytes only it is
**61.1173 %**, which is the lowest. Chapter 15 does the whole table and it sums
to the user area to the byte.

## Where the bytes are

```
directory                    files          bytes    % of user area
/OrgData/stream                  9     93,585,570        35.6166
/OrgData/music                  12     45,412,116        17.2830
/OrgData/room                   33      7,955,696         3.0278
/OrgData/isearch                49      7,528,252         2.8650
/OrgData/images                 24      3,534,670         1.3452
/OrgData/effect                 50        661,433         0.2517
/                                5        582,598         0.2217
/System/*                      102        403,961         0.1537
everything else                 82      1,682,570         0.6403
```

**`/System` is 102 files of 366 and none of them is this game's.** It is the
control this repository uses whenever a per-file statistic is quoted, and it is
the reason the collection-wide hash crossing is 15.5 % here against the fifth
disc's 50.2 %: **all 56 crossing hashes are under `/System`, 56 of 56.**

## The three things this disc did to the platform notes

1. **It broke the rule that said this could not happen.** The notes carried,
   `[2 of 2]`, *the redundancy is in the index, not in the data*, with an
   explicit contrast against CD-i. A third of this disc is duplicated
   **content**. Chapter 04 measures what the unit of duplication actually is,
   and it is not the file.
2. **It made the `IMAG` `pixel order` trap testable for the first time since
   the first disc — and the trap did not fire.** 77 files, the descriptor
   agrees with the measurement on 77 of 77, where the first disc's descriptor
   lied on 31 of 61. Chapter 06.
3. **It closed an open question that had survived five discs.** Eight bits per
   pixel was *the one cel depth no disc has used*. This disc has **729 cels at
   8 bpp of 1,157**. Chapter 07.

## The question, and the answer this repository gives

> A Japanese 3DO CD-ROM of April 1994, built on an SDK closer to the launch
> title than to anything else; which duplicates a third of itself in content
> and not in index, against a written rule of the platform; which uses all
> three of the graphics containers the other five discs divided between them;
> which ships its own script in the clear inside a directory named after a
> person; and which arrives eight months before the 3DO port of the game it is
> called a clone of.

**On the duplication: the unit is not the file, it is a contiguous run of files
drawn from different directories** — a working set — and twenty-four such runs
are pressed sixty-seven times between them. That is the CD-i result in its
exact form, and chapter 04 says so with the addresses.

**On the clone question: the axes that close point away from a port.** The byte
order is the console's on 33 of 33 rooms and 77 of 77 images, the containers
are the platform's own three, and the script is plain text where Alone in the
Dark's was compressed inside a rewritten PKZIP. Chapter 12 is the table, and
the owner of the machine decided that rows which do not close are omitted
rather than guessed at.

| | |
|---|---|
| 02 | the technical sheet, with the command on every line |
| 03 | the file system, the sector map and the fill that closes to zero |
| 04 | **the copies: a third of the disc is itself, and the unit is a run** |
| 05 | the eight films, and the one that needed four bytes skipped |
| 06 | the 77 `IMAG` images, and a trap that did not fire |
| 07 | 1,157 cels, 33 rooms, and eight bits per pixel |
| 08 | the audio |
| 09 | the executables and an SDK older than four of five |
| 10 | strings, and both directions of the cross-reference |
| 11 | **the script, and the person the disc names** |
| 12 | the clone question, as a table of measured axes |
| 13 | personal data, user state and protection |
| 14 | against the collection |
| 15 | the accounting, which must sum to the user area |
| 16 | leftovers |
| 17 | corrections |
| 18 | the scoring |

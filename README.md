# Doctor Hauzer (Japan) — a 3DO disc that presses a third of itself twice

Documentation of one retail 3DO CD-ROM, measured from a CHD image. No bytes of
the product are in this repository — hashes and figures only. Sixth 3DO object
in this pipeline, and the second-oldest of the six.

## The short sheet

```
title              Doctor Hauzer, Riverhill Soft, Japan
pressed            1994-04-15 11:30:33   (/rom_tags type 0x0c, 1904 epoch)
image              Doctor Hauzer (Japan).chd   149,661,045 bytes
                   sha1 94a5f18422f811191a472d89e0353a387e7e8c14
track              1, MODE1_RAW, SUBTYPE:NONE, PREGAP:0, no audio track
sectors            128,300  =  38.5285 % of a 74-minute CD
user area          262,758,400 bytes
volume             Opera, not ISO 9660; declares 128,000 blocks = 250 MiB exactly
files              366 in 32 directories, 161,346,866 bytes, 362 distinct sha1
sector map         closes: 0 owned by nothing, 0 double-claimed
integrity          sync, MSF, EDC, ECC P, ECC Q clean on 128,300 of 128,300
```

```
SECOND COPIES OF FILE CONTENT   43,970 sectors = 90,050,560 bytes = 34.2712 %
eight Cinepak films             93,585,408 bytes = 35.6165 % of the user area
recorded sound, ALL of it       67,611,225 bytes = 25.7313 %
77 IMAG images, 320 x 240       11,830,940 bytes, pixel order measured on 77/77
1,157 cels                      729 of them at 8 bits per pixel
33 rooms                        a 3-word big-endian offset table over 4 sections
identified, including copies    95.3886 %      distinct bytes only: 61.1173 %
```

## What is unusual about it

**A third of this disc is itself.** Five 3DO discs of five had exactly two files
with a second copy. This one has eighty, with up to seven copies each, and
90,050,560 bytes of duplicated **content** — against a platform-notes rule that
said, at `[2 of 2]`, *the redundancy is in the index, not in the data*.

**And the unit of duplication is not the file.** Sorting every copy of every
file by block address and joining runs shows **24 contiguous runs of files —
drawn from different directories — pressed 67 times between them.** Six files
from five directories laid down end to end and written four times over. That is
the CD-i working-set result, on a 3DO, measured from the addresses the file
system already declares.

**It closes an open question that survived five discs.** *Eight bits per pixel —
the one cel depth no disc has used.* There are 729 of them here.

**It makes a five-disc-old trap testable, and the trap does not fire.** The
`IMAG` descriptor's `pixel order` byte lied on 31 of 61 files on the 1993 launch
title; here it agrees with the measurement on **77 of 77**.

**It ships its own script.** `/OrgData/mes/` holds the game's messages as plain
Shift-JIS text — the first object in fifty-seven sessions of this pipeline, on
any platform, to do so — in a directory named `MES by HAYASHI`, after a person
the game's own opening titles credit as its director.

## The chapters

| | |
|---|---|
| [00](docs/00-predictions.md) | predictions, written before the disc was opened |
| [01](docs/01-the-object.md) | what the object is, the four denominators, and the coverage |
| [02](docs/02-the-sheet.md) | the technical sheet, with the command on every line |
| [03](docs/03-the-file-system.md) | the file system, the sector map, and a fill that closes to 0.00 sectors |
| [04](docs/04-the-copies.md) | **the copies: a third of the disc is itself, and the unit is a run** |
| [05](docs/05-the-films.md) | eight Cinepak films, and one that needed four bytes skipped |
| [06](docs/06-the-imag-images.md) | 77 `IMAG` images, and a trap that did not fire |
| [07](docs/07-cels-and-rooms.md) | 1,157 cels, 33 rooms, and the cel depth no disc had used |
| [08](docs/08-the-audio.md) | the audio, and two thirds of it where no AIFF reader looks |
| [09](docs/09-the-executables.md) | an SDK older than four of five, and the exception is the studio's |
| [10](docs/10-strings-and-the-cross-reference.md) | strings, and one file that is named and not there |
| [11](docs/11-the-script.md) | **the script, and the person the disc names** |
| [12](docs/12-the-clone-question.md) | is it a clone of Alone in the Dark, and in what precise sense |
| [13](docs/13-personal-data-and-protection.md) | personal data, user state and protection |
| [14](docs/14-against-the-collection.md) | against the collection: 56 of 362, all under `/System` |
| [15](docs/15-the-accounting.md) | the accounting, which sums to the user area to the byte |
| [16](docs/16-leftovers.md) | what did not close, with how much of it there is |
| [17](docs/17-corrections.md) | corrections, mine and the briefing's, and two new tool defects |
| [18](docs/18-prediction-scoring.md) | the scoring: 13.00 of 13 inherited, 30.25 of 41 open |

## The lists

`notes/sha1-all.txt` — one record per file, sha1 first, 366 records for 366
files. `notes/copies.txt` — one record per multi-copy file with every copy's
block address and whether the copies agree. `notes/ccb-list.txt` — one record
per cel, 1,157 of them, with geometry and depth. `notes/streams.txt` — the Data
Streamer audit. `notes/crossall.txt` — the collection-wide hash sweep.

## Tools

`tools/` carries the pipeline's shared box, 457 files, of which **three were
written for this object**: `filecopies.py` hashes and locates every copy of
every file and finds the repeated runs; `imagwalk.py` censuses the `IMAG`
descriptor and measures the pixel order instead of reading it; `streamaudit.py`
accounts for a Data Streamer file by chunk tag and totals the sound the films
carry, with an explicit and reported resync for the one film that needs it.

**Everything needs `PYTHONIOENCODING=utf-8`.** Three filenames on this disc are
Shift-JIS and two inherited tools die on them under the default Windows
codepage — one of them leaving a hash list silently truncated at 199 records of
366. See [17](docs/17-corrections.md).

## Platform notes

The running checklist this object was read against, and which it changed, is
[3do-platformnotes-doc](https://github.com/vs-sr-dev/3do-platformnotes-doc). It
now covers six discs.

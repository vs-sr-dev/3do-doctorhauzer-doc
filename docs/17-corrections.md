# 17 — corrections: the pre-briefing's, mine, and two more inherited defects

*Measure: eight errors in the material this session was handed, six in this
session's own work, and two new inherited tool defects, taking the running list
to eighteen.*

The session brief said of its own pre-briefing: *treat it as `[unverified]` line
by line — and know that it has run twenty tools and holds three big conclusions,
which makes it more dangerous, not less.* That was correct.

## Against the brief and the pre-briefing

**1. The platform notes are 2,881 lines, not 2,867.**

```
wc -l 3do-platformnotes-doc/3do-platform-notes.md   ->   2881
```

At commit `7fc9840`, working tree clean. Fourteen lines out. It changes nothing
and it is the first thing this session measured, which is why it is first here.

**2. `90,222,592 bytes` and `34.3367 %` are not "second copies of files".**

The brief and `_pre\object.txt` both use those figures for duplicated file
content. They are `opercopies.py`'s total and it includes directory copies:

```
file second copies      43,970 blocks   90,050,560 bytes   34.2712 %
directory copies            84 blocks      172,032 bytes    0.0655 %
                        ------                              -------
                        44,054          90,222,592          34.3367 %
```

**The figure for duplicated file content is 90,050,560 bytes = 34.2712 %**, and
it is the sector map's `copy` bucket to the sector. Both numbers were true of
something; only one is true of the sentence they were used in.

**3. There are 77 `IMAG` files, not 76 — and the pre-briefing censused by
name.**

75 files carry `.img`, one carries `.IMG`, and `/OrgData/images/MADO3` carries
**no extension** and begins `IMAG` like the other 76. The platform notes'
instruction, from the fourth disc, is *census by first four bytes, never by
name*, and the pre-briefing did it by name and lost one.

**4. `/OrgData/isearch` is not "49 files, no extension, no magic".**

`_pre\formats.txt` lists it as unopened and unidentified, 2.87 % of the
pressing. All 49 files are named `sea*.img`, all 49 begin `IMAG`, and all 49 are
320 × 240 sixteen-bit pictures. The directory was one `head -c4` away from being
closed.

**5. The seven-copy list was filtered from ten to four, and the conclusion was
drawn from the four.**

The brief and `_pre\question.txt` both list `music003.aifc`, `room004.bin`,
`cmd01.img` and `cursor.cel` and conclude *the seven-copy files are the ones a
room needs at once*. There are ten, and the other six are `note.img`, `pen.cel`
and **four `/System/Audio/dsp` instrument patches**, which belong to the SDK and
are byte-identical with files on five other discs. The reading survives in a
better form (chapter 04) and the evidence as presented was selected.

**6. The AIFF sample total double-counts `sinewave.aiff`.**

```
_pre: 45,410,350 + 647,723 + 8,820 = 46,066,893
aiffread.py, over 61 files          46,058,073
```

`647,723` is the AIFF-`NONE` total and it **already contains** the SDK's
8,820-byte sinewave. The correct figure is **46,058,073 = 17.5287 %** of the
user area, not 46,066,893 = 17.5320 %. Every figure in this repository derived
from it was recomputed.

**7. The pre-briefing contradicts itself about `MES by HAYASHI`.**

`_pre\object.txt`'s directory table says the directory holds **6** files, 28,593
bytes. `_pre\formats.txt` says it holds **three more, `floor001.message`,
`floor002.message`, `floor003.message`**. It holds six: those three plus
`追加MES4`, `追加MES5` and `追加MES6`, whose names are Shift-JIS — which is the
same reason the tools crashed, so the file that documented the crash is the file
that lost the files to it.

**8. `_pre\question.txt` calls `protscan.py`'s output "a positive-control
match".** It is a positive control that **fires on 339 files of 366**, and the
eleven markers are zero. The distinction matters because the sentence as
written could be read as the disc matching a marker.

## Against this session's own work

**9. `predcount.py` caught the predictions header, for the sixth session
running.** It was typed as `inherited 11.80, open 26.65` and the sums are
**11.75** and **26.68**. Both were added by eye while the clauses were still
being edited. The header now standing is the command's output.

**10. The `BL` decode at offset 4 was off by four bytes, and it made every
image an exception.** ARM's `BL` targets `PC + 8 + offset × 4` where `PC` is the
instruction's own address; the first pass used `+ 4` and reported **36 of 36
images as `ro + rw + 4` exceptions**, which would have been a spectacular and
entirely false finding about the whole disc. The `aifcensus.py` output next to
it said 35 of 36, and the disagreement between two tools is what caught it.
**One image is the exception and it is `/OrgData/program/sramtools`.**

**11. The room-id mapping was wrong on the first pass.** `(F1R001)` was mapped
to `room101.bin` and the disc has no `room1nn` at all. The correct mapping is
**F1 → `room0nn`, F2 → `room2nn`, F3 → `room3nn`**, and with it 27 of 27 ids
resolve where the wrong mapping resolved 15 and produced twelve phantom missing
files.

**12. Four figures were written into chapters before being measured, and the
commands caught all four.** The `IMAG` byte total (`11,833,972` for
`11,830,940`), the film chunk count (`11,505` for `11,405`), and two of the
three room offset tables quoted in chapter 07 (`room002.bin` and `room305.bin`).
They were recomputed and replaced. **This is rule 10's insidious error and it
happened four times in one session**, in every case from arithmetic done in
prose rather than in a shell.

**13. Chapter 07 first claimed every cel depth was covered "except 2 bpp".**
The second disc supplied 2 bpp on 41 cels. With 8 bpp arriving here, **every
depth the platform defines is now seen**, and the open question can be closed
rather than narrowed. The first version of the sentence would have left it open
for no reason.

**14. Chapter 10 said "seven proved of thirteen" over a list of fourteen with
eight proved.** Counted, corrected.

## Two new inherited tool defects, taking the list to eighteen

**Defect 17 — `account3do.py` prints another disc's finding on this one.**

```python
region = 34127872 if fill > 34127872 else 0
```

The line emits

```
not in any file: ANOTHER MACHINE (x86/Watcom), sectors 176,147+  34,127,872  12.9883 %
```

on **any** disc whose *not in a file* total exceeds 34,127,872 bytes. This disc
has 128,300 sectors — **sector 176,147 does not exist on it** — and its sector
map closes at zero unowned, so there is nothing there but copies, index, fill,
zeros and slack. It is the fifth disc's genuine finding, hard-coded, firing
falsely and silently, worth **12.9883 %** of a headline table. Reported and not
fixed, per the rule that fixing an inherited tool quietly is worse.

**Defect 18 — `celdecode.py --all` with no output directory raises a
traceback.** `out` is positional and optional, and `--all` calls
`os.makedirs(a.out)` on `None`:

```
TypeError: expected str, bytes or os.PathLike object, not NoneType
```

It is the ninth tool in this box with no refusal path, and the ninth to fail
with a traceback where a message would do.

**And defect 16 is confirmed and is the one that stops a session.**
`PYTHONIOENCODING=utf-8` is required for `opera.py --list` and `hashall.py` on
this object, and without it `hashall.py` writes **199 records of 366** and exits
in a way a pipeline does not notice. **366 records were counted against 366
files before any hash list was used**, which is the check the brief demanded and
the reason the crossing figure in chapter 14 can be trusted.

## What the running defect list now looks like

```
 1  bmp.py         never says how many files it opened
 2  pe.py          refuses a non-PE with a traceback
 3  wavcheck.py    lower-cases the filename but not --ext
 4  checkscore.py  skips bolded table rows in silence
 5  controltat.py  IndexError on any file shorter than 199 bytes
 6  mdmd.py        prints two verdict words, so grep -c REFUSED undercounts
 7  crossall.py    --skip defaults to empty
 8  crossall.py    "repositories swept" is documented as counting only
                   repositories with a hit; on this run it reported 85 where
                   5 had a hit, so the number is the breadth and not the yield
 9  celdecode.py   PermissionError when given a directory
10  pcspk.py       no refusal path
11  cga.py         no refusal path
12  iso9660.py     refuses correctly and exits 0
13  pak.py         refuses a foreign .PAK with an uncaught traceback
14  sdx2dec.py     refuses a non-AIFF with an uncaught traceback
15  slack.py       no refusal path; dies inside assoc.walk on a non-ISO image
16  opera.py/hashall.py die on a non-ASCII filename under the default Windows
                   codepage, and hashall leaves a TRUNCATED hash list
17  account3do.py  prints the fifth disc's Watcom region on any disc whose
                   not-in-a-file total exceeds 34,127,872 bytes            NEW
18  celdecode.py   --all with no output directory raises a TypeError       NEW
```

## The three tools written today, counted before and after

The second lesson of the previous session was that a tool was overwritten
because nobody looked first, and that counting the files caught it.

```
ls tools/*.py | wc -l   before   454
                        after    457
tools written today              3
```

**Three is three.** `filecopies.py`, `imagwalk.py` and `streamaudit.py`, and
each name was checked against the directory before it was written. `imagecensus.py`
already exists and is a PC-format tool (BMP/JPEG/GIF/ICO) that does not apply
here; `pixorder.py` already exists and was used rather than rewritten.

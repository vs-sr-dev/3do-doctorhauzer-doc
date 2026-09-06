# 14 — against the collection: 56 of 362, and every one of them under `/System`

*Measure: denominators re-derived today rather than taken from the brief — the
root swept holds **119 directories, 114 `-doc` repositories, 85 of them carrying
a `notes\`**, and `crossall.py` reports 85 swept; 362 distinct sha1 on this
disc; 56 crossings, of which **56 are under `/System`** and which appear in
**5 repositories of the 85**.*

## The prediction, written before the sweep

The session's clause C50 predicted **at least 45 of the crossings under
`/System`**, on the reasoning that a 102-file `/System` on a 366-file disc is
what makes this disc's crossing rate low where the fifth disc's was high.

```
python tools/crossall.py notes/sha1-all.txt --collection <root> \
       --skip 3do-doctorhauzer-doc
```

```
my distinct sha1              362
repositories swept             85      (and 85 is exactly the number of -doc
                                        repositories under this root with a
                                        notes/ directory, re-counted today)
CROSSINGS                      56 of my 362 = 15.5 %
crossings under /System        56 of 56
repositories carrying a hit     5, and all five are the 3DO neighbours
empty-file sha1 among mine     no
```

**Fifty-six of fifty-six.** Not one file of this game's own data is
byte-identical with anything else in the collection, on any platform, across
the 114 `-doc` repositories under this root.

## Why 15.5 % where the fifth disc had 50.2 %

The fifth disc shared a whole `/System` with its twin — 116 of 116 files
byte-identical — so half its hash list crossed. This disc's `/System` is 102
files against the others' 94, 116, 116, 117 and 126, and its SDK is eight months
older than three of them:

```
identical /System files with     Crash 'n Burn 45   Slayer 38   Alone 38
                                 SSF2T 38           Wolfenstein 32
```

**45 of the 56 crossing hashes appear in the launch title's repository and 11
do not** — counted from the sweep's own output — and 45 is exactly `sdkdiff.py`'s
count of files byte-identical with that disc, arrived at by a completely
different route. The other eleven are DSP instruments and `sinewave.aiff` that
every 3DO disc carries. The platform
notes' three-way core — 19 `FORM 3INS` instruments plus `sinewave.aiff`, 31,186
bytes, byte-identical across three studios and twenty-seven months — survives
onto a sixth disc.

**And the sweep's known defects were handled.** `--skip` is not the default and
was passed; `repositories swept` is inherited defect eight — it is
documented as counting only repositories with a hit, and here it reports **85**
while only **5** repositories carry a hit and 85 is exactly the number of
`notes/` directories re-counted under the root, so on this run the number is the
sweep's breadth rather than its yield; and the
empty-file sha1 trap — 32 occurrences in 12 repositories — is reported
separately by the tool and **this disc contributes zero to it, because it has no
zero-length files.**

## Where this disc sits in the collection

```
disc                        pressed       % of a CD   recorded sound   identified
Crash 'n Burn               1993-09-09     92.3261 %     0.3230 %       ~77 %
Doctor Hauzer               1994-04-15     38.5285 %    25.7313 %       95.39 %
AD&D Slayer                 1994-08-16     45.4474 %    67.4093 %       87.6184 %
Alone in the Dark           1994-12-19     57.9012 %    77.1890 %       90.7863 %
Super Street Fighter II T.  1995-01-10     45.5568 %    86.2465 %       87.3403 %
Wolfenstein 3D              1995-09-06     17.0276 %    59.7896 %       71.1132 %
```

**The five neighbours' figures were taken from their own `docs\` and not from
memory**, as rule 6 requires.

**And the `identified` column needs its footnote, because this disc's is not
comparable.** On the other five, second copies were 0.03 % of the pressing and
the distinction did not exist. Here they are 34.27 %:

```
identified INCLUDING the second copies of identified files   95.3886 %
identified counting distinct bytes only                      61.1173 %
```

**The first is the one in the table above**, because it is what the other five
columns measure — every sector of every file whose format is derived. The second
is printed beside it in chapter 15 and neither is hidden. **A disc that presses
a third of itself twice cannot have one coverage number**, and saying which one
you mean is the whole content of the decision.

## What this disc did to the platform notes' marks

Six discs, and this one exercises marks that four discs did not touch.

**Broken or weakened:**

```
"the redundancy is in the index, not in the data"   [2 of 2] -> BROKEN
    90,050,560 bytes of duplicated CONTENT, 34.2712 % of the pressing

the IMAG pixel-order trap                          [1 of 1] -> [1 of 2]
    the descriptor lied on 31 of 61 on the first disc and tells the truth
    on 77 of 77 here

the Data Streamer frame count encoded twice        [2 of 2] -> [2 of 3]
    FHDR declares 313 / 767 / 525 where the files hold 2,149 / 2,594 / 848
```

**Confirmed to a higher mark:**

```
the sector map closes at zero unowned              [4 of 5] -> [4 of 6]
iamaduck present                                   [4 of 5] -> [4 of 6]
the whole-mebibyte volume declaration              [3 of 3] -> [4 of 4]
/signatures is 335,872 bytes                       [3 of 3] -> [6 of 6]
rom_tags 0x05 +8 == /signatures first block - 1    [4 of 4] -> [5 of 5]
rom_tags 0x07 +12 == os_code size                  [4 of 4] -> [5 of 5]
the studio's name is a picture                     [3 of 3] -> [4 of 4]
the fill arithmetic closes to the sector           [4 of 4] -> [5 of 5], with a
                                                   FOURTH term
directory copies differ only by a case bit         [3 of 3] -> [4 of 4],
                                                   190 of 190 here
no studio compresses its own binaries              [3 of 3] -> [4 of 4]
the relocation exception is the studio's           2 points -> 3 points
```

**Closed:**

```
open question 3 -- 8 bits per pixel, "the one cel depth no disc has used"
    729 cels of 1,157, and every depth the platform defines is now seen

open question 16 -- how much of SDX2's use is a false economy
    48 files, 638,903 bytes of 8-bit codec NONE on this disc, at the identical
    byte cost of 16-bit SDX2
```

**New, and not previously possible:**

```
a 3DO disc that duplicates file CONTENT, and the unit is a contiguous RUN of
    files across directories -- 24 runs pressed 67 times
a Data Streamer file with a bare tag and no length, which resyncs at +4
the IMAG metadata chunks CPYR / KWRD / CRDT / DESC
a named-and-absent asset -- $boot/OrgData/menu/game.anim
iamaduck counted twice: 4,896 pure sectors and 585 partial ones
```

## What was written into the platform notes, and the commit

`3do-platformnotes-doc` was read in full **before a single clause of
`docs/00-predictions.md` was written** — 2,881 lines at commit `7fc9840` — and
it saved four predictions outright: the 128-against-132 label question, the 1904
epoch, the `0x02` block identity and the fixed +224 offset of the signature are
all settled there and were cited rather than re-derived.

**It was then edited and pushed**, on branch `main`, at commit

> **[`bd94fa8`](https://github.com/vs-sr-dev/3do-platformnotes-doc/commit/bd94fa8)**
> — *Sixth disc: the redundancy is in the data after all, and a trap that did
> not fire.* **+656 lines, −107**, taking the document from 2,881 lines to
> **3,430**.

The mark reconciliation was **re-counted by the document's own command** rather
than by eye and the table now carries a sixth column: **149 opening marks, from
136**, of which seven are new `[1 of 1]` lines and three are new `[corrected]`.

**And what was deliberately NOT promoted.** Five `[2 of 2]` lines this disc
leaves untouched — no `.PAL`, no `M.K.`, no `BRGR`, no `APPSCRN`, one track —
stay at `[2 of 2]`. Being uncontradicted a sixth time is not evidence, and this
disc is the argument for that rule rather than an exception to it: **the one
line it could finally test after five discs of silence turned out to be wrong.**

**One rule was reported as inapplicable rather than confirmed.** The notes'
answered open question 10 — *the builder writes up to the end of a run of
root-directory copies and stops* — cannot be exercised here, because this disc's
seven root copies are single blocks with no two adjacent, so there is no *run* to
end. That is written into the notes as neither a confirmation nor a refutation,
which is what promoting for silence would have avoided saying.

## The debt this repository does not owe and reports anyway

`pc-linksthechallengeofgolf-doc` has **three corrections outstanding from four
sessions ago**. They are not this object's business, they were not paid today,
and they are still due. Saying so is cheaper than the alternative, which is that
they stop being visible.

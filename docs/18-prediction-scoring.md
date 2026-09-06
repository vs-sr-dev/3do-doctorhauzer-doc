# 18 — the scoring: 13.00 of 13 inherited, 30.25 of 41 open, and six clean misses

*Measure: 54 clauses, counted by `predcount.py` before the disc was opened and
scored here row by row; the two totals are never summed.*

**The header below is written from the command's output.** The predicted totals
in `docs/00-predictions.md` were themselves typed wrong by eye — `11.80` and
`26.65` against sums of `11.75` and `26.68` — and `predcount.py` caught them, for
the sixth session running.

```
inherited  13 clauses   predicted 11.75   obtained 13.00   deviation -1.25
                        hits 13   half 0   misses 0

open       41 clauses   predicted 26.68   obtained 30.25   deviation -3.57
                        hits 26   half 9   misses 6
```

**The two totals are never summed.**

## The inherited clauses

| clause | verdict | score | what happened |
|---|---|---|---|
| C01 | hit | 1.00 | sync, MSF, EDC, ECC P, ECC Q and reserved all clean on 128,300 of 128,300 |
| C02 | hit | 1.00 | big-endian on every field; `room001.bin` reads 12,896 BE and 1,613,889,536 LE |
| C03 | hit | 1.00 | the record is 132 bytes, +128 is `00000000`, `--label` prints 128, and no prediction was spent on the difference |
| C04 | hit | 1.00 | `0xa9d42b59` → 1994-04-15 11:30:33, identical in both copies, cited not re-derived |
| C05 | hit | 1.00 | `0x02` A/B = 120,667 / 121 == `/launchme`'s directory entry exactly |
| C06 | hit | 1.00 | 335,872 bytes, sixth of six; and it is not among the 56 crossing hashes, so its content differs from every other repository's |
| C07 | hit | 1.00 | 64 bytes at +224 wholly different; `0x0d`, `0x07`, `0x10`, `0x05` patched, `0x0c` and `0x02` untouched |
| C08 | hit | 1.00 | all five header identities on 36 of 36 |
| C09 | hit | 1.00 | **the top bit is set 0 times over 5,913,600 pixels** — the largest single confirmation of 5-5-5 in the collection |
| C10 | hit | 1.00 | the chunk rule tiles 77 `IMAG`, 10 `CCB `/`ANIM` and 8 films to their last byte |
| C11 | hit | 1.00 | `Riverhill` 0 in all three cases; the copyright notice is a picture |
| C12 | hit | 1.00 | burst 1 and gap 0 on **398 of 398** entries, including the eight Data Streamer files |
| C13 | hit | 1.00 | 190 differing bytes in 3 directory groups, **190 of 190 a case bit**, plus `/rom_tags` |

**Thirteen of thirteen, predicted 11.75.** The inherited clauses were
under-predicted by 1.25 and the reason is the same as last session's: **a clause
that re-tests a settled measurement is arithmetic, and arithmetic scores 1.00 or
0.00.** The correction was applied to the open clauses and not to these.

## The open clauses

| clause | verdict | score | what happened |
|---|---|---|---|
| C14 | half | 0.50 | the copy-hashing pass **is** under sixty lines; the tool as shipped is 260 with the bundle mode, so the clause is half right about its own deliverable |
| C15 | hit | 1.00 | 79 of 80 groups byte-identical, and the one is `/rom_tags`, as the clause said |
| C16 | hit | 1.00 | mean gap > 5,000 blocks on **10 of 10** seven-copy files; overall mean 14,848.2 |
| C17 | **miss** | 0.00 | one copy per band on **17 of 80**; 63 files put two copies in one band. The bands are not the structure |
| C18 | hit | 1.00 | 128,300 − 43,970 = 84,330 = 25.3243 % of a 74-minute CD |
| C19 | hit | 1.00 | the seven-copy set spans 616 B to 3,097,280 B; size does not order the histogram |
| C20 | half | 0.25 | the set is **not** "music, room, interface image, cursor": four of the ten are `/System/Audio/dsp` patches. The working-set reading survived in a better form and the clause's evidence did not |
| C21 | half | 0.75 | the arithmetic supports the working-set reading — 47 files in 24 runs, not a whole-disc mirror — but the drive's behaviour is not measurable and is not claimed |
| C22 | half | 0.25 | the chain up to 7,995,388 **is** clean; the tail is **not** padding, zeros or a second object — it is 104 more chunks of the same film after a bare tag |
| C23 | hit | 1.00 | strips sum to 212 on all three; 212 = 53 macroblocks of four and 210 is not a multiple of four |
| C24 | hit | 1.00 | 21,553,152 bytes of `SNDS`, against a predicted floor of 15,000,000 |
| C25 | half | 0.25 | **the block size is 32,768, not 20,480** — and all **8 of 8** films are a whole number of 32,768-byte blocks with remainder zero. The shape was right and the named number was wrong |
| C26 | hit | 1.00 | 93,585,408 of 93,585,570 = 99.9998 %, the remainder being `stream.scp` |
| C27 | hit | 1.00 | `bytes_per_row × height == payload` on **77 of 77**, against a predicted 70 of 76 |
| C28 | **miss** | 0.00 | the descriptor disagrees with the measurement on **0 of 77**. The trap did not fire |
| C29 | **miss** | 0.00 | the measured order is **lrform on 77 of 77**, not linear. Both halves of the image prediction were wrong and the measurement was made before rendering, which is the only reason they are visible |
| C30 | hit | 1.00 | the `IMAG` headers are big-endian on 77 of 77 |
| C31 | half | 0.75 | three containers and no fourth, confirmed; `BRGR` reads as noise in context. But `ccbread.py` leaves 36 files unchained and the clause promised every cel-bearing file accounted for |
| C32 | hit | 1.00 | big-endian on 33 of 33 rooms and 77 of 77 images |
| C33 | half | 0.25 | **five of seven axes close, not four or fewer.** The direction was right and the number was pessimistic |
| C34 | hit | 1.00 | `/OrgData/item` is two files holding 33 cels; no 52-byte stride, no 292 records |
| C35 | hit | 1.00 | 33 rooms against 8 floor archives; the unit is a room |
| C36 | hit | 1.00 | **99.9966 %** of non-ASCII bytes are valid Shift-JIS pairs, against a predicted 90 % |
| C37 | hit | 1.00 | not byte-identical; 12 of 12 room ids shared; 98.34 % of the Japanese runs shared |
| C38 | **miss** | 0.00 | **27 distinct room ids against 33 rooms** — a difference of six where the clause allowed five. The clause named a number and the number is wrong by one |
| C39 | hit | 1.00 | `OPDS` credits "Directed by KENICHIRO HAYASHI" |
| C40 | **miss** | 0.00 | the counter reports 1 mail-shaped, 10 telephone-shaped and 4 postal-shaped runs, not zero. They are almost certainly chance on a 262-megabyte denominator and **the clause said zero** |
| C41 | hit | 1.00 | `os_code` 79,692 == record `0x07` field B, a fifth distinct value landing in date order |
| C42 | hit | 1.00 | the exception is `/OrgData/program/sramtools`, the studio's own binary |
| C43 | hit | 1.00 | 190 of 190 differing bytes are a case bit with copy 0 upper — it is copy 0, not an older convention |
| C44 | hit | 1.00 | 56 `FORM 3INS` of 56, and 53 / 56 / 63 / 63 / 63 / 77 is monotone by pressing date |
| C45 | hit | 1.00 | no file is user state; `/nvram/RH_HAUZERJ` is in `/launchme` |
| C46 | hit | 1.00 | 61.4050 %, and the copies are declared in or out of every fraction published |
| C47 | half | 0.75 | the in-file undetermined share is **0.2877 %**, well under 4 %, but it was measured by an independent classification of all 366 files and `account3do.py` was **not** re-run, which is what the clause named |
| C48 | **miss** | 0.00 | `/OrgData/isearch` and `/OrgData/room` are **35.4809 %** of the unknown bucket, not 72.98 %. `room*.bin` is not in that bucket at all, and `isearch` turned out to be 49 `IMAG` pictures |
| C49 | hit | 1.00 | 25.7313 %, inside the predicted 25–35 % band |
| C50 | hit | 1.00 | **56 of 56** under `/System`, against a predicted floor of 45 |
| C51 | hit | 1.00 | eight of fourteen abbreviations demonstrable from the object, against a predicted six |
| C52 | hit | 1.00 | the empty-file trap fires at 32 occurrences in 12 repositories; this disc contributes zero and has no zero-length files |
| C53 | hit | 1.00 | the fill arithmetic closes to **0.00 sectors**, with a fourth term no earlier disc had |
| C54 | half | 0.50 | `/OrgData/isearch` is one format repeated — 49 `IMAG`, closed entirely. But the directory's **name does not expand from the object** and the clause promised it would |

## What the six misses have in common, and it is not nothing

**C17, C28, C29, C38, C40 and C48 are all `content` clauses**, and five of the
six were scored **in seconds, on a number, with nobody needing to agree about
what the thing was.** That is last session's prescription working:

- C17 predicted *no band holds two copies of one file*; the tool printed
  17 and 63;
- C28 predicted *at least one disagreement*; the census printed 0;
- C29 predicted *linear on ≥ 70 of 76*; the census printed lrform on 77;
- C38 predicted *within five of 33*; the count was 27, out by six;
- C48 predicted *≥ 70 %*; the arithmetic gave 35.4809 %;
- C40 predicted *zero contacts*; the counter printed 1, 10, 0 and 4.

**C28 and C29 are the pair worth keeping.** They were written to test the
platform notes' oldest untestable trap, and both were wrong in the same
direction: this disc's descriptor is honest. **A prediction that a trap will
fire, and a measurement that shows it does not, is the outcome the clause was
for** — the wrong prediction is what makes the result mean something rather than
being an assumption confirmed.

**C40 is the one that should sting and does not.** The clause said zero and the
counter said fourteen shape matches over 262 megabytes. The clause was wrong to
name zero on a denominator that large; the *editorial* answer — that these are
not contact details and that the count is publishable while the values are not —
is unchanged, and chapter 13 states it with the denominator beside it.

## The calibration, sixteenth object

The series of *predicted minus obtained* on open clauses:

```
+10.5  +7.5  +5.0  +2.0  -14.0  -2.0  +9.0  0.0  +19.75  +5.25  -4.10
-3.40  +9.30  +1.05  -2.50  **-3.57**
```

```
sum        39.78          over sixteen objects
mean       +2.4863
amplitude  33.75          from -14.00 to +19.75
negatives  6 of 16
```

**The sixteenth is negative and the reason is legible.** Twenty-six of the 41
open clauses scored 1.00, and **nineteen of those twenty-six were content
clauses about a count on an object nobody had opened** — the sort last session's
`predcount.py` warning says score about 68 % and which here scored 100 %. The
difference is that this disc's pre-briefing had already run eighteen tools, so
the clauses were written with the shape of the answer visible even where the
number was not.

**The prescription in force is still the boring one and this object does not
change it.** The last six deviations are −4.10, −3.40, +9.30, +1.05, −2.50 and
−3.57. Four of the six are negative and one is +9.30; **anybody correcting for
the run of negatives would have been nine points worse on the thirteenth
object.** No global offset.

**The one prescription this object adds** is about the clause that names a
number inside a tolerance. C38 said *within five of 33* and the answer was six
away; C25 said *20,480* and the answer was 32,768 with the structure intact;
C33 said *four or fewer of seven* and five closed. **Three clauses of 41 were
wrong only in a bound, and all three would have been right as a shape.** The
lesson is not to widen the bound — a wide bound scores nothing — it is that a
clause naming a tolerance should say what it would mean to be outside it, so
that the miss is informative rather than merely a miss.

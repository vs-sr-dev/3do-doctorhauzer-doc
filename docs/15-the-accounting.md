# 15 — the accounting: four denominators, and a table that sums to the user area

*Measure: 366 files each placed in exactly one bucket, summing to 161,346,866
bytes — the directory's own total; and a second table summing to 262,758,400
bytes, the user area, to the byte.*

## The denominator was decided before anything was published

There are four, and the fourth is new to this collection:

```
the pressing                  128,300 sectors      = 38.5285 % of a 74-minute CD
the user area                 262,758,400 bytes    = 128,300 x 2,048
the volume's own declaration  128,000 blocks       = 250 MiB exactly
bytes inside files            161,346,866          = 61.4050 % of the user area
SECOND COPIES OF FILE CONTENT 90,050,560 bytes     = 34.2712 % of the pressing
```

**The rule, applied to every fraction in this repository.** A second copy is
**inside the user area** and **outside `bytes in files`**. `music003.aifc` is
3,097,280 bytes and it is pressed seven times: it contributes 3,097,280 to
*bytes in files* and 21,680,896 to the pressing. Nothing in this repository
counts it twice in one column, and no column mixes the two.

## Table one — every file, in exactly one bucket

```
bucket                                                    files        bytes    % user
Data Streamer film (Cinepak), every chunk walked              8    93,585,408  35.6165
AIFF-C container, SDX2 sample data                           12    45,412,116  17.2828
IMAG image, geometry closed, pixel order measured            77    11,830,940   4.5026
room file: a 3-word offset table and 1,066 cels              33     7,955,696   3.0278
AIFF container, codec NONE                                   49       668,316   0.2543
ARM Image Format executable                                  36       568,284   0.2163
/signatures: size and fill measured, content not read         1       335,872   0.1278
cel or animation container (CCB / ANIM)                      10       127,668   0.0486
plain text (Shift-JIS or ASCII)                              18        57,194   0.0218
FORM 3INS DSP instrument                                     56        49,156   0.0187
/rom_tags and /Disc label, derived record by record           2           260   0.0001
NO FORMAT DERIVED                                            64       755,956   0.2877
                                                            ---   -----------  -------
TOTAL BYTES IN FILES                                        366   161,346,866  61.4050
```

**366 of 366 files, and the column sums to the directory's own total**, so
nothing is counted twice and nothing is missing.

```
identified          160,590,910 of 161,346,866 bytes in files  =  99.5315 %
not derived             755,956 of 161,346,866                 =   0.4685 %
```

## Table two — the whole user area, which must sum to 262,758,400

```
                                                             bytes    % user area
identified bytes, distinct                             160,590,910      61.1173
their second and later copies (43,970 sectors)          90,050,560      34.2712
in a file, kind not derived (64 files)                     755,956       0.2877
the index: 40 directories + 84 directory copies            253,952       0.0966
iamaduck mastering fill, 4,896 sectors                  10,027,008       3.8161
the all-zero tail past the declared volume, 300 sectors     614,400      0.2338
round-up slack in files' and copies' last blocks           465,614       0.1772
                                                       -----------     --------
TOTAL                                                  262,758,400     100.0000
```

**It closes to the byte.**

## The two coverage numbers, and why there are two

```
identified INCLUDING the second copies of identified files   250,641,470   95.3886 %
identified counting distinct bytes only                      160,590,910   61.1173 %
```

**Both are published and the difference is 34.2712 points, which is the object.**

The five neighbours published one number each — ~77 %, 87.34 %, 71.11 %,
87.62 %, 90.79 % — and on those discs the two definitions differed by 0.03
points, so the question never arose. **The figure comparable with theirs is
95.3886 %**, because what they measured is *every sector of every file whose
format is derived*, and on this disc that includes the copies. **The figure that
says how much distinct content was understood is 61.1173 %.**

Saying which one you mean is the entire content of the decision, and a
repository that published only one of them would be hiding the object's main
fact in a rounding.

## What `account3do.py` says, and one line of it is false

The inherited tool was run and its output is in chapter 17's defect list, but
one line has to be addressed here because it is a **12.9883 % error on this
disc's headline table**:

```
not in any file: ANOTHER MACHINE (x86/Watcom), sectors 176,147+   34,127,872  12.9883 %
```

**This disc has 128,300 sectors. Sector 176,147 does not exist on it.** The line
is the *fifth* disc's finding — a PC's Watcom C/C++ installation showing through
where a builder wrote no fill — and it is emitted here by

```python
region = 34127872 if fill > 34127872 else 0
```

which fires on **any** disc whose *not in a file* total exceeds 34,127,872
bytes. On this disc that total is 101,411,534 bytes and **every byte of it is
copies, index, fill, zeros and slack**, because the sector map closes at zero
unowned. **Inherited defect seventeen**, reported and not fixed, and the tables
above are computed independently of it.

## The 64 files with no derived format

755,956 bytes, 0.4685 % of what is in files, largest first:

```
/OrgData/human/HumanPol.bin       188,976    holds 48 cels; the rest not derived
/System/Kernel/os_code             79,692    the kernel, raw, not an AIF image
/OrgData/human/HumanTex.bin        63,452    texture data for the above
/OrgData/item/ItemTex.bin          46,404
/OrgData/font/fontNew.bin          36,363    the Shift-JIS font
/OrgData/item/ItemPol.bin          23,324    holds 33 cels
/OrgData/mes/mes_no.scp            12,585    Shift-JIS, but under the 55 %
/OrgData/macro/macro303            12,424    printable threshold this pass used
/OrgData/macro/macro004            11,416
... and 55 more, none above 11,409 bytes
```

**Two of the buckets above are honest about being partial.** `HumanPol.bin`,
`HumanTex.bin`, `ItemPol.bin` and `ItemTex.bin` hold 81 cels between them whose
structure *is* derived; what is not derived is the rest of those four files, and
they are counted whole as unknown rather than split on an estimate. The same is
true of the `room*.bin` sections 0 and 3 — 1,000,592 bytes across 33 files —
which are inside a bucket marked *derived* because the offset table and the
cels are, and which are named in chapter 16 as the part that is not.

**The largest single thing this session removed from the unknown bucket is
`TRDS`**, 8,683,520 bytes, which `account3do.py` charged to nothing because
`cvidmovie.py` refused it. Four bytes of resync moved 3.30 % of the user area
from *unknown* to *derived*.

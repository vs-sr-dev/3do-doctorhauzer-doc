# 13 — personal data, user state and protection

*Measure: two people are named on this disc and both are named by the shipped
game itself; `unowned.py --contacts` over the whole 262,758,400-byte user area
reports one mail-shaped run, ten telephone-shaped runs and four postal-shaped
runs, and can print none of them; and no file on the disc is user state.*

## What is published, and why

**A directory on this disc is named after a member of the team.**
`/OrgData/mes/MES by HAYASHI/` holds six files, three of them with Shift-JIS
names reading 追加MES4, 追加MES5 and 追加MES6 — *supplementary MES 4, 5 and 6*.

This pipeline's line is that what is on the disc is published, and that the line
is drawn at **reach** and only there. Here the decision needed no weighing,
because the product names the same person on screen:

```
/OrgData/stream/OPDS, the opening film
        "Directed by KENICHIRO HAYASHI"
        "Programmer MASAHIRO NODA"
```

**The directory publishes no identity the shipped game does not.** That is the
same structure the platform notes recorded on the fifth disc, where a build
machine's volume name carried a first name and the game's own credit sequence
carried the full one — and there, as here, no contact detail accompanies either.

The owner of the machine was asked and chose to publish the directory name
together with the cross-check rather than either alone.

## Reach, counted as a shape and never as a value

```
python tools/unowned.py _work/hauzer.bin --range 0 128299 --contacts
```

```
bytes                              262,758,400
distinct sectors                        65,501  (51.0530 %)
printable runs of >= 6                 408,961  holding 15,595,742 bytes (5.9354 %)

mail addresses            1 occurrence,  1 distinct, lengths 7..7
telephone-shaped         10 occurrences, 10 distinct, lengths 8..11
URL-shaped                0
postal-code-shaped        4 occurrences,  4 distinct, lengths 8..9
```

**The matched text is discarded inside the function and is not reachable from
any output path.** The count is publishable; the values are not, and that is why
the tool is written that way.

**And this document does not call these contact details.** They are shape
matches on a denominator of 262 megabytes, of which 93.6 are Cinepak and 45.4
are SDX2 — 116 megabytes of high-entropy data in which a seven-character
mail-shaped run and ten grouped-digit runs are what chance produces. A single
seven-character match over a quarter of a gigabyte is not distinguishable from
noise, and the honest report is the count with its denominator beside it, which
is what is printed above.

The platform notes' `[1 of 2]` explains why the number is small structurally
rather than luckily: **where personal data lives on a 3DO disc depends on the
music format.** A ProTracker module has 31 instrument-name slots of 22 bytes of
free text and a person will write in one. `M.K.` counts **zero** over this
pressing. Forty-five megabytes of AIFF-C and twenty-one of `SNDS` have nowhere
for anybody to write.

## User state — the collection's sixth answer to the same question

`nvram` counts 16 and `NVRAM` 11 over the pressing. Inside `/launchme`:

```
/nvram/another
/nvram/dummy
/nvram/dummy
/nvram/RH_HAUZERJ
/nvram/RH_HAUZERJ
```

**No file on the disc is user state. The save goes to the console's NVRAM**, at
a path the binary spells out, and `/OrgData/program/sramtools` — 68,108 bytes,
the studio's own binary and the one image on the disc whose relocation branch
lands on `ro + rw + 4` — is the utility that manages it.

`/OrgData/images/` holds `DontSram.img`, `_DontSram.img` and `NoMemory.img`, and
`/System/Programs/CHKNVRAM` is the SDK's own NVRAM checker. **Six discs, six
times the same answer**, and this is the second to give the literal save path
after the fifth disc's `/nvram/aloneX.save`.

`RH` reads as the studio's initials and `HAUZERJ` as the title plus the region
letter. **Neither is demonstrated by the object** and both are listed among the
unexpanded abbreviations in chapter 10.

## Protection

```
python tools/protscan.py _work/files --all-files
```

```
files searched  366     bytes searched  161,346,866

BoG_ 0   SafeDisc 0   SECUROM 0   securom 0   CMS16.DLL 0   LaserLok 0
CDCOPS 0   StarForce 0   TAGES 0   SETTEC 0   Macrovision 0

POSITIVE CONTROL: four zero bytes           339 files
```

**The zero measures the marker list and not the disc**, and this document says
so rather than reporting eleven zeros as a finding. Every one of those eleven
markers is a **PC CD-ROM protection product name** — SafeDisc, SecuROM,
LaserLok, StarForce, Tages, Alpha-ROM. None of them could appear on a 3DO disc
under any circumstances, because none of them was ever built for this platform.
The reasoning is copied from `3do-aloneinthedark-doc/docs/18` and it is copied
because it was right.

**The positive control fires on 339 files of 366**, so the tool is looking.

**This platform's own protection is a different thing entirely and all three
parts of it are present here:**

```
/signatures                335,872 bytes, at block 126,135   -- sixth disc, sixth
                                                                time, to the byte
/rom_tags +224             64 bytes = 512 bits, wholly different between the two
                           copies of the block
the signing pass           the +8 word of records 0x0d, 0x07, 0x10 and 0x05
                           patched between copy 0 and copy 1, and 0x0c and 0x02
                           left alone
```

**`/signatures` is 335,872 bytes on six discs of six**, which is 164 blocks and
is the SDK's fixed reservation. The platform notes' open question 7 asked
whether it is always that size; six of six is now the answer and the file's
*contents* differ on six of six.

The algorithm is still unnamed. What this disc adds is a sixth confirmation of
the size, a fifth confirmation that `/rom_tags` record `0x05`'s `+8` word is
`/signatures`' first block minus one — 126,134 against 126,135 — and a sixth
observation of 512 bits at a fixed offset in a block whose declared table is
128 bytes and whose real table is 192.

# 06 — the 77 `IMAG` images: a trap that has waited five discs, and did not fire

*Measure: 77 files begin `IMAG`, 11,830,940 bytes = 4.5026 % of the user area;
all 77 are 320 × 240 at 16 bits per pixel; the chunk chain closes to the last
byte on 77 of 77; `bytes_per_row × height == PDAT payload` on 77 of 77; and
the `pixel order` byte agrees with the measured order on 77 of 77.*

`IMAG` is the **first** disc's image descriptor. Four discs of five since have
not had one — the second had zero, the third had a single false positive inside
a Cinepak frame, the fourth used `ANIM` and the fifth used no platform
container at all. The platform notes therefore carry the chunk at `[1 of 3]` on
its counts and, more importantly, they carry a **trap** on it that has been
untestable since 1993:

> The trap stands **for the `IMAG` chunk**: on the first disc `pixel order`
> says LRform on 30 of 61 files and says the opposite on the other 31, and a
> decoder that reads it produces 31 wrong pictures. **Do not trust
> `pixel order`.**

**This disc has 77 of them.** This chapter tests the trap.

## Counting them, and why the count is 77 and not 76

```
python tools/imagwalk.py _work/files --census
```

```
files walked                        : 366
files beginning IMAG                : 77
  parsed                            : 77
  refused                           : 0
chunk chain closes to the last byte : 77 of 77
bytes_per_row x height == payload   : 77 of 77
distinct (w, h, bpp) shapes         : 1     ->  320 x 240, 16 bpp, on all 77
```

**The pre-briefing said 76 and it censused by name.** 75 files carry `.img`, one
carries `.IMG`, and the seventy-seventh is `/OrgData/images/MADO3`, which has
**no extension at all** and begins `IMAG` like the rest. The platform notes
already say what to do about that, from the fourth disc:

> **Census by first four bytes, never by name.**

Where they are:

```
/OrgData/isearch   49        /OrgData/images   23        /OrgData/search    2
/OrgData/window     2        /OrgData/menu      1
```

**And that closes `/OrgData/isearch` entirely.** The pre-briefing listed its 49
files, 7,528,252 bytes, 2.87 % of the pressing, as *no extension, no magic,
unopened*. They are 49 of these images and nothing else: `sea01.img` to
`sea22.img` and their variants, all `IMAG`, all 320 × 240.

## Two shapes of file, and four chunk types nobody has recorded

Sixty-six files are 153,636 bytes and eleven are 153,724. The difference is 88
bytes and it is four chunks the platform notes have never seen:

```
python tools/imagwalk.py _work/files/OrgData/images/mado.img
```

```
IMAG   at      0  len     28
CPYR   at     28  len     24     payload: "No Copyright"
KWRD   at     52  len     20     payload: "No KeyWord"
CRDT   at     72  len     20     payload: "No Credit"
DESC   at     92  len     24     payload: "No Description"
PDAT   at    116  len 153608
```

**`CPYR`, `KWRD`, `CRDT` and `DESC` are an image tool's metadata block, and on
all eleven files every field holds the tool's placeholder.** They obey the
platform's chunk rule — four printable characters, a big-endian length
including the eight-byte header, tiling to the last byte — which is why the
chain still closes on 77 of 77.

**This is also why `Copyright` counts 28 on this pressing** where it counts 2,
2, 2, 2 and 3 on the other five discs. Eleven of the occurrences are the word
`Copyright` used as a **field label whose value is "No Copyright"** — the exact
opposite of an assertion. Chapter 10 does that count properly.

## The trap, tested

The order is **measured and not read**. The method is the platform notes' own,
used there to settle the third disc's banner screen and the fifth disc's
full-screen pictures: render the payload under each candidate order and compare
**vertical roughness against horizontal roughness** over the whole picture. A
picture is smooth in both directions; a wrong row order shows up as vertical
roughness several times the horizontal.

```
gameover.img   V/H  linear 3.2604   lrform 0.5531   measured: lrform
mado.img       V/H  linear 10.0929  lrform 1.0992   measured: lrform
```

Over all 77:

```
the descriptor's pixel-order byte  : 1 on 77 files
THE ORDER AS MEASURED              : lrform on 77
files where the descriptor DISAGREES with the measurement : 0
```

**The trap did not fire.** On the first disc the field lied on 31 of 61 files;
here it tells the truth on 77 of 77. So the platform notes' line has to change
shape: the claim is not *the descriptor lies*, it is **the descriptor lies on
one of the two discs that have one**, which is `[1 of 2]` and is a much weaker
and much more useful statement than either disc alone gives.

**And the prescription does not change at all.** A field that is right on one
disc and wrong on another is a field you must measure, and this session
measured it before rendering anything.

## Then a person looked

The arithmetic closing is not the check; the platform notes are explicit that a
decode can be arithmetically perfect and produce something with nothing in it to
recognise. So one file was chosen that **must** look like something.

```
python tools/pixorder.py _work/files/OrgData/images/CopyRight.img \
       --offset 36 --size 320x240 --png _work/png/order_copyright.png
```

Five candidate orders side by side. Under `lr-pair` — the order both the
descriptor and the roughness test choose — the picture reads:

```
                        Doctor Hauzer
              (C)1994 Riverhill Soft Inc.
      (C)1994 Matsushita Electric Industrial Co.,Ltd.
                  PUSH "P" BUTTON!
```

Under `linear` it is the same text with every other row displaced.

**Three things fall out of that one picture, and none of them is about pixel
order.**

1. **The studio asserts copyright, and it does it in pixels.** `Riverhill`,
   `RIVERHILL` and `riverhill` all count **zero** over the whole 301,761,600-byte
   track. The platform notes' rule — *on this platform the studio's name is a
   picture* — now holds on six discs of six, and this is the first one where
   the picture is a formal copyright notice rather than a logo or a credit
   screen;
2. **Matsushita again.** The console's manufacturer is the fourth party the
   notes have found inside a Japanese font on two earlier discs. Here it is a
   co-holder of the copyright on the title screen of a Japanese disc;
3. **the year is 1994, and it is an independent check on the epoch.** The disc's
   `/rom_tags` type `0x0c` reads **1994-04-15** under the 1 January 1904 epoch
   the platform notes settled from `COMM` chunks. Under a 1900 epoch the same
   word reads **1990-04-19**, and a disc pressed in April 1990 cannot carry a
   1994 copyright notice. **The rendered art refutes the 1900 epoch from
   inside the object**, which is a third independent route to the same answer
   and the first one that came from a picture. It is not what the notes' open
   question 8 asked for — that asks for a disc whose pressing date is
   documented *outside* the object, and this disc does not have one either.

# 03 — the file system: a map that closes, and a fill that needs a fourth term

*Measure: 128,300 sectors attributed exactly once each, zero owned by nothing
and zero double-claimed; 4,896 sectors of `iamaduck` fill; and a fill
arithmetic that closes to 0.00 sectors once the file copies are counted.*

## Opera, on a sixth disc, with nothing changed in the reader

The disc is not ISO 9660 and `iso9660.py --vd` says so cleanly — `descriptors :
0` — and then **exits 0**, which is inherited defect twelve and is still
unfixed because fixing an inherited tool silently is worse than reporting it.

`opera.py`, written against the first disc, opened this one without a line
changed: 366 files, 32 directories, a negative control that still refuses
blocks 0 and 1, and a sector map that closes. Six discs, one 200-line reader.

**The one thing that did change is the environment.** Three filenames are
Shift-JIS and the reader's *output* dies on them under the default Windows
codepage. The format was never the problem.

## The map

```
python tools/sectormap3do.py _work/hauzer.bin --runs
```

```
file        79,010   61.5822 %
copy        43,970   34.2712 %     <- second and later copies of FILES
dir             40    0.0312 %
dircopy         84    0.0655 %
duck         4,896    3.8161 %
zero           300    0.2338 %
other            0    0.0000 %
            -------
            128,300  100.0000 %          double-claimed blocks: 0
```

**`other` is zero.** The fifth disc left 16,168 sectors owned by nothing and
broke a `[4 of 4]`; this one closes, so the mark is four of six on the closing
map and the fifth disc remains the single exception.

**`iamaduck` is back**, which the fifth disc did not have at all, so that mark
is four of six too.

## Counting the fill twice, which is the notes' own lesson in a new place

The platform notes insist that all-zero sectors be counted twice — once for the
map and once for the truth — because most of them are inside files. **The same
applies to the fill and nobody had checked.**

```
iamaduck over the whole track, sequentially, with an overlap   1,344,484
```

4,896 sectors of pure fill hold 4,896 × 256 = **1,253,376**. The other 91,108
are somewhere else. A per-sector census says where:

```
sectors containing iamaduck at all              5,481 of 128,300
  sectors that are 256 repetitions (pure fill)  4,896   <- the map's duck bucket
  sectors with a PARTIAL run                      585   holding 91,107
per-sector total                                        1,344,483
sequential total                                        1,344,484
difference: one match straddling a sector join                  1
```

**The 585 are blocks the file system owns.** They are the round-up slack in
files' last blocks and the space past `first_free_byte` in directory blocks —
space the builder allocated, never filled, and never overwrote, so the master's
fill is still showing through inside the index. **Zero occurrences of
`iamaduck` are inside any extracted file**, because `opera.py` truncates to
`byte_count` and the slack is past it.

So the honest pair of statements is: *4,896 sectors of this disc are mastering
fill*, and *5,481 sectors of this disc contain mastering fill*. Both are true
and only the first answers *what does no file own*.

## The fill arithmetic, and the term this disc adds

The notes turned the fill from a story into an arithmetic on the third and
fourth discs: the fill is the complement of the sectors the **file system**
uses, and the file system uses more sectors than the files use bytes. Three
terms closed it there. **Here it takes four, and the fourth is the object's
whole subject.**

```
how full                161,346,866 / 262,758,400            =  61.4050 %

round-up slack          79,010 - 161,346,866/2,048           =     227.35 sectors
the index               40 directories + 84 directory copies =     124
FILE SECOND COPIES                                           =  43,970      <- new
the zero tail past the declared volume                       =     300
                                                                --------
                                                                44,621.35

predicted fill  =  100 - 61.4050 - (44,621.35 / 128,300) x 100  =  3.8161 %
measured fill   =  4,896 / 128,300                              =  3.8161 %
                                                       difference  0.0000 points
                                                                   0.00 sectors
```

**0.00 sectors, on a fourth disc, with a term no previous disc could supply.**
That is worth more than a third confirmation would have been, because the rule
survived being given a case where the biggest term is one nobody had written
down: a disc that spends a third of itself on copies still satisfies *the fill
is what the file system does not use*, provided you count the copies as use.

## Where the builder stops

The notes' open question 10 was answered on the fifth disc: **the builder writes
up to the end of a run of root-directory copies and stops**, and what follows is
fill on four discs and the medium's previous contents on one.

This disc's root copies are single blocks at 85, 19675, 38475, 57690, 79779,
100363 and 109741 — the first layout of six that is not clustered — so there is
no *run* to end. The fill is not one region after a run of copies; it is
scattered. **The rule as stated does not apply to a disc whose root copies are
never adjacent**, and this disc neither confirms nor refutes it. That is worth
saying explicitly rather than counting it as a fifth confirmation, which is
what promoting a mark for silence would look like.

## The zero tail, and the two numbers that are one fact

```
blocks the volume declares    128,000        = 250 MiB exactly
sectors in the pressing       128,300
past the declared volume         300         contiguous at 128,000..128,299
all-zero user sectors          9,241         in 2,579 runs
```

**The 300 free sectors are exactly the 300 past the declared volume**, so on
this disc as on the fourth, "the zero tail" and "the undeclared sectors" are one
fact stated twice. The other **8,941 all-zero sectors are not free** — 6.97 %
of the pressing, and they are silence in the SDX2 music, transparent runs in the
cels and padding in the films, sitting inside blocks that files and their copies
own. A tool that counted zero sectors without asking who owned them would have
called 7.2027 % of this disc empty when 0.2338 % of it is.

## `/Disc label`, compared as the notes now require

```
/Disc label   132 bytes, type *lbl, entry type byte 6, at blocks 0 and 225
blocks 0 and 225 compared over all 2,048 bytes : 0 differing bytes
the word at +128, past a seven-copy list        : 00000000
block 0 at offset 132  : "duckiamaduckiamaduckiamaduck"
block 225 at offset 132: "duckiamaduckiamaduckiamaduck"
```

**Identical, which is what a disc with fill looks like.** The fifth disc's two
copies differed in 1,905 of 2,048 bytes because there was no fill to write after
byte 132. Here the fill is there and the comparison finds nothing — which is
the check working, at block 0, before anything else says so.

# 08 — the audio: one codec, and two thirds of it where no AIFF reader looks

*Measure: 61 AIFF-family files holding 46,058,073 bytes of sample data,
18:07.75; plus 21,553,152 bytes of SDX2 inside the eight films, 8:08.73; total
67,611,225 bytes = **25.7313 %** of the 262,758,400-byte user area.*

## The containers

```
python tools/aiffread.py _work/files
python tools/thesis3do.py _work/files 128300 128000
```

```
kind                files   SSND payload    running time
music, AIFF-C SDX2     12     45,410,350     17:09.71
effects, AIFF NONE     48        638,903      0:57.94
the SDK's sinewave      1          8,820      0:00.10
                       --     ----------     --------
                       61     46,058,073     18:07.75
```

**56 `.dsp` files are correctly refused** for having no `COMM` chunk. They are
`FORM 3INS` instrument patches for the audio folio and they are not audio — the
platform notes' warning that *forty-four per cent of what the audio reader opens
on a 3DO disc may not be audio* holds again, at 48 % here, and **the refusal is
the measurement**.

## The codec, derived from the header rather than assumed

The platform notes' rule is that SDX2 is exactly 2:1 and that the ratio must be
derived from `COMM` when the disc does not ship the same sound twice. This disc
does not, so it is derived:

```
for SDX2:  SSND payload == frames x channels x 1     on 12 of 12 music files
for PCM :  SSND payload == frames x channels x 2     on 49 of 49 others
```

Twelve files, one codec, no exceptions. **The music is 22,050 Hz sixteen-bit
stereo SDX2 and the effects are uncompressed eight-bit mono.** This is the
fourth 3DO disc of six to use SDX2.

## The two thirds nobody was counting

`thesis3do.py` reads `COMM` chunks. **It cannot see a `SNDS` stream**, and this
disc's films carry 21,553,152 bytes of sound in them — 16-bit, 22,050 Hz,
stereo, compression `SDX2`, declared in the `SNDS SHDR` sub-chunk and matching
the concatenated `SSMP` payloads on 8 of 8 (chapter 05).

```
AIFF and AIFF-C containers          46,058,073    17.5287 %  of the user area
SDX2 inside the eight films         21,553,152     8.2027 %
                                    ----------    ---------
ALL RECORDED SOUND                  67,611,225    25.7313 %
```

**That is the figure this repository publishes**, and the difference between it
and the AIFF-only number is **8.2027 points**. The fifth disc's session had to
make exactly this correction on exactly this column — its brief handed it
45.9737 % from `thesis3do.py` and the answer was 77.1890 % once the headerless
streams were counted. **Two sessions in a row, the same tool, the same column,
the same shape of error**, and this time it was caught before the column was
written rather than after.

Against the collection, by pressing date:

```
Crash 'n Burn      1993-09-09    0.3230 %
Doctor Hauzer      1994-04-15   25.7313 %
AD&D Slayer        1994-08-16   67.4093 %
Alone in the Dark  1994-12-19   77.1890 %
SSF2T              1995-01-10   86.2465 %
Wolfenstein 3D     1995-09-06   59.7896 %
```

**Second lowest of six**, and the reason is legible from the same accounting:
this disc spent 35.62 % of itself on moving pictures and 17.28 % on music, and
a disc cannot do both to the extent the middle four did.

## The Red Book question, on a sixth disc

```
python tools/thesis3do.py _work/files 128300 128000
```

```
the AIFF sound as CD-DA    191,879,753 bytes = 81,582 sectors = 24.4990 % of a CD
everything that is not it  115,266,434 bytes = 56,283 sectors
a hypothetical Red Book pressing            137,865 sectors = 41.4008 % of 333,000
                                                     ... so it WOULD have fitted
compression achieved by SDX2 against CD-DA                       4.1660 : 1
```

**It would have fitted, at 41.40 % of a 74-minute CD against the 38.53 % this
disc actually uses.** Six discs, six studios, twenty-four months, **zero Red
Book tracks**, and on this one capacity was free by nearly sixty per cent of a
CD.

**The constraint is the drive and this disc says so louder than the others.** A
single-speed drive delivers 153,600 bytes per second. This disc needs to stream
a Cinepak film and its soundtrack *at the same time* — the `SNDS` and `FILM`
chunks are interleaved, which is the whole point of the Data Streamer — and it
cannot serve a Red Book track and read data at once. The films are 35.62 % of
the pressing. A CD-DA track would have made 35.62 % of this disc unplayable.

## Sample rates, and what they rule out

```
music, 12 AIFF-C           22,050 Hz, 16-bit, stereo, SDX2   on 12 of 12
effects, 47 AIFF           11,025 Hz,  8-bit, mono,  NONE
effects, 1 AIFF            11,127 Hz,  8-bit, mono,  NONE  <- SAKEBI.AIFF
the SDK's sinewave.aiff    44,100 Hz, 16-bit, mono,  NONE
the films' sound           22,050 Hz, 16-bit, stereo, SDX2  on 7 of 7 with sound
```

**Sixty of the sixty-one files are 44,100 divided by two or by four. One is
not, and it is worth its own paragraph.** `/OrgData/effect/SAKEBI.AIFF` — a
scream, one second and six hundredths of it — declares **11,127 Hz**, and
11,127.27 is exactly half of 22,254.5454, which is the Macintosh family rate the
platform notes name. Forty-seven of its siblings in the same directory are at
11,025.

**That is a trace and it is not a proof, and the notes say why.** A resample
destroys this evidence in both directions, so a rate cannot establish where a
sound was made. What makes this one worth printing is the **asymmetry**: it is
one file of forty-eight in one directory, its neighbours were all normalised to
the CD family and it was not, and 3DO development was hosted on the Macintosh
Programmer's Workshop. On a disc where `foreign.py` finds **no file carrying a
foreign-architecture signature at all**, the only surviving fingerprint of
another machine is an eighty-bit float in one sound effect's `COMM` chunk.

## Eight-bit uncompressed, which is the platform's false economy

The platform notes' open question 16, written after the fifth disc and never
counted:

> **How much of the 3DO's SDX2 usage is a false economy?** SDX2 stores one
> signed byte per sample per channel; eight-bit PCM stores one byte per sample.
> **The two encodings cost identical bytes**, and one delivers eight more bits
> for free. Any disc that ships an eight-bit uncompressed file is throwing away
> eight bits for nothing, and nobody has counted how often that happens.

**This disc counts it, and it is the first data point the question has:**

```
files at 8 bits, codec NONE          48 of 61
their sample data                    638,903 bytes = 0.2432 % of the user area
the same bytes as 16-bit SDX2        638,903 bytes -- identical, to the byte
what was thrown away                 8 bits of resolution on 0.2432 % of the disc
```

**And the studio knew the codec**, because the same disc uses SDX2 on all twelve
music files and on all seven films with sound. The eight-bit effects are not an
oversight about compression; they are a decision to spend nothing on effects at
all, made by a studio that had the better encoder loaded in the same folio.

## Where personal data would live, and why it does not

The platform notes' `[1 of 2]`: *where personal data lives on a 3DO disc depends
on the music format*, because a ProTracker module has 31 instrument-name slots
of 22 bytes of free text each and a conversion credit fits in one.

```
M.K. over the whole 301,761,600-byte track : 0   (chance expectation 0.0703)
```

**No modules, so no comment fields.** Forty-five megabytes of AIFF-C and
twenty-one of `SNDS` have nowhere for a person to write, and the disc's one
piece of personal data is a directory name and a credit sequence instead
(chapter 11). Third disc of six with the same structural answer.

## The instrument bank, which is a clock

```
/System/Audio/dsp    56 files, 49,156 bytes, FORM 3INS on 56 of 56
```

Ordered by each disc's own `/rom_tags` date:

```
Crash 'n Burn      1993-09-09    53
Doctor Hauzer      1994-04-15    56
AD&D Slayer        1994-08-16    63
Alone in the Dark  1994-12-19    63
SSF2T              1995-01-10    63
Wolfenstein 3D     1995-09-06    77
```

**Six points, monotone non-decreasing, no inversion** — and this disc's 56 lands
exactly where its date says it should, between the launch title's 53 and the
1994-95 group's 63. The platform notes have four points on this series; this is
the sixth, and it is an independent confirmation of the pressing date from a
file count.

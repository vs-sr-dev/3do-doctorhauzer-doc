# 05 — the eight films: 35.62 % of the disc, and one of them needed four bytes skipped

*Measure: eight files beginning `SHDR`, 93,585,408 bytes = 35.6165 % of the
262,758,400-byte user area; 11,405 chunks; every chunk walked to the last byte
of every file; 21,553,152 bytes of SDX2 sound inside them, and the `SNDS`
header's declared sample total matched on 8 of 8.*

This is the largest use of the platform's Data Streamer this collection has
seen — bigger than the third disc's 11.6 megabytes and the fifth disc's 11.3
together, by a factor of four.

## The census

```
python tools/cvidmovie.py _work/files/OrgData/stream/<film> --census
python tools/streamaudit.py _work/files/OrgData/stream --census --resync \
       --user-area 262758400
```

```
file        bytes    chunks     FILM       SNDS       FILL      SSMP   geometry
EDDS     30,146,560   3,469  17,223,284  6,333,728  6,589,280 6,307,840  260x200
OPDS     27,918,336   3,924  15,307,476  7,649,104  4,961,488 7,624,704  300x160
MESDS    10,584,064   1,330   6,294,500  2,501,024  1,788,272 2,488,320  290x210
SLDS     10,551,296   1,018   6,732,704  1,737,744  2,080,580 1,722,368  290x210
TRDS      8,683,520     892   5,191,468  1,559,104  1,932,676 1,552,384  290x210
STDS      4,063,232     518   2,413,328    974,464    675,172   972,800  290x210
PADDS     1,146,880     105      86,552    893,264    166,796   884,736  320x240
GODS        491,520     149     380,104          0    111,148         0  260x200
```

**All eight declare compression `cvid`** in their `FHDR`, which is standard
Cinepak, and this document uses the public definition of Cinepak and says so.
The strip walk, the sub-chunk header convention and the relative-rectangle
rule all come from the platform notes, where they were derived on the third
disc, and every one of them holds here; that coverage arrived free and is
declared as free.

## The one that does not chain, and why it does now

`cvidmovie.py` stops on `TRDS` with `bad chain at 7995388`, having explained
7,995,388 of 8,683,520 bytes and leaving **688,132** it cannot account for.

The bytes at that offset are:

```
7,995,384:  0b 08 0d fc | 46 49 4c 4c | 46 49 4c 4d | 00 00 0f 78
                          F  I  L  L    F  I  L  M
```

**A bare `FILL` tag with no length field after it.** The next four bytes are
the `FILM` tag of the chunk that follows. Stepping four bytes and carrying on
chains **104 more chunks** to the file's last byte exactly:

```
resync at 7,995,388 :   0 chunks, stops at 7,995,388 of 8,683,520   breaks
resync at 7,995,392 : 104 chunks, stops at 8,683,520 of 8,683,520   CLOSES
```

**This is a defect on a retail pressing, not a defect in a reader.** Every
sector of the file passes its own EDC and both ECC parities — the whole track
does, 128,300 of 128,300 — so the four missing bytes were written that way by
whatever multiplexed the stream. `streamaudit.py --resync` performs the step
and **reports it on the line where it happens**; a tool that repaired the
stream silently would turn a defect on a pressing into a clean number.

**And the accounting says the same thing from the other end.** The pre-briefing
recorded an unexplained gap of 8,683,682 bytes between `/OrgData/stream`'s
directory size and what `account3do.py` charged to the Data Streamer. That gap
is not a mystery and it is not a format:

```
TRDS, which the walker refused entirely   8,683,520
stream.scp, which is a text file            + 162
                                          ---------
                                          8,683,682   exactly
```

## Everything closes, in both directions

With the resync, and reading the whole directory:

```
bytes in the eight films          93,585,408
bytes the chunks explain          93,585,408
unexplained                                0
stream.scp, plain text                 + 162
                                  ----------
/OrgData/stream, per the directory 93,585,570
```

**By tag, over the eight films:**

```
FILM  53,629,416   57.31 %      SNDS  21,648,432   23.13 %
FILL  18,305,412   19.56 %      SHDR       1,952    0.00 %
CTRL        192     0.00 %
```

**Nineteen and a half per cent of the largest thing on this disc is padding.**
`FILL` is the Data Streamer's alignment to the drive's read quantum, and it is
the price of being able to stream at all.

## The quantity encoded twice, and where it disagrees

The platform notes record that the Data Streamer stores its sample byte total
in a `SNDS SHDR` field and again as the concatenated `SSMP` payloads.

**`SSMP` payload == `SNDS SHDR` declaration on 8 of 8, difference zero** —
once `TRDS` is resynced. **Before the resync `TRDS` reported 1,362,144 against
a declared 1,552,384**, short by exactly 190,240 bytes, which is how the defect
first showed up in the arithmetic rather than in the walk.

**The frame count is NOT encoded twice on this disc, and that breaks a
`[2 of 2]`.** The notes carry: *`FHDR` declares 409 and 141, and the files hold
exactly 409 and 141 `FRME` chunks.* Here:

```
        FHDR declares   FRME measured
EDDS         313            2,149
OPDS         767            2,594
MESDS        525              848
GODS         131              131   equal
SLDS         585              585   equal
STDS         330              330   equal
PADDS         11               11   equal
```

**Four of seven equal, three not**, and the three that disagree are the three
longest films. The field is described and not named: on this disc `FHDR` +40 is
a number that is right on the short films and low on the long ones.

## The sound inside the films, which no AIFF reader can see

```
SNDS SSMP sample bytes  21,553,152 = 8.2027 % of the user area
format                  16-bit, 22,050 Hz, 2 channels, compression SDX2
running time            8:08.73 at one byte per sample per channel
```

**`thesis3do.py` reads `COMM` chunks and cannot see any of it**, which is
exactly the error the fifth disc's session had to correct on the same column.
The disc's total recorded sound is therefore

```
AIFF and AIFF-C containers   46,058,073   17.5287 %
inside the eight films       21,553,152    8.2027 %
                             ----------   ---------
ALL RECORDED SOUND           67,611,225   25.7313 %  of the user area
```

and **25.7313 % is the figure this repository publishes in the thesis column**,
against neighbours' 0.3230 %, 67.4093 %, 77.1890 %, 86.2465 % and 59.7896 %.
It is the second-lowest of six, and the reason is that this disc spent its
budget on pictures.

## What the films are

Frames were rendered and shown to the owner of the machine. The names decode,
and two of the eight prove their own expansion:

```
OPDS   the opening: the 1952 newspaper, the mansion, the title card
       "Doctor Hauzer", and the credits
GODS   131 frames of the words GAME OVER tumbling on black
PADDS  eleven frames of a Panasonic 3DO controller with the buttons
       labelled in Japanese and English -- the tutorial
MESDS  the prologue narration: Japanese prose, white on black, as VIDEO
SLDS   the approach to the mansion at night
STDS   a first-person walk to a door, and the door opening
EDDS   a cave, a shore, and a night sky -- the ending
TRDS   the film with the four-byte defect
```

**`OPDS` and `GODS` are self-proving.** `GODS` renders the literal words `GAME
OVER`, and `OPDS` renders the opening titles; with `DS` reading as *Data
Stream* — which is the platform's own name for the format — `GODS` is
*Game Over Data Stream* and `OPDS` is *OPening Data Stream*. `EDDS` follows as
*ENDing*, on the Japanese convention that pairs OP with ED, and that one is
supported by what it shows rather than proved by it. `PADDS` shows a pad.
`MESDS` shows messages. `SLDS`, `STDS` and `TRDS` are **not** demonstrated by
their contents and are left unexpanded; see chapter 16.

## The thing worth saying about `MESDS`

**Ten and a half megabytes — 4.03 % of the pressing — is Japanese prose
delivered as Cinepak video.** The text is white on black, it does not move, and
it is the game's own prologue. The disc has a font (`/OrgData/font/fontNew.bin`,
36,363 bytes) and it has a text renderer, because the in-game messages in
`/OrgData/mes/` are drawn from Shift-JIS at run time. For the prologue it did
not use either.

At 22,050 Hz stereo SDX2 the narration's sound is 2,488,320 bytes and the
pictures are 6,294,500. **Six megabytes of video to show text that is 12,995
bytes of Shift-JIS elsewhere on the same disc** — a ratio of about 484 to 1.
That is a choice about timing and about the voice track running under it, and
it is one of the clearest things this object says about what a 1994 studio
thought a CD was for.

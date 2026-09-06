# 12 — is it a clone of Alone in the Dark, and in what precise sense

*Measure: seven axes were proposed; **five close on both objects and are
published below**; two do not close and are omitted from the table on the
owner's own instruction, and named at the end so that the omission is visible.*

The owner of the machine asked this question and was specific about it: the
reference is **the 1992 MS-DOS original**, not the 3DO port. This chapter says
what can be measured, and declines to answer with an adjective.

## What the date settles before any axis is measured

```
Doctor Hauzer     /rom_tags 0x0c   ->  1994-04-15 11:30:33
Alone in the Dark /rom_tags 0x0c   ->  1994-12-19 16:12:01
```

**Eight months and four days.** Whatever these two discs share, **the 3DO port
of Alone in the Dark is not the source of it.** That is not an inference from
release years — it is two fields in two `/rom_tags` blocks under one epoch, and
the epoch is confirmed here three ways (chapters 06 and 09).

**The 1992 MS-DOS original is not in this collection.** What is available is the
3DO port, and the platform notes record that the PC game's data layout survived
that port intact: the `.PAK` archives (PKZIP with the per-entry headers
rewritten, 2,072 members), `OBJETS.ITD` (292 objects in 52-byte little-endian
records), the eight `ETAGE` floor archives, and 149 fixed-camera backgrounds at
320 × 250 in forty-sector blocks. **That is a partial proxy and every row below
says which object it measured.**

## The table

| axis | Alone in the Dark (3DO, 1994-12-19) | Doctor Hauzer (1994-04-15) |
|---|---|---|
| **byte order** | little-endian, the PC's, on a big-endian console | **big-endian, the console's**, on 33 of 33 rooms and 77 of 77 images |
| **graphics container** | none of the platform's — a raw 320 × 250 raster in a 40-sector block, and a raw 16-bit raster with no header | **all three of the platform's**: 77 `IMAG`, 6 `CCB `, 4 `ANIM`, and 1,157 cels whose two width encodings agree 1,157 of 1,157 |
| **the unit of space** | a **floor** — 8 `ETAGE` `.PAK` archives | a **room** — 33 `room*.bin`, each a 3-word big-endian offset table over four sections |
| **the script** | inside the `.PAK`, compressed, in a rewritten PKZIP | **plain Shift-JIS text**, 13 files, 99.9966 % valid pairs, in a directory named after the person who wrote it |
| **archive format** | 20 archives, 2,072 nameless members, PKZIP tails left in place | **none.** `BRGR` 4 and all four read as noise in context; no `PK`; no member table anywhere |

**Five axes, five answers, and all five point the same way: away from a port.**

## What each row is actually evidence of

**Byte order is the decisive one and it was measured first.** A port keeps its
source's byte order because rewriting every structure is the expensive part.
Alone in the Dark on the 3DO kept the PC's little-endian layout **on a
big-endian machine**, which is the signature of a port. Doctor Hauzer's first
word of `room001.bin` reads 12,896 big-endian — an offset inside a 179,844-byte
file — and 1,613,889,536 little-endian, which is nine thousand times the file.
On 33 of 33. **Nothing on this disc was laid out by a little-endian compiler.**

**The graphics containers say the same thing from the other end.** Alone in the
Dark used *none* of the platform's — its art is raw rasters the game blits
itself, because that is what the PC version did and the port did not change it.
This disc uses `IMAG`, `CCB ` and `ANIM` **at once**, which no other disc in the
collection does, and its cels satisfy the platform's own internal identity on
1,157 of 1,157. **A studio that writes to three of a platform's containers is
writing for that platform.**

**The script row is the one a reader will feel.** Alone in the Dark's text is
inside a compressed archive with the headers rewritten. This disc's is
`MESSAGE1.TXT`, openable, with room headers, in a directory called
`MES by HAYASHI`. **Two games with the same premise, and one of them shipped its
writing and the other buried it.**

## The two axes that do not close, and are therefore not in the table

The owner's instruction was that a row which does not close is omitted rather
than guessed at. Both omissions are named here so that the table cannot be
mistaken for a complete one:

**The object table.** Alone in the Dark has `OBJETS.ITD`: 292 objects in 52-byte
little-endian records. `/OrgData/item/` on this disc holds **two** files,
`ItemPol.bin` (23,324 bytes) and `ItemTex.bin` (46,404), and they hold **33
cels** between them — they are polygon and texture data, not a record table.
There is no file on this disc that reads as an object table with a fixed record
stride, and the equivalent structure has not been located. **What would close
it:** finding where the game stores an item's properties, which is probably
inside `/OrgData/macro/`'s 39 files and has not been derived.

**The actors.** Alone in the Dark has `LISTBODY` and `LISTANIM` inside its
`.PAK`s. `/OrgData/human/` holds nine files, of which `HumanPol.bin` (188,976 B)
and `HumanTex.bin` (63,452 B) carry **48 cels**, and the naming is exactly
parallel to `/OrgData/item/`. **That parallel is suggestive and it is not a
measurement**, because neither the record structure of `HumanPol.bin` nor the
count of distinct actors has been derived. **What would close it:** a record
stride in `HumanPol.bin` that divides 188,976 and yields a plausible actor
count.

## The honest answer

**On the five axes that close, this is not a port of Alone in the Dark and it is
not built from its data.** The byte order, the containers, the spatial unit, the
script's storage and the absence of an archive format are five independent
measurements and they do not have a single result in common with the other
object.

**What the measurements cannot reach is the resemblance the question is really
about** — a fixed-camera polygonal horror game set in one haunted house, with a
protagonist who explores rooms and solves object puzzles, released two years
after the game it is compared to. That resemblance is real, it is what put the
question on the table, and **no field on this disc encodes it.** It is a
resemblance of design, and the honest form of this chapter's answer is:

> **Structurally, no, on every axis that closes.** Doctor Hauzer is native 3DO
> code laying out native 3DO containers in the console's own byte order, and it
> arrives eight months before the port it is compared against. Whatever it took
> from Alone in the Dark, it took as an idea and not as a file format.

The owner has the other half of that answer, and it is the half that comes from
looking at the two games rather than at their bytes.

# Ultima Underworld NPC conversion backlog

This audit uses all nine mobile-object tables from the clean Japanese Rev 1 PlayStation disc. The companion CSV records each floor, archive offset, conversation ID, spawn and home tiles, initial link status, DOS record match, palette, and directional animation coverage. It includes hostile creatures and dormant records alongside conversational NPCs.

[Record-by-record audit](ultima-underworld-npc-conversion-backlog.csv) · [Atlas feasibility by DOS family](ultima-underworld-npc-atlas-feasibility.csv)

Of 657 PSX records, 550 are initially linked. The original goblin, lizardman, and rat preview verified DOS idle and walk for 70 linked records. At that checkpoint, 480 initially linked records used native PSX idle and walk, 100 other records had no enabled substitution, and seven qualified pending activation. The inventory and counts below describe that checkpoint. For the current early-floor coverage, see the [Levels 1–4 verification](named-dialogue-audit.md#levels-14-recurring-creature-preview).

The optional lizardman combat preview adds DOS stance, melee, retreat and death poses for 18 records. Other creature families retain native combat.

The cumulative preview passed 197 DuckStation floor transitions across all 56 directed pairs among Levels 1–8. The Level 8 menu cleared the rat atlas while open and restored it on resume. A separate entry into Level 9 verified native rendering was selected there. Repeated Level 9 travel remains unverified.

## Remaining models by type

In the floor column, the number after L identifies the dungeon level. Counts are for initially linked records. A DOS association identifies source art for that type. The CSV identifies individual record matches.

| PSX type | DOS asset | Palette | Active still native by floor | Dormant still native | Dormant eligible, untested |
| ---: | --- | ---: | --- | ---: | ---: |
| 64 | `rotgrub` | 0 | L1 × 2, L3 × 1, L6 × 2 | 1 | 0 |
| 65 | `slug` | 0 | L1 × 2, L6 × 2 | 1 | 0 |
| 66 | `bat` | 0 | L1 × 6, L3 × 2, L4 × 1, L6 × 2, L7 × 8 | 2 | 0 |
| 67 | `rat` | 0 | L1 × 4, L3 × 1, L4 × 2 | 3 | 0 |
| 68 | `spider` | 0 | L1 × 3, L2 × 1, L3 × 1 | 2 | 0 |
| 69 | `slug` | 1 | L1 × 2, L2 × 9, L3 × 1, L4 × 1, L6 × 2 | 1 | 0 |
| 71 | `graygob` | 0 | L1 × 3 | 0 | 0 |
| 72 | `rat` | 1 | L1 × 1, L2 × 3, L3 × 3, L4 × 3, L5 × 3, L7 × 1 | 1 | 2 |
| 73 | `bat` | 1 | L1 × 1, L4 × 1, L6 × 2 | 1 | 0 |
| 74 | `skela` | 0 | L1 × 1, L2 × 3, L3 × 3, L4 × 4, L5 × 8, L6 × 2 | 3 | 0 |
| 75 | `imp` | 0 | L6 × 1 | 5 | 0 |
| 77 | `gngob32` | 2 | — | 0 | 1 |
| 78 | `gngob32` | 3 | — | 1 | 4 |
| 79 | `batskull` | 0 | L9 × 26 | 1 | 0 |
| 80 | `graygob` | 1 | L1 × 3, L2 × 1, L7 × 4 | 0 | 0 |
| 81 | `imp` | 1 | L3 × 1, L4 × 3, L6 × 2, L8 × 14 | 5 | 0 |
| 82 | `rotgrub` | 1 | L2 × 4, L3 × 1, L4 × 1, L5 × 6, L6 × 4, L8 × 7 | 5 | 0 |
| 83 | `spider` | 1 | L1 × 1, L2 × 3, L3 × 2, L4 × 8, L8 × 3 | 4 | 0 |
| 84 | `dwarf32` | 0 | L2 × 12 | 0 | 0 |
| 86 | `dwarf32` | 1 | L2 × 2, L7 × 2 | 0 | 0 |
| 87 | `Lurk` | 0 | L1 × 3, L2 × 2, L3 × 11, L4 × 1, L7 × 1 | 0 | 0 |
| 90 | `fight32` | 0 | L1 × 5, L4 × 2 | 1 | 0 |
| 91 | `hedless` | 0 | L2 × 2, L3 × 1, L4 × 5, L5 × 3, L6 × 4, L8 × 9 | 12 | 0 |
| 92 | `spider` | 2 | L3 × 1, L4 × 2, L5 × 6, L6 × 6, L7 × 1, L8 × 5 | 12 | 0 |
| 93 | `femfite` | 0 | L3 × 3, L4 × 2 | 2 | 0 |
| 94 | `femfite` | 1 | L3 × 1, L4 × 2 | 0 | 0 |
| 95 | `fight32` | 3 | L4 × 2 | 0 | 0 |
| 96 | `troll` | 0 | L4 × 5 | 2 | 0 |
| 97 | `ghost` | 0 | L3 × 1, L5 × 5, L6 × 1, L7 × 1, L8 × 5 | 5 | 0 |
| 98 | `fight32` | 1 | L2 × 1, L4 × 4 | 1 | 0 |
| 99 | `ghoul` | 0 | L5 × 4 | 0 | 0 |
| 100 | `ghost` | 1 | L5 × 2 | 1 | 0 |
| 101 | `ghost` | 2 | L5 × 2 | 0 | 0 |
| 102 | `gazer` | 0 | L2 × 1, L3 × 1, L4 × 1, L5 × 1, L6 × 1, L7 × 2, L8 × 2 | 3 | 0 |
| 103 | `wiza` | 0 | L6 × 2 | 0 | 0 |
| 104 | `fight32` | 2 | L3 × 1, L4 × 1, L7 × 1, L8 × 1 | 1 | 0 |
| 105 | `ghoul` | 1 | L6 × 2 | 0 | 0 |
| 106 | `wizb` | 0 | L3 × 1, L4 × 2, L5 × 1, L6 × 2 | 0 | 0 |
| 107 | `femwiz` | 0 | L5 × 1, L6 × 2 | 0 | 0 |
| 108 | `wiza` | 1 | L6 × 3, L7 × 2 | 0 | 0 |
| 109 | `wiza` | 2 | L6 × 2, L7 × 1 | 0 | 0 |
| 110 | `ghoul` | 2 | L5 × 2, L8 × 1 | 1 | 0 |
| 111 | `troll` | 2 | L4 × 2, L6 × 1, L7 × 9, L8 × 1 | 1 | 0 |
| 112 | `troll` | 1 | L4 × 1, L6 × 1 | 1 | 0 |
| 113 | `ghost` | 3 | L3 × 1, L5 × 1, L7 × 3, L8 × 4 | 2 | 0 |
| 114 | `golem` | 0 | L2 × 1, L7 × 3 | 2 | 0 |
| 115 | `wizb` | 1 | L6 × 1 | 0 | 0 |
| 116 | `Lurk` | 1 | L3 × 3, L4 × 1, L7 × 7 | 1 | 0 |
| 117 | `shadow` | 0 | L3 × 2 | 1 | 0 |
| 118 | `reaper` | 0 | L3 × 1, L4 × 1, L5 × 2, L7 × 1, L8 × 5 | 3 | 0 |
| 119 | `golem` | 1 | L6 × 1, L8 × 3 | 2 | 0 |
| 120 | `fire` | 0 | L6 × 1, L7 × 10, L8 × 8 | 8 | 0 |
| 121 | `golem` | 2 | L3 × 1, L8 × 1 | 0 | 0 |
| 122 | `wisp` | 0 | L4 × 1, L8 × 1 | 0 | 0 |
| 123 | `tybal` | 0 | L7 × 1 | 0 | 0 |
| 124 | `demon` | 0 | L9 × 1 | 1 | 0 |
| 125 | `litening` | 0 | L9 × 28 | 0 | 0 |
| 126 | `eye` | 0 | L9 × 15 | 1 | 0 |

## Completed lizardman batch

The lizardman family uses three palettes of the DOS `lizman` artwork. All 18 linked PSX records have an individual DOS match and source art for all eight idle and walk views. Level 3 contains eight type 85, six type 88, and three type 89 records. Level 4 contains one type 89 record. All 18 were verified at their native records through controlled DuckStation render calls.

## Source-art checks for other families

The Xcode exporter attempted idle and walk atlases for all 63 PSX creature types. It exported both for 58. Types 84 and 86 (dwarves) share one DOS frame whose declared stream ends with one pixel undecoded. Type 91 (headless) has two walk frames with incomplete declared streams, with one and 43 pixels undecoded. These types remain native while their DOS output is investigated. Types 125 and 126 have no directional DOS walk slots.

## Level 8 rat batch

All 20 initially linked type 72 rats on Level 8 use the second DOS rat palette for idle and walk. Two additional unlinked type 72 records on Level 8 meet the substitution rule. Type 67 and type 72 on earlier floors still use native PSX visuals.

## Remaining linked records by floor

Level 1 × 37, Level 2 × 45, Level 3 × 45, Level 4 × 59, Level 5 × 47, Level 6 × 49, Level 7 × 58, Level 8 × 70, Level 9 × 70.

## Measured candidates for a later batch

These combinations fit the indicated texture dimensions in an offline packing check. Each family still needs its own palette selection and verified native VRAM ownership on that floor.

| Candidate area | Initially linked records in the packing check | DOS families |
| --- | ---: | --- |
| Level 6, two 256 × 248 4-bit pages | 30 | Male wizards, female wizards, spiders, bats, slugs, rotworms, gazer |
| Level 8, one additional 256 × 248 4-bit page | 24 | Rotworms, fire elementals, wisp, spiders |
| Level 8, one additional 256 × 248 4-bit page | 25 | Ghosts, rotworms, wisp, spiders |

The Level 6 layouts leave the current preview’s other floor atlases independent. The Level 8 layouts would share the floor with the existing rat renderer. Fire, wisps, and ghosts need a dedicated opacity and lighting comparison before selecting a draw mode.

The three incomplete DOS bitstreams are dwarf animation page `CR33PAGE.N01` frame 20 and headless page `CR24PAGE.N01` frames 29 and 31. Their declared compressed lengths end next to later frame headers. The existing exporter stops at those declared boundaries. This audit leaves their tails and the corresponding PSX models for a separate comparison against what DOS displays.

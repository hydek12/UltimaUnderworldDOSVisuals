# Ultima Underworld critter inventory

The [record-by-record inventory](ultima-underworld-npc-conversion-backlog.csv) covers all 657 mobile creature and NPC records in the clean Japanese Rev 1 archive. It compares the default release Track 1 (`78427bb7dea91c18fc2ca345865983a2ad6cc642`) with the dedicated-bank combat preview (`619b7b76837d008690679e3c9812a0510991154b`). The inventory reads the resident bank grids, palette registrations, and combat tables from the built tracks.

Each record is checked at two camera cells, the archived spawn tile and one tile west. Directional coverage is identical in the two builds. Both cells register DOS art for **633 records** and one cell registers it for **24 records**. All 24 are initially linked in the archive. The two-cell check measures configured coverage near the spawn. It leaves camera visibility, reachable viewpoints, actors that move, and actual gameplay draws to the [encounter audit](named-dialogue-audit.md).

| Level | Records | Archive-noninitial | DOS in both views | DOS in one view | Source action candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 56 | 6 | 51 | 5 | 33 |
| 2 | 57 | 8 | 54 | 3 | 24 |
| 3 | 74 | 12 | 74 | 0 | 31 |
| 4 | 70 | 10 | 69 | 1 | 26 |
| 5 | 59 | 9 | 59 | 0 | 24 |
| 6 | 60 | 11 | 56 | 4 | 33 |
| 7 | 94 | 24 | 88 | 6 | 58 |
| 8 | 115 | 25 | 110 | 5 | 42 |
| 9 | 72 | 2 | 72 | 0 | 0 |
| Total | 657 | 107 | 633 | 24 | 271 |

## Remaining checks

- **Directional coverage at bank boundaries.** Filter for `preview_directional_views=1` to get all 24 records with their bank names and coordinates. The largest groups are Level 7 green goblins (five), Level 8 rats (three), and Level 6 bats (two). A neighbouring bank may already serve another family, so confirm visibility and bank ownership in-game before changing its grid cells.
- **Fixed combat and special actions.** The preview maps at least one fixed DOS action at a sampled view for 322 records, including slot `0d` for 128. There are 271 records across 37 types with one or more decodable source slots missing from a view that already registers their directional art. Fire elementals (27 records) and spiders (26 type-92 records, plus other variants) are the largest groups. Slot `0d` appears in the source for 156 of the candidates. Check whether the original PSX AI can select the corresponding action before mapping it. The Level 6 warren Ghost is an intentional exception and uses native combat. The DOS export has no mapped fixed combat slots for types 79, 125, and 126.
- **Native activation.** Both sampled views already register DOS directional art for all 107 archive-noninitial records. The earlier native tile-chain trace found 44 already linked on floor load and identified create traps for another 60 records. Two Level 7 fire elementals share a type and spawn coordinate and need record-specific evidence. The remaining record, the Level 3 green goblin at (35, 62), was spawned by controller-driven rest. A create-trap entry identifies a candidate trigger and can include calls exercised with the debugger. The complete ordinary gameplay trigger chain still needs verification where the encounter audit lacks it.

## Regenerate the inventory

Run `audit-npcs.py --psx-inventory` with the local DOS installation and the clean Japanese Rev 1 `DATA/AVATAR` archive. Export the DOS action manifests separately for types 64–127 using `UnderworldVisuals export-mixed-combat DOS_ROOT TYPE MANIFEST_DIR/type-TYPE`. Redirect each export's standard error to `MANIFEST_DIR/type-TYPE.err` so the audit can distinguish an explicit missing-slot message from an unavailable manifest.

```sh
python3 audit-critter-banks.py records.csv release-track-1.bin combat-track-1.bin \
  --dos-actions MANIFEST_DIR --dormant-audit dormant-audit.log \
  > docs/ultima-underworld-npc-conversion-backlog.csv
```

The optional dormant audit input is the earlier local DuckStation tile-chain log with `ACTOR` lines. Without it the inventory reports the archive marker and the documented controller-rest result. Action values in the CSV are hexadecimal. A blank action mapping means the sampled bank has no mapped fixed action for that actor. Source action candidates list decodable slots absent from at least one sampled view with a DOS palette. They exclude the directional registration gaps.

## Earlier atlas feasibility measurements

These combinations fit the indicated texture dimensions in an offline packing check. Each family still needs its own palette selection and verified native VRAM ownership on that floor.

| Candidate area | Initially linked records in the packing check | DOS families |
| --- | ---: | --- |
| Level 6, two 256 × 248 4-bit pages | 30 | Male wizards, female wizards, spiders, bats, slugs, rotworms, gazer |
| Level 8, one additional 256 × 248 4-bit page | 24 | Rotworms, fire elementals, wisp, spiders |
| Level 8, one additional 256 × 248 4-bit page | 25 | Ghosts, rotworms, wisp, spiders |

The Level 6 layouts leave the current preview’s other floor atlases independent. The Level 8 layouts would share the floor with the existing rat renderer. Fire, wisps, and ghosts need a dedicated opacity and lighting comparison before selecting a draw mode.

The three incomplete DOS bitstreams are dwarf animation page `CR33PAGE.N01` frame 20 and headless page `CR24PAGE.N01` frames 29 and 31. Their declared compressed lengths end next to later frame headers. The existing exporter stops at those declared boundaries. This audit leaves their tails and the corresponding PSX models for a separate comparison against what DOS displays.

# Ultima Underworld critter inventory

The [record-by-record inventory](ultima-underworld-npc-conversion-backlog.csv) covers all 657 mobile creature and NPC records in the clean Japanese Rev 1 archive. It compares the default release Track 1 (`e29e66fb895387c304b4c47c945e2876b24c87a9`) with the dedicated-bank combat preview (`a7573c30fbd148136314ead74e799bcd6dd06506`). The inventory reads the resident bank grids, palette registrations, and combat tables from the built tracks.

Each record is checked at two camera cells, the archived spawn tile and one tile west. Directional coverage is identical in the two builds. Both cells register DOS art for **646 records** and one cell registers it for **11 records**. All 11 are initially linked in the archive. The two-cell check measures configured coverage near the spawn. It leaves camera visibility, reachable viewpoints, actors that move, and actual gameplay draws to the [encounter audit](named-dialogue-audit.md).

| Level | Records | Archive-noninitial | DOS in both views | DOS in one view | Source action candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 56 | 6 | 51 | 5 | 33 |
| 2 | 57 | 8 | 54 | 3 | 24 |
| 3 | 74 | 12 | 74 | 0 | 31 |
| 4 | 70 | 10 | 69 | 1 | 26 |
| 5 | 59 | 9 | 59 | 0 | 24 |
| 6 | 60 | 11 | 58 | 2 | 33 |
| 7 | 94 | 24 | 94 | 0 | 47 |
| 8 | 115 | 25 | 115 | 0 | 31 |
| 9 | 72 | 2 | 72 | 0 | 0 |
| Total | 657 | 107 | 646 | 11 | 249 |

## Level 8 boundary coverage

The three west approach cells for the headless at (12, 3) and rats at (6, 22) and (26, 61) now select the existing ghosts, rats, and headless bank. In the built-track audit, all three gained directional coverage in the west approach and the combat preview registered DOS slots `00 01 02 03 07 0c` there. The ghost at (10, 3) retained its directional registration and gained the mixed bank’s fixed poses at its spawn. The new menu preview differs from the previous menu preview in 16 copies of the same Level 8 data sector. All four CHD tracks passed byte-for-byte readback. In DuckStation, the preview loaded the `test` memory-card save and the native renderer submitted DOS sprite quads from bank 15 at all three west approaches. The probe checked the texture coordinates and palette for each draw after placing the camera with the debugger. Controller-driven approaches and combat at these boundaries remain open.

## Remaining Level 8 approaches

The rat at (26, 7) now shares the west approach with the fire elemental bank. The imp at (8, 61) uses a mixed bank that carries the nearby headless and ghost as well. The imp and headless share an 8-bit texture page and the ghosts use a 4-bit page. The built-track audit now registers DOS directional sprites in both sampled views for all 115 Level 8 records. All previously mapped action slots were retained, and the rat and imp gained DOS action mappings on their west approaches.

In live DuckStation gameplay, the rat used its DOS walk frame from camera tile (25, 7) in bank 12 with palette `0x7e58`. The imp used its DOS idle frame from (7, 61) in bank 14 with palette `0x7e18`. The probe also matched the expected frames and palettes for the fire elemental at (22, 5), headless at (6, 60), and ghost at (9, 60). The debugger placed the camera, and the game selected the poses.

## Level 7 troll and green goblin bank

The Level 7 troll bank uses one texture page for the two troll variants and a second page for green goblins. This pass kept its room assignments. The built-track audit gained west-approach directional coverage for goblins at (22, 5), (8, 30), (2, 34), and (28, 57). Both troll variants retain their previous directional coverage. The combat preview maps goblin slots `01 02 03 07 0c` and troll slots `00 01 02 03 07 0c 0d` when the mixed bank is active. The DOS map marks the west sample cell for (2, 34) as solid, so the registration at that sample is build evidence only.

DuckStation submitted the expected DOS texture coordinates and palettes for the other three goblins and the troll at (24, 2) with the camera placed by the debugger. This checked directional sprites. Game-selected combat poses and controller-driven approaches still need verification. The release builder verified the xdelta round-trip and all four CHD tracks and CUE indexes.

## Remaining Level 7 approaches

The green goblin at (18, 8) now has DOS sprites in the west approach, where the existing lurker rooms use a mixed bank. The bank preserves lurker directional sprites and native lurker combat, and adds goblin slots `01 02 03 07 0c`. The troll at (6, 29) now uses the existing troll-and-goblin bank at the west approach. The goblin at (5, 29) keeps DOS coverage in the reassigned cell. All 94 Level 7 records register DOS directional sprites in both sampled views. The full audit found no directional coverage losses and retained all previously mapped action slots.

In live DuckStation gameplay, the green goblin at (18, 8) rendered from camera tile (17, 9) with bank 8 and palette `0x7e98`. The troll at (6, 29) rendered from (5, 29) with bank 5 and palette `0x7e18`. The nearby lurker at (15, 9) and goblin at (5, 29) also rendered correctly. The debugger placed the camera, and the game selected all four idle poses. The probe checked the exact DOS texture coordinates and palette for each draw.

## Level 6 bat approaches

The bats at (40, 50) and (40, 52) now have DOS idle and walk sprites in the existing Academy imp bank. The bank uses separate texture pages for imps and bats. The room grid is identical, and the audit confirmed that all previously mapped imp action slots remain available. Bats use native combat in this bank. The change applies to the Slasher combat preview and cumulative profiles based on it.

In live DuckStation gameplay, both bats drew the exact DOS idle frame and palette `0x7ed8` from camera tiles (39, 50) and (39, 52) in bank 7. The nearby imp at (37, 50) also drew the expected idle frame with its own palette, `0x7e58`. The debugger placed the camera, and the game selected the poses.

## Remaining checks

- **Directional coverage at bank boundaries.** Filter for `preview_directional_views=1` to get all 11 records with their bank names and coordinates. Level 6 still has a slug at (16, 51) on a troll approach and an imp at (36, 52) on a default-bank approach. A neighbouring bank may already serve another family, so confirm visibility and bank ownership in-game before changing its grid cells.
- **Fixed combat and special actions.** The preview maps at least one fixed DOS action at a sampled view for 351 records, including slot `0d` for 150. There are 249 records across 37 types with one or more decodable source slots missing from a view that already registers their directional art. Spiders (26 type-92 records, plus other variants) remain among the largest groups. Slot `0d` appears in the source for 135 of the candidates. Check whether the original PSX AI can select the corresponding action before mapping it. The Level 6 warren Ghost is an intentional exception and uses native combat. The DOS export has no mapped fixed combat slots for types 79, 125, and 126.
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

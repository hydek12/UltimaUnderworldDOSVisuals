# Ultima Underworld critter inventory

The [record-by-record inventory](ultima-underworld-npc-conversion-backlog.csv) covers all 657 mobile creature and NPC records in the clean Japanese Rev 1 archive. It compares the default release Track 1 (`691fea5eaf8d6925c170ed40fe35dd9a69709d0f`) with the dedicated-bank combat preview (`2895f48350a195d396015f515216b4c5718e1d63`). The inventory reads the resident bank grids, palette registrations, and combat tables from the built tracks.

Each record is checked at two camera cells, the archived spawn tile and one tile west. Directional coverage is identical in the two builds. Both cells register DOS art for **all 657 records**. The two-cell check measures configured coverage near the spawn. It leaves camera visibility, reachable viewpoints, actors that move, and actual gameplay draws to the [encounter audit](named-dialogue-audit.md).

| Level | Records | Archive-noninitial | DOS in both views | DOS in one view | Source action candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 56 | 6 | 56 | 0 | 33 |
| 2 | 57 | 8 | 57 | 0 | 24 |
| 3 | 74 | 12 | 74 | 0 | 31 |
| 4 | 70 | 10 | 70 | 0 | 26 |
| 5 | 59 | 9 | 59 | 0 | 23 |
| 6 | 60 | 11 | 60 | 0 | 33 |
| 7 | 94 | 24 | 94 | 0 | 34 |
| 8 | 115 | 25 | 115 | 0 | 31 |
| 9 | 72 | 2 | 72 | 0 | 0 |
| Total | 657 | 107 | 657 | 0 | 235 |

## Level 8 boundary coverage

The three west approach cells for the headless at (12, 3) and rats at (6, 22) and (26, 61) now select the existing ghosts, rats, and headless bank. In the built-track audit, all three gained directional coverage in the west approach and the combat preview registered DOS slots `00 01 02 03 07 0c` there. The ghost at (10, 3) retained its directional registration and gained the mixed bank’s fixed poses at its spawn. The new menu preview differs from the previous menu preview in 16 copies of the same Level 8 data sector. All four CHD tracks passed byte-for-byte readback. In DuckStation, the preview loaded the `test` memory-card save and the native renderer submitted DOS sprite quads from bank 15 at all three west approaches. The probe checked the texture coordinates and palette for each draw after placing the camera with the debugger. Controller-driven approaches and combat at these boundaries remain open.

## Remaining Level 8 approaches

The rat at (26, 7) now shares the west approach with the fire elemental bank. The imp at (8, 61) uses a mixed bank that carries the nearby headless and ghost as well. The imp and headless share an 8-bit texture page and the ghosts use a 4-bit page. The built-track audit now registers DOS directional sprites in both sampled views for all 115 Level 8 records. All previously mapped action slots were retained, and the rat and imp gained DOS action mappings on their west approaches.

In live DuckStation gameplay, the rat used its DOS walk frame from camera tile (25, 7) in bank 12 with palette `0x7e58`. The imp used its DOS idle frame from (7, 61) in bank 14 with palette `0x7e18`. The probe also matched the expected frames and palettes for the fire elemental at (22, 5), headless at (6, 60), and ghost at (9, 60). The debugger placed the camera, and the game selected the poses.

## Level 7 troll and green goblin bank

The Level 7 troll bank uses one texture page for the two troll variants and a second page for green goblins. This pass kept its room assignments. The built-track audit gained west-approach directional coverage for goblins at (22, 5), (8, 30), (2, 34), and (28, 57). Both troll variants retain their previous directional coverage. The combat preview maps goblin slots `01 02 03 07 0c` and troll slots `00 01 02 03 07 0c 0d` when the mixed bank is active. The DOS map marks the west sample cell for (2, 34) as solid, so the registration at that sample is build evidence only.

DuckStation submitted the expected DOS texture coordinates and palettes for the other three goblins and the troll at (24, 2) with the camera placed by the debugger. This checked directional sprites. Game-selected combat poses and controller-driven approaches still need verification. The release builder verified the xdelta round-trip and all four CHD tracks and CUE indexes.

## Remaining Level 7 approaches

The green goblin at (18, 8) now has DOS sprites in the west approach, where the existing lurker rooms use a mixed bank. The bank preserves lurker directional sprites and native lurker combat, and adds goblin slots `01 02 03 07 0c`. The troll at (6, 29) now uses the existing troll-and-goblin bank at the west approach. The goblin at (5, 29) keeps DOS coverage in the reassigned cell. All 44 Level 7 records register DOS directional sprites in both sampled views. The full audit found no directional coverage losses and retained all previously mapped action slots.

In live DuckStation gameplay, the green goblin at (18, 8) rendered from camera tile (17, 9) with bank 8 and palette `0x7e98`. The troll at (6, 29) rendered from (5, 29) with bank 5 and palette `0x7e18`. The nearby lurker at (15, 9) and goblin at (5, 29) also rendered correctly. The debugger placed the camera, and the game selected all four idle poses. The probe checked the exact DOS texture coordinates and palette for each draw.

## Level 6 bat approaches

The bats at (40, 50) and (40, 52) now have DOS idle and walk sprites in the existing Academy imp bank. The bank uses separate texture pages for imps and bats. The room grid is identical, and the audit confirmed that all previously mapped imp action slots remain available. Bats use native combat in this bank. The change applies to the Slasher combat preview and cumulative profiles based on it.

In live DuckStation gameplay, both bats drew the exact DOS idle frame and palette `0x7ed8` from camera tiles (39, 50) and (39, 52) in bank 7. The nearby imp at (37, 50) also drew the expected idle frame with its own palette, `0x7e58`. The debugger placed the camera, and the game selected the poses.

## Remaining Level 6 approaches

The slug at (16, 51) now uses the default Academy bank from its west approach. The imp at (36, 52) uses the mixed imp and bat bank from its west approach, where the bat at (35, 53) retains DOS coverage. The built-track audit found exactly two changed camera cells and no lost directional or action mappings. All 60 Level 6 records now have DOS directional sprites in both sampled views. The imp gained its existing DOS combat and casting slots at the west approach.

In live DuckStation gameplay, the slug drew the exact DOS idle frame and palette `0x7f98` from (15, 51) in bank 0. The imp drew the exact DOS idle frame and palette `0x7e58` from (35, 53) in bank 7. The nearby bat also drew the expected DOS idle frame and palette `0x7e98` from (35, 54) in bank 7. The debugger placed the camera, and the game selected each pose.

## Level 1 goblin approaches

Three green goblins at (54, 38), (52, 52), and (46, 55) now use the default DOS shade-map bank from the west. The gray goblins at (2, 57) and (52, 59) use a shared gray and green bank on their affected approaches. The bank packs gray sprites at 13/16 texture scale and green sprites at 9/16 to fit both families in VRAM. The built-track audit found five changed camera cells and retained all previously mapped actions. All 56 Level 1 records now have DOS directional sprites in both sampled views.

The live DuckStation check matched the DOS texture coordinates and palettes for all five targets. From (53, 38), the green goblin at (54, 38) drew its walk frame with palette `0x7a1e`. The green goblins at (52, 52) and (46, 55) drew idle frames from (51, 52) and (45, 55) with palette `0x7a1a`. The gray goblins at (2, 57) and (52, 59) drew idle frames from (2, 56) and (51, 59) with palettes `0x7e18` and `0x7e58`. Both nearby green goblins at (4, 56) and (51, 58) also drew their expected idle frames in the shared bank. The debugger placed the camera, and the game selected all seven poses.

## Remaining Level 2 and Level 4 approaches

On Level 2, the green goblins at (54, 55) and (60, 55) use the default goblin bank from the west. The gray goblin at (56, 60) uses a gray and green bank from the west. The shared bank packs gray sprites at 13/16 and green sprites at 9/16 texture scale.

On Level 4, the bat at (32, 45) gains a west approach in a bank it shares with the lizardman at (31, 44). The shared bank retains the lizardman’s DOS combat slots and the bat’s native depth-based lighting. The built-track audit confirmed that exactly four camera cells changed across both floors, with all previously mapped actions retained.

In live DuckStation gameplay, the green goblins at (54, 55) and (60, 55) drew the exact DOS idle frames from camera tiles (52, 55) and (59, 55) using palette `0x7f1a`. The gray goblin drew its idle frame from (55, 61) using palette `0x7e58`. The Level 4 bat drew its idle frame from (31, 45) with palette `0x7e18`. The neighboring green goblin and lizardman also drew their expected DOS frames and palettes. The debugger placed the camera, and the game selected the poses.

## Dedicated fire elemental combat

The Level 5 and 7 fire elemental banks now carry DOS slots `00 01 02 03 07 0c 0d` for all 14 records that use those banks in the audit. The existing room grid and other combat mappings were retained.

In DuckStation, the Level 7 elemental at (51, 40) selected action `01` and drew all five DOS phases before the native damage dispatcher identified it as the source. On Level 5, invoking the original create trap with the debugger spawned the dormant elemental at (19, 50). After it spawned, its AI selected action `03` and drew all five DOS phases. The debugger staged the approaches and assigned the player as the AI target. The game selected the actions and advanced their phases. The ordinary gameplay trigger for the Level 5 trap remains open.

A separate replay used live actor projections from both banks and staged the seven action values across front and rear views and three animation phases. Each floor produced 54 matching DOS sprite packets and six expected native fallbacks for an unmapped action. The checks compared palette, texture page, and texture coordinates, and verified that native fallbacks preserved the packet and draw order.

## Remaining checks

- **Fixed combat and special actions.** The preview maps at least one fixed DOS action at a sampled view for 365 records, including slot `0d` for 164. There are 235 records across 37 types with one or more decodable source slots missing from a view that already registers their directional art. Spiders (26 type-92 records, plus other variants) remain among the largest groups. Slot `0d` appears in the source for 121 of the candidates. Check whether the original PSX AI can select the corresponding action before mapping it. The Level 6 warren Ghost is an intentional exception and uses native combat. The DOS export has no mapped fixed combat slots for types 79, 125, and 126.
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

# Ultima Underworld critter inventory

The [record-by-record inventory](ultima-underworld-npc-conversion-backlog.csv) covers all 657 mobile creature and NPC records in the clean Japanese Rev 1 archive. It compares the default release Track 1 (`72fed1544044659fc323ab86219be2b7eaba8cbf`) with the dedicated-bank combat preview (`06223230c45149324e738cb85288b52109c79af2`). The inventory reads the resident bank grids, palette registrations, and combat tables from the built tracks.

Each record is checked at two camera cells, the archived spawn tile and one tile west. Directional coverage is identical in the two builds. Both cells register DOS art for **all 657 records**. The two-cell check measures configured coverage near the spawn. It leaves camera visibility, reachable viewpoints, actors that move, and actual gameplay draws to the [encounter audit](named-dialogue-audit.md).

| Level | Records | Archive-noninitial | DOS in both views | DOS in one view | Source action candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 56 | 6 | 56 | 0 | 28 |
| 2 | 57 | 8 | 57 | 0 | 24 |
| 3 | 74 | 12 | 74 | 0 | 24 |
| 4 | 70 | 10 | 70 | 0 | 15 |
| 5 | 59 | 9 | 59 | 0 | 16 |
| 6 | 60 | 11 | 60 | 0 | 24 |
| 7 | 94 | 24 | 94 | 0 | 28 |
| 8 | 115 | 25 | 115 | 0 | 31 |
| 9 | 72 | 2 | 72 | 0 | 0 |
| Total | 657 | 107 | 657 | 0 | 190 |

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

In DuckStation, the Level 7 elemental at (51, 40) selected action `01` and drew all five DOS phases before the native damage dispatcher identified it as the source. On Level 5, invoking the original create trap with the debugger spawned the dormant elemental at (19, 50). After it spawned, its AI selected action `03` and drew all five DOS phases. The debugger staged the approaches and assigned the player as the AI target. The game selected the actions and advanced their phases. A follow-up test staged the player on the dry tile (12, 48), facing east. Normal forward input entered the move trigger’s approach at (13, 48). The native trigger chain called create trap 645 with the player as the source and linked the previously absent elemental at (19, 50) in mobile slot 196. The debugger positioned the player and observed the trigger call.

A separate replay used live actor projections from both banks and staged the seven action values across front and rear views and three animation phases. Each floor produced 54 matching DOS sprite packets and six expected native fallbacks for an unmapped action. The checks compared palette, texture page, and texture coordinates, and verified that native fallbacks preserved the packet and draw order.

## Dedicated spider combat

Dedicated spider banks on Levels 1, 3, 4, 5, and 7 now carry DOS slots `00 01 02 03 07 0c 0d` for spider types 68, 83, and 92. Across the two sampled views, the patch resolves missing action mappings for 36 records.

In live DuckStation gameplay, the Level 5 type-92 spider at (36, 52) drew DOS frames for native actions `00`, `01`, and `07`, and the damage dispatcher identified that spider as the source. The debugger placed the camera and assigned the player as the target. The game selected and advanced the actions. Controlled replay used live projections from a type-68 spider on Level 1, type 83 on Level 3, and type 92 on Level 5. Each produced 54 matching DOS sprite packets and six expected native fallbacks across the action, view, and phase checks.

## Level 6 default-bank spider combat

The Academy default bank now uses compact DOS combat tables for type-92 spiders and the wizard family. It retains directional sprites for grubs, slugs, and bats. Both pages fit at full texture scale. All nine default-bank spider records now have DOS slots `00 01 02 03 07 0c 0d` in both sampled views, and the audit found no loss of directional coverage or existing action mappings.

In live DuckStation gameplay, the spider at (42, 43) selected attack `02` and drew the matching DOS frames at phases 0, 2, and 4. The native damage dispatcher identified the same spider as the source. The debugger staged the camera and assigned the player as the target. The game selected the action and advanced its phases.

Controlled replay checked all seven slots against live projections of all nine spiders and the wizard at (24, 21). Each actor produced 54 matching DOS packets and six expected native fallbacks. The three dormant spiders spawned when the debugger invoked their original create handlers.

#### Dormant spider activation

The original PSX wandering-monster routine at `0x80089e4c` scans the floor for zero-flag create traps with mobile templates. The ordinary time update calls it with an eight-tile proximity check on both axes. The rest path calls it without that check. The create handler rejects rolls below the trap's own threshold. This path explains why earlier tile-entry and nearby book tests produced no spawn.

The Academy Spider Combat CHD cold-booted in DuckStation. The debugger staged a fresh character and a bedroll at Level 6 tile (10, 5). The player then used the original R2 + Triangle shortcut and confirmed the rest prompt with Circle. The trace confirmed all three tiles started without a live spider. During rest the game called the wandering routine from return address `0x80077134` and entered the original create handler at `0x80088e44` for each trap. The debugger observed the rolls and tile chains without calling the traps or changing their rolls.

| Spawn tile | PSX create trap | First successful rest | Roll / threshold | Live type-92 slot |
| --- | --- | --- | --- | --- |
| (45, 45) | 778 | 2 | 52 / 42 | 195 |
| (4, 53) | 679 | 1 | 58 / 52 | 195 |
| (47, 56) | 639 | 2 | 49 / 48 | 194 |

Each successful call put a live spider in the target tile's object chain before the handler returned. The slot numbers are runtime allocations. Slot 195 was reused on the second rest.

## Level 7 fire elemental activation

Two type-120 records share (60, 43), and both have a zero in the archive field used by the inventory's initial-link heuristic. Comparing the clean Japanese Rev 1 record bytes to the live tile chain distinguished the floor-loaded actor from the dormant template.

| AVATAR offset | Original activation | Live verification |
| --- | --- | --- |
| `0x9ae4b4` | Level 7 floor load | Starting one tile from the stairs on Level 6, the player walked west from (4, 61) into move trigger 585 at (3, 61). Teleport trap 586 took the player to Level 7 at (2, 61). The elemental was already in mobile slot 189 at (60, 43) before the player rested. |
| `0x9ae498` | Wandering-monster create trap 665, linked to template slot 190 | The player used R2 + Triangle and confirmed Rest with Circle from (2, 61). The original wandering routine called the create handler from return address `0x80089ef4`. A roll of 42 cleared the threshold of 30, and a live elemental matching template 190 appeared at (60, 43). |

The tile was empty just before trap 665 ran, and the game reused mobile slot 189 for the spawned actor. The original archive records differ in the word at offset `+0x0a` (`0x0008` for the floor-loaded actor and `0x0000` for the trap template). The debugger staged the Level 6 approach using the disposable checkpoint and then observed the transition, rest, and tile chains.

The elemental at (35, 56) also uses the wandering-monster routine. After entering Level 7 through the same stairs, the player used the original rest controls at (2, 61). Trap 563, which points to template 171, produced no actor on the first rest (roll 6, threshold 30). On the second rest, a roll of 49 cleared the threshold and the game linked a live type-120 elemental in slot 189 at (35, 56). The debugger confirmed the target tile was empty before each attempt and observed the game's create handler return.

## Level 7 spider movement triggers

The Academy Spider Combat CHD ran in DuckStation with the player staged at (3, 43), facing west. Both target tiles initially had no live spiders. Normal forward input entered (2, 43), where two original move triggers called their own create traps. The debugger observed each create handler call and the live tile chain after return.

| Trigger tile | Move trigger | Create trap | Spawn tile | Template slot | Live type-92 slot |
| --- | --- | --- | --- | --- | --- |
| (2, 43) | 678 | 677 | (4, 43) | 193 | 161 |
| (2, 43) | 676 | 693 | (3, 41) | 196 | 193 |
| (15, 43) | 673 | 713 | (15, 40) | 200 | 161 |
| (15, 43) | 672 | 674 | (13, 43) | 192 | 200 |

In a separate trial on the same CHD, the debugger staged the player at (15, 42). Forward input entered (15, 43). Both spiders at (15, 40) and (13, 43) were absent before their native create calls and present in their target tile chains immediately afterward.

## Remaining checks

- **Fixed combat and special actions.** The preview maps at least one fixed DOS action at a sampled view for 409 records, including slot `0d` for 208. There are 190 records across 34 types with one or more decodable source slots missing from a view that already registers their directional art. Slot `0d` appears in the source for 76 of the candidates. Check whether the original PSX AI can select the corresponding action before mapping it. The Level 6 warren Ghost is an intentional exception and uses native combat. The DOS export has no mapped fixed combat slots for types 79, 125, and 126.
- **Native activation.** Both sampled views already register DOS directional art for all 107 records marked noninitial by the archive heuristic. Of those, 56 have observed floor-load or controller activation and 51 have a create trap identified with the ordinary trigger chain still open. The Level 3 green goblin and the three Level 6 spiders were spawned by controller-driven rest. The Level 5 fire elemental and four Level 7 spiders were spawned by controller-driven movement. All three Level 7 fire elemental activation records have been verified.

## Regenerate the inventory

Run `audit-npcs.py --psx-inventory` with the local DOS installation and the clean Japanese Rev 1 `DATA/AVATAR` archive. Export the DOS action manifests separately for types 64–127 using `UnderworldVisuals export-mixed-combat DOS_ROOT TYPE MANIFEST_DIR/type-TYPE`. Redirect each export's standard error to `MANIFEST_DIR/type-TYPE.err` so the audit can distinguish an explicit missing-slot message from an unavailable manifest.

```sh
python3 audit-critter-banks.py records.csv release-track-1.bin combat-track-1.bin \
  --dos-actions MANIFEST_DIR --dormant-audit dormant-audit.log \
  > docs/ultima-underworld-npc-conversion-backlog.csv
```

The optional dormant audit input is the earlier local DuckStation tile-chain log with `ACTOR` lines. Without it the inventory reports archive markers and the documented controller activation results. Action values in the CSV are hexadecimal. A blank action mapping means the sampled bank has no mapped fixed action for that actor. Source action candidates list decodable slots absent from at least one sampled view with a DOS palette. They exclude the directional registration gaps.

## Earlier atlas feasibility measurements

These combinations fit the indicated texture dimensions in an offline packing check. Each family still needs its own palette selection and verified native VRAM ownership on that floor.

| Candidate area | Initially linked records in the packing check | DOS families |
| --- | ---: | --- |
| Level 6, two 256 × 248 4-bit pages | 30 | Male wizards, female wizards, spiders, bats, slugs, rotworms, gazer |
| Level 8, one additional 256 × 248 4-bit page | 24 | Rotworms, fire elementals, wisp, spiders |
| Level 8, one additional 256 × 248 4-bit page | 25 | Ghosts, rotworms, wisp, spiders |

The Level 6 layouts leave the current preview’s other floor atlases independent. The Level 8 layouts would share the floor with the existing rat renderer. Fire, wisps, and ghosts need a dedicated opacity and lighting comparison before selecting a draw mode.

The three incomplete DOS bitstreams are dwarf animation page `CR33PAGE.N01` frame 20 and headless page `CR24PAGE.N01` frames 29 and 31. Their declared compressed lengths end next to later frame headers. The existing exporter stops at those declared boundaries. This audit leaves their tails and the corresponding PSX models for a separate comparison against what DOS displays.

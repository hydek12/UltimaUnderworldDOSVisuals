# Ultima Underworld PSX with DOS visuals

This macOS Xcode command-line project uses the local DOS release as the visual reference and the English-patched PlayStation disc as the target. The current target inventories the PSX resource archive and exports original DOS critter frames, including their anchors. Game data is supplied locally.

[View the NPC screenshot gallery](https://github.com/hydek12/UltimaUnderworldDOSVisuals/blob/v0.1.0/docs/npc-screenshots.md) for a matched Level 3 lizardman comparison and a Level 7 goblin capture.

## Project changes

Use the [pull request workflow](docs/pull-request-workflow.md) for all changes to `main`. Follow the [project rules](docs/project-rules.md) for builds, verification, and milestones. See the [historical change log](docs/change-history.md) for changes made before PRs were adopted.

## Release acceptance status

The published v0.1.0 source ZIP passed its SHA-256 and ZIP integrity checks. All 25 packaged files matched the release tag, and the rebuilt CHD passed both raw and overall SHA-1 verification. The gallery is available in the tagged GitHub source.

The rebuilt v0.1.0 release passed the four-track disc readback, BIOS cold boot, native memory-card save and reload, and representative staircase round-trips from Level 1 through Level 8. The game’s original eight-talisman sequence also loaded Level 9 from a staged Chamber of Virtue setup. The patched disc and English-only baseline both played the ending film through to scrolling credits in matched cold-boot tests. The rebuilt patch then displayed both result pages and the original Japanese power-off prompt. Normal controller input started the ending from a staged position at the edge of the native gate trigger. A follow-up verified that controller movement could enter the trigger tile from an adjacent tile after staging on its north approach. The ending from that approach remains open. A separate controller check assembled the Key of Infinity from staged pieces and opened the original Chamber of Virtue seal. A continuous controller replay picked up Garamon’s original bones on Level 8, used Gate Travel to reach Level 5, and buried them at his grave. QA prepared the starting position and travel supplies before pickup. The staircase route remains open at the Level 7 eastern fork, with Garamon’s original bones still in inventory. The full quest replay also remains open. Warren’s dialogue preview is the final acceptance check. [Gameplay audit](docs/named-dialogue-audit.md#published-v010-release-acceptance)

## Reproduce the asset checks

1. Open `UnderworldVisuals.xcodeproj` and build the `UnderworldVisuals` scheme.
2. Extract `ultimaunderworld_dos_win.7z` to a scratch directory. Pass the inner `ultimaunderworld/uu` directory to the tool.
3. To get the PSX archive, run `chdman extractcd -i INPUT.chd -o baseline.cue -ob baseline.bin` in a scratch directory. Open the resulting cue in an ISO9660/XA-aware disc extractor and extract `DATA/AVATAR` as a file. The baseline uses Mode 2, so a plain 2048-byte stride over the raw BIN will read the wrong bytes.
4. Run these commands with the executable from Xcode’s Products directory.

```sh
UnderworldVisuals inspect-psx /path/to/AVATAR > avatar-index.csv
UnderworldVisuals export-dos /path/to/ultimaunderworld/uu 70 36 0 goblin.png
UnderworldVisuals export-dos /path/to/ultimaunderworld/uu 70 36 0 goblin-shade-8.png 8
UnderworldVisuals export-dos /path/to/ultimaunderworld/uu 70 36 0 goblin-at-two-tiles.png --dos-light 0 512 0 0
UnderworldVisuals export-dos /path/to/ultimaunderworld/uu 96 36 0 troll.png
UnderworldVisuals export-dos /path/to/ultimaunderworld/uu 111 36 0 troll-111.png
UnderworldVisuals export-dos /path/to/ultimaunderworld/uu 112 36 0 troll-112.png
```

The export arguments after the DOS path are decimal actor type ID, animation slot, frame within the slot, and output path. Slot 36 is the front-facing idle direction. Slots 32–39 provide the other view directions for idle, where available. With an optional shade row from 0 to 15, the exporter maps the original VGA indices through `DATA/LIGHT.DAT` before looking up their colors and keeps the original transparency. Omit the shade for the source palette used by the disc atlas. The DOS renderer selects shade by scene conditions and also handles ghost blend, palette cycling, and projection.

`--dos-light LEVEL DX DY DZ` computes the original DOS creature shade. `LEVEL` is the active DOS light level from 0 to 7. The signed deltas run from the player to the sprite anchor in DOS world units, with 256 units per horizontal tile. The calculation includes height, signed 16-bit distance behavior, and the parameters in `SHADES.DAT`. Light level 5 uses `MONO.DAT`. The exporter prints the table and row it used. [Reconstructed DOS drawing routine](https://github.com/abedegno/underworld-exhumed/blob/54ffea7c08d562176a8edf7398a6ff3fd372a9d2/uw1/src/3d/GAMESORT.C#L330) · [DOS lighting table loader](https://github.com/abedegno/underworld-exhumed/blob/54ffea7c08d562176a8edf7398a6ff3fd372a9d2/uw1/src/map/LIGHTING.C#L35)

See [Visual assessment and patch design](VISUAL-ASSESSMENT.md) for local findings, the intended renderer changes, and the acceptance tests.

## Prepare a comparison in one command

```sh
./prepare-comparison.sh /path/to/UnderworldVisuals \
  "/path/to/ultimaunderworld_dos_win.7z" /path/to/AVATAR /path/to/comparisons
```

The command creates a fresh comparison folder and prints its path. It contains eight DOS goblin idle directions, three troll palette samples, a frame and hotspot manifest, and the PSX resource index. Open its `Compare.html`, then select matching DOS and PSX screenshots for side-by-side and opacity-overlay review. Screenshot selection stays in the browser. Save captures in the generated `captures` folder using the same scene name with `-dos` and `-psx` suffixes so pairs remain easy to find. The viewer normalizes full output frames to 4:3. For pixel-level actor alignment, first capture at matched yaw, distance, camera pitch, and screen-space scale.

## Audit NPC records and DOS animation coverage

[View the NPC conversion backlog](docs/npc-conversion-backlog.md) for coverage by floor and type, the full record audit, and the measured atlas candidates.

```sh
python3 audit-npcs.py /path/to/ultimaunderworld/uu /path/to/japanese-rev1/AVATAR > npc-records.csv
python3 audit-npcs.py /path/to/ultimaunderworld/uu /path/to/japanese-rev1/AVATAR --psx-inventory > psx-npc-records.csv
python3 audit-npcs.py /path/to/ultimaunderworld/uu /path/to/japanese-rev1/AVATAR \
  --dialogue-inventory --english-avatar /path/to/english-v2/AVATAR > local-dialogue-inventory.csv
```

The audit walks the linked objects in the nine DOS tile maps and parses each PSX floor’s 28-byte creature records using the native loader’s table offsets. It checks the type, conversation ID, first six bytes, and packed home tile for full matches. For changed records it looks for an unmatched PSX candidate on the same spawn tile, then for a unique named candidate with the same conversation ID. Each row lists the evidence and the number of idle and walk phases per facing. The PSX inventory includes records the level loader leaves unlinked. The [named dialogue audit](docs/named-dialogue-audit.md) explains how to use the local dialogue inventory for the 70% milestone.

## Build a patch for the original Japanese release

The release source is the clean Japanese Rev 1 raw Mode 2 Track 1 BIN for SLPS-00742, SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`. The English CHD can be a development and comparison build. A Japanese-language visual edition should use the clean Japanese track as its edit base. An English edition can use Gertius’s v2.0 translation as its edit base. Both editions can use the original Japanese track as the only xdelta source. [Gertius’s Rev 1 source and track layout](https://github.com/gertius1/UU_PSX_ENG)

After verifying a visual change in DuckStation, supply its rebuilt raw Track 1 BIN to the release builder. The packager expects the original sector count by default. Pass `--allow-expanded-track` for the larger English build and use a split-BIN CUE. Update the Mode 2 EDC/ECC and ISO file references when rebuilding Track 1. This tool verifies the patch's source hash and output bytes. It assumes the input visual build has already passed the emulator test.

```sh
./build-rev1-patch.sh japanese-rev1-track1.bin tested-visual-track1.bin dos-visuals.xdelta
xdelta3 -d -s japanese-rev1-track1.bin dos-visuals.xdelta patched-track1.bin
```

Use `build-local-release.py` to generate the cumulative xdelta and verify a local CHD in one command. The release includes DOS combat and casting poses in mixed and dedicated rooms, native sprite lighting, and gameplay-driven DOS shade maps. It reads the original split CUE and preserves the three audio tracks and indexes. The [local patch builder guide](docs/local-patch-builder.md) gives the command, source requirements, and manual preview workflow.

The current creature coverage and remaining checks are tracked in the [critter inventory](docs/npc-conversion-backlog.md).

Start the visual work with one camera-facing goblin using the original DOS frames, anchor and eight viewing angles. Trace the retail renderer on the original Japanese Rev 1 before porting any executable change found on the English build. Extend actor coverage after palette, lighting, wall occlusion, facing and animation work on the first actor. Restore DOS materials and color response next. The viewport and HUD need a separate pass to fit the console menus and any chosen language. The patch builder is packaging infrastructure and does not implement these visual changes.

## PlayStation button legends

Build a local preview with `build-local-preview.sh --menu-controls --dos-shade-maps` and the usual source arguments. The footer shows only the available actions, in □, ○, △, × order. The four symbols use the native menu font. Directional prompts are omitted.

| Screen | Prompts |
| --- | --- |
| Options | × Exit on the main page and × Back in submenus |
| Inventory | □ Drop, ○ Pick up or Place, △ Open or Use, and × Exit, Back, or Cancel as appropriate |
| Map | ○ Toggle marker over a valid tile and × Exit |
| Rune Bag and spells | × Back in the Rune Bag, ○ Pick in the spell menu, and × Exit or Back |
| Dialogue | ○ Reply during selection and ○ Continue when dialogue waits for input, right-aligned in the footer |

Most footers are centered. The inventory text shifts left when needed to clear the HUD, and dialogue uses a 16-pixel right margin. Save and load screens use the original prompts. [Build instructions and verification history](docs/local-patch-builder.md#context-sensitive-menu-controls-development-preview) · [Controller footer screenshots](docs/npc-screenshots.md#controller-legend-footers)

## Clean Japanese baseline and Lanugo texture

The downloaded Rev 1 ZIP was verified. Its four-track CUE begins with a 343,678,944-byte Mode 2 data track with the expected Japanese SHA-1. This clean Track 1 is the source for all visual changes. The English Batocera data track is larger, so the fixed-sector Japanese release builder cannot accept a mod built from that English track as its target.

- Japanese `DATA/AVATAR` is 10,584,064 bytes at LBA 397. Lanugo's type-70 actor record is at `AVATAR+0x9A45A4`, entry 133 + 0x5A4, Track 1 LBA 5333. Its 28 bytes match the previously identified English record. The executables have 4,627 differing byte positions, so English runtime addresses and code changes need verification on Japanese Rev 1.
- Build the Xcode scheme and run `UnderworldVisuals export-lanugo-tim DOS_ROOT NEW_OUTPUT_DIRECTORY` to generate a 256×192 16-bit PlayStation TIM with 25 unique idle frames. The CSV records UVs, dimensions and original hotspots for four sequence entries in each of idle slots 32–39. The TIM uses zero for transparent texels. Its VRAM placement is a placeholder that must be assigned by the rendering integration.
- The patch builder converts the TIM to a 4-bit texture with a 16-entry palette. See the Lanugo build notes for the renderer and disc layout.

See the [Lanugo sprite build and verification instructions](lanugo/README.md) for the English release with eight-direction idle and walking animation.

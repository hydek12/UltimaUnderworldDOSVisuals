# Generate the combined patch locally

The combined xdelta is a local output. Its source dictionary is the clean Japanese PlayStation data track, so the delta can carry DOS sprite pixels, palettes, and English translation bytes that are absent from that source. Compressing or repacking the delta would still distribute those bytes. Generate a new delta from the original inputs instead of trying to strip the existing one.

## Build the verified local release

Use Python 3.11 or later, the Xcode-built `UnderworldVisuals` exporter, `xdelta3` with LZMA support when supplying an upstream translation patch, and a `chdman` build that supports split-track extraction. Set `XDELTA3` or `CHDMAN` to the executable path when needed.

```sh
python3 build-local-release.py --english-patch \
  "/path/to/DOS/uu" "/path/to/clean Japanese Rev 1.cue" \
  "/path/to/UU_patch_v2_0.xdelta" "/path/to/UnderworldVisuals" \
  "/path/to/new-local-output"
```

Omit `--english-patch` and supply the already translated English v2.0 Track 1 BIN if you have it. Use the original split four-track Japanese Rev 1 CUE. Its `FILE` entries must point to the accompanying raw BINs.

The release command verifies the hashes of all four original tracks and the CUE indexes before building. It runs the cumulative `--dos-shade-maps` recipe, decodes the combined xdelta against the original Japanese Track 1, and verifies the patched track SHA-1 `691fea5eaf8d6925c170ed40fe35dd9a69709d0f`. It verifies the CHD and checks the indexes and bytes of all four tracks on extraction. The new output directory contains `english-dos-visuals.xdelta` and `Ultima Underworld (English Patch - DOS Visuals).chd`. Both files contain locally supplied game data and belong on the user's machine.

The release includes the Slasher of Veils combat poses, mixed and dedicated room combat and casting, native sprite lighting, and gameplay-driven DOS normal and monochrome shade maps. The [encounter audit](named-dialogue-audit.md#levels-59-recurring-creatures-and-special-models) records the remaining gameplay and art coverage. Delta bytes can vary with the xdelta3 version. The patched track hash identifies the reproduced data track.

## Update Batocera after each local preview

Set the following local Git configuration in the checkout that builds your previews:

```sh
git config --local uw.batoceraCue "/path/to/clean Japanese Rev 1.cue"
git config --local uw.batoceraShare "/Volumes/share"
```

Every successful `build-local-preview.sh` run then packages the patched track with the three original audio tracks, verifies the CHD, and checks all extracted tracks and CUE indexes. It stages the CHD on the mounted share and replaces `roms/psx/Ultima Underworld (English Patch - DOS Visuals).chd` at the existing path after comparing the staged file. Launch the game from a fresh boot to use the new image.

Set `CHDMAN` or local Git config `uw.batoceraChdman` if `chdman` is outside your PATH. Use `UW_SKIP_BATOCERA=1` for a local-only preview. If the share is unavailable, the build reports the deployment failure and keeps the verified local xdelta. The offline release command builds its separate release image locally.


## Run the current preview builder

On macOS, install the Xcode command-line tools, Python 3.11 or later, and xdelta3. If xdelta3 is outside your PATH, set `XDELTA3` to its executable path. Compile the exporter from this checkout into a local build directory.

```sh
mkdir -p /tmp/underworld-tools
swiftc -O main.swift -o /tmp/underworld-tools/UnderworldVisuals
```

1. Extract your DOS installation and select the folder containing `CRIT/ASSOC.ANM` and the creature animation pages.
2. Select your clean Japanese Rev 1 raw Mode 2 Track 1 BIN, SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`.
3. Prepare the English v2.0 raw Track 1 locally from the same revision with the separately obtained translation. The expected English track SHA-1 is `325585c11548538e323e8896c3fb8b1cc5d65521`.
4. Run the builder with the compiled exporter and a new destination.

```sh
./build-local-preview.sh "/path/to/DOS/uu" \
  "/path/to/clean-japanese-track1.bin" "/path/to/english-v2-track1.bin" \
  "/tmp/underworld-tools/UnderworldVisuals" "/path/to/english-dos-preview.xdelta"
```

To supply the separately obtained English v2.0 xdelta instead of a translated BIN, add `--english-patch` before the DOS folder argument and use the upstream xdelta as the English input. The builder decodes it locally and validates the resulting English track. Use an xdelta3 build with LZMA support to decode the upstream translation. The already-translated BIN input can also be used with an xdelta3 build that lacks LZMA.

The script exports sprites and palettes into temporary storage, applies the renderer changes, and builds the English preview data track. It uses the existing packager to encode the delta against the Japanese BIN, decodes it, and compares every output byte before publishing the local file. It cleans up the generated atlases and working BIN on exit. To use the result, decode it against the original Japanese BIN and point Track 1 in a copy of the original split-BIN CUE at the new BIN. Keep the three audio tracks and all original indexes. The current preview target SHA-1 is `18c839eec5fdbc311f6c0c5cd5c69d085279762c`.

### Build the Level 6 wizard preview

Add `--level-six-wizards` as the first argument. It adds the seven initially linked Level 6 wizards of types 103, 108, and 109. They draw DOS idle and walk sprites in their three original palettes. Other wizard actions retain the native renderer. The expected Track 1 SHA-1 for this optional build is `f3e72a895004cc695ecc6b71a149962530382ae2`.

### Build the Level 6 wizard and spider preview

Use `--level-six-spiders` as the first option. It includes the wizard preview and adds the six initially active Level 6 type 92 spiders, with the DOS spider palette tied to that type. The two families use separate texture pages and share the floor loader. Type 92 on other floors and non-idle/non-walking actions retain their native graphics. The expected Track 1 SHA-1 is `9fdef5197a7e80f7a291172ae37f6e0155045918`.

### Build the Level 6 wizard casting preview

Use `--level-six-casting` as the first option to include the Level 6 wizards and spiders and replace the wizard casting pose. The PlayStation casting state uses action `0x0d` and phases 0–4. The builder reads those five poses from DOS slot `0x0d` for each of the three wizard palettes. The wizard uses standing sprites when viewed from the sides or rear, following the DOS view rule. Spell effects, hit logic, and cast timing use the PlayStation routines. The expected Track 1 SHA-1 is `812bdaa643bd2c247ee9b16a80812dabfc331d64`.

### Build the Level 6 wizard combat preview

Use `--level-six-combat` as the first option. It includes the wizard casting preview and adds the combat stance, three melee attacks, retreat, and death poses for all seven Level 6 wizards. The three wizard palettes share one texture page, with the spiders on the adjacent page. Front views use the fixed DOS poses. Side and rear views use directional standing sprites, except death uses its fixed pose from all angles. The PlayStation still handles damage, timing, and spell effects. The expected Track 1 SHA-1 is `1a6812c72b0e97f534b3ccc77c8fe23d7f40cd9c`.

### Build the wizard spell-effects preview

Use `--level-six-effects` as the first option. It extends the Level 6 combat preview with DOS art for the shared Fireball, Lightning Bolt, and Magic Missile projectiles, the secondary Fireball flames, and the Lightning Bolt impact. The five central Fireball impact frames already match the DOS texels and remain in their original slots. The effect textures are shared across floors. The PlayStation still handles flight, collision, animation timing, and damage.

DuckStation traced flight at `0x8004dc6c` and impact draws at `0x8004e168`. The projectile and impact packets use the port's existing indexed texture pages. The recipe updates those sheets, assigns the DOS flame rectangles, and recalculates the affected Mode 2 Form 1 sectors. It changes nine sectors compared with the combat preview. The build booted from a separate four-track CHD. All 3,172 texels sampled from live GPU memory matched the 21 DOS source frames selected by the traced packets. The expected Track 1 SHA-1 is `051934d738450cc1424267ed5b15c07db5b10ecf`.

For a local comparison, run `UnderworldVisuals export-dos-spell-effects DOS_ROOT NEW_OUTPUT_DIRECTORY`. The exporter reads `OBJECTS.GR`, `ANIMO.GR`, `OBJECTS.DAT`, `ALLPALS.DAT`, and `PALS.DAT`. It writes PNGs, RGB555 frames for the builder, and a frame manifest. Keep the generated graphics local.

### Build the expanded Level 6 NPC preview

Use `--level-six-expanded` as the first option. It includes the spell-effects preview and adds idle and walking sprites for 14 initially linked Level 6 rot grubs (64 and 82), slugs (65 and 69), and bats (66 and 73). Three dormant records match the same renderer rules. The shared secondary texture page also holds the six previously supported spiders. Each family uses its own DOS palette bank and frame table. Effects, actor records, and dialogue data retain the previous preview's data. Combat actions on the new families use the native renderer.

The expected Track 1 SHA-1 is `fe7250fd1f4e2c099895b9871c2274f7ac38d1d6`. This preview is one batch of the Level 6 and named dialogue work. Additional families need more texture capacity. For example, the two-page layout cannot add the Level 6 spectre alongside the current allocation without moving an existing family or changing the layout.

## Separate release code from game assets

1. Freeze a tested build and record the Japanese and English baseline hashes, the final Track 1 hash, the exporter and builder revisions, and the supported DOS source versions. Record individual input signatures for the DOS files the exporter consumes, so unsupported releases fail with actionable errors.
2. Review each change to the final data track. Keep project-authored renderer logic, guarded hook offsets, actor-to-animation mapping, palette conversion rules, build configuration, and expected hashes in the release recipe. Read original instructions, graphics, indices, palettes, and other game-derived bytes from the local files wherever the builder needs them. Generate atlas pixels and palette rows at build time. Review hardcoded byte blocks individually, especially expected hook signatures and any copied instructions.
3. Let the user supply the upstream English translation separately. Verify the translated baseline before applying visual changes. Keep the upstream translation payload, translated disc, and regenerated combined delta out of the release.
4. Build the distributable with an explicit list of source files, tools, recipe, and documentation. Exclude game archives, binaries, executable dumps, textures, palettes, audio, disc images, intermediate build products, and screenshots from the package. Use synthetic fixtures for automated tests. Review the packaged files and repository history for prior asset commits before choosing what to publish. Keep the curated screenshots in the documentation gallery. Use the explicit source archive below for release downloads.
5. Rebuild from a clean checkout with only the supported local inputs and compare the target Track 1 hash. Exercise missing and wrong inputs and confirm that no partial output is published. Verify the CUE, audio tracks, fresh emulator boot, and representative scenes. Review permissions for anything the release would redistribute before publishing.

## Assemble the source-only release

Run this from the repository root after committing the reviewed release sources. Attach this archive to the release if distributing a download.

```sh
git archive --format=zip --output=/tmp/underworld-builder-source.zip HEAD -- \
  build-local-release.py build-local-preview.sh build-rev1-patch.sh main.swift docs/local-patch-builder.md \
  lanugo/academy_banks.py lanugo/build_english.py lanugo/build_track.py lanugo/creature_atlas.py \
  lanugo/lower_atlas.py lanugo/mipswords.py lanugo/preview_lighting.py \
  lanugo/renderer.py lanugo/spell_effects.py lanugo/variant_atlas.py
unzip -l /tmp/underworld-builder-source.zip
```

Review the archive contents before uploading. Users generate the combined xdelta on their own machines. After verifying a new preview, keep only the latest verified test disc image. Remove superseded test CHDs and temporary test BIN/CUE copies. Preserve the original disc dumps and audio tracks.

## Develop the macOS application

1. Add a SwiftUI macOS app target to the Xcode project. Keep the current command-line builder as the first backend so the GUI and CLI run the same recipe. Package the original exporter with the app and use a versioned recipe for source hashes, enabled features, and tool compatibility checks.
2. Present file pickers for the DOS folder, Japanese data track, and the upstream translation patch or locally translated track. For patch input, verify the Japanese hash, apply the upstream delta in temporary storage, and check the English hash before continuing. Start with an extracted DOS directory, then add local archive import with safe extraction if needed.
3. Run the tools off the main thread with explicit argument arrays. Show validation, export, track rebuild, and round-trip verification as distinct stages. On cancellation, terminate the active build and remove temporary files after it exits. Keep game data on the device and publish the xdelta to the selected destination only after verification.
4. Test that a build from the app matches the CLI output track, preserves input files, handles paths with spaces, and reports missing assets or tool versions clearly. During release QA, confirm the app bundle contains only reviewed tools, recipe data, and documentation. Check the applicable redistribution terms before bundling third-party tools.

### Academy art previews

Use `--academy-wizb` or `--academy-wizc` in place of `--level-six-expanded` to test one Academy sprite family at a time. Both previews keep the primary wizard page and replace the secondary page. WizB covers types 106 and 115 (including Dr. Owl, Dominus, and Nilpont). WizC covers type 107 (including Delanrey and Louvnon). The previews use the local DOS idle and walking frames at their original dimensions, with native rendering for other actions. Spiders, rot grubs, slugs, and bats use native rendering in these builds.

Each family fits the 256×248 secondary page by itself. Packing both together exceeds that page at the original frame sizes. Use the runtime build to test both on one disc.

### Level 6 runtime banking preview

Use `--academy-runtime` in place of the static Academy flags. The preview selects an atlas bank at the start of a frame from the camera's four-tile map cell. On a change, it waits for pending GPU work, reads the new tables and textures, and retains the bank's disc address for inventory and dialogue restoration. Actors outside the active bank use the native renderer. The primary wizard page is available except in the banks that use both pages.

The runtime build includes all five Level 6 types that were still using native idle and walk art. The imp variants (75/81) share both pages at full 8-bit resolution and use independent 32-entry palette rows. The skeleton (74) uses both pages at its original 4-bit resolution. The headless (91) uses both pages at full resolution and 8-bit depth. Its exporter fills one missing transparent tail pixel in each of two identified walking frames. The ghoul (105) uses both pages with 8-bit indices and 7/8-resolution textures. It retains the original DOS frame dimensions and hotspots for on-screen placement.

The Japanese Rev 1 source track remains the input for every generated xdelta. Earlier non-runtime profiles still use their existing layouts. Named quest NPCs beyond Level 6 remain tracked separately.

The creature combat build uses the DOS stance, three melee sequences, retreat, and death for the imps, skeleton, and headless. The imps also use four DOS casting frames. Their last frame is held through the remaining PSX casting phases. The ghoul uses DOS stance and retreat at its existing texture resolution. Its attack and death poses use the native renderer. Action timing and damage still come from the PlayStation release. Side and rear combat views use the DOS directional standing sprites, with the DOS death pose visible from all directions where enabled.

### Level 1 named NPC preview

Use `--level-one-dialogue` to include the Level 1 dialogue NPCs with the cumulative Level 6 combat build. DuckStation selects one Level 1 bank for the current camera cell. The original green goblin textures, palette, and frame tables remain in their default bank. Drog, Vernix, Ketchaval, and Retichall use two full-resolution 4-bit pages. Bragit, Gulik, and Hagbard use two 8-bit pages with textures at 15/16 of the original resolution. Their on-screen dimensions and hotspots come from the unscaled DOS frames.

The banks switch between frames. Dialogue and inventory return use the active bank's disc address. An actor keeps native rendering when the active bank has no matching art or action. In particular, a camera angle that crosses the boundary between Lanugo's room and the south approach to Vernix can expose the native fallback. The preview leaves the PlayStation's dialogue scripts, portraits, trade, quest logic, and combat behavior in place.

The Level 1 named-NPC profile stores floor starts as little-endian halfword sector offsets relative to its Level 1 payload. Offset 0 selects Level 1, positive offsets through 32766 select later payloads, and 32767 marks an absent payload. Earlier profiles retain their original byte tables for reproducible builds. The extended-table build has Track 1 SHA-1 `d3b370395327bdd630c3d9eade4d73662eb8dd43`.

### Level 2 named NPC preview

Use `--level-two-dialogue` for the cumulative named-NPC preview. Level 2 switches among the existing green goblin art, a full-resolution 8-bit dwarf bank for types 84 and 86, and a fighter bank for Corby (type 98). Corby uses his DOS palette and 15/16 texture resolution with the original on-screen dimensions and hotspots. The local exporter restores one transparent tail pixel in the identified DOS dwarf idle frame. The new banks use sector offsets 652, 703, and 754 relative to the first Level 1 bank. The other floors keep their existing payloads. Unsupported actions use native rendering.

The expected Track 1 SHA-1 is `1886fa383413e53d4dd1756975f5ced8526b187b`.

### Level 3 named NPC preview

Use `--level-three-dialogue` for the cumulative Level 1–3 and Level 6 preview. Level 3 keeps its standard DOS lizardman bank with combat poses. Three additional room banks cover the bandits, Murgo and nearby lizardmen, and Zak. The bandits and Zak use the local DOS palettes with 15/16 textures. Murgo uses full-resolution 4-bit textures. His room shares VRAM with the three lizard palettes at 12/16 texture resolution for idle and walk. Fixed lizard combat poses there fall back to the native renderer. All sprite screen dimensions and hotspots use the original DOS frames.

The expected Track 1 SHA-1 is `59e4eaa757852bae0c9b1cac0aff28199e6c05b8`.

### Level 4 named NPC preview

Use `--level-four-dialogue` to include the Level 4 named actors. The town bank fits both DOS fighter families on separate 8-bit pages at 11/16 texture resolution. Dedicated fighter rooms use 15/16 textures. Rawstag, Lakshi Longtooth, and Sethar Strongarm share a full-resolution 4-bit troll bank with the matching DOS palettes. The standard lizard bank remains available outside those areas.

The expected Track 1 SHA-1 is `eab1814243f110e993076762d590ed86a4aaae24`.

### Cumulative named NPC and recurring creature preview

Use `--late-dialogue` as the first argument for the cumulative build. This includes the recurring creature and humanoid banks for Levels 1–4, then adds Judy, Anjor, and the four named ghouls on Level 5, and Carasso on Level 8. Judy and Anjor use full-resolution 4-bit art. The ghouls use 14/16 textures, and Carasso shares a bank with full-resolution rats using 11/16 fighter textures. The standard goblin and rat banks remain available elsewhere on their respective floors. Garamon’s initially dormant record retains native rendering pending activation and DOS identity checks.

The same option adds Level 7 banks for Tyball, Cardon, the gray guards, the prison corridor, the troll guard, and the dormant imp. The prison bank shares two pages across wizards, dwarves, and fighters. The wizard page runs at full 4-bit resolution. The shared 8-bit page uses 9/16 textures for dwarves and 8/16 textures for fighters and retains the original sprite dimensions and anchors. Cardon’s separate 8-bit bank uses 15/16 textures. These additions supply directional idle and walk frames. Other actions use the existing native fallback. Dormant actors still require their original gameplay triggers.

The Level 1 imp and Level 3 green goblin have local idle and walk banks. The Level 5 Gazer shares a bank with the three nearby green goblins so their spawn views can show both families. See the [critter coverage audit](named-dialogue-audit.md#imp-green-goblin-and-gazer-spawn-coverage). The cumulative recipe also fills 27 spawn-view gaps for noninitial records. See the [dormant creature audit](named-dialogue-audit.md#dormant-creature-spawn-coverage).

The early-floor room selector selects a bank from the camera’s two-tile cell. Shared banks retain independent DOS palettes for nearby families. Level 4 packs bats and grubs on one page and rats on the other so their rooms can overlap without displacing the grub. The eight idle and walk facings retain their frame rectangles and anchor points. The `--late-dialogue` comparison build’s Track 1 SHA-1 is `ae115f5170f751f0d9290c42ff2a1c7dec210065`. The renderer falls back to native art when the selected room lacks the actor’s entry or when an action has no supported DOS pose.

### Levels 5–9

The cumulative build uses additional room banks on Levels 5, 7, and 8, and extends the existing Academy banks to cover the third troll palette and more native trap spawn cells on Level 6. One floor-wide Level 9 bank includes the bat skull, lightning, eye, and Slasher of Veils. The Slasher follows the Avatar, so it needs its atlas outside its initial spawn room. The Level 9 renderer saves each touched depth bucket once so the Slasher’s native model can be replaced even when it submits more than 128 polygons. The lightning and eye reuse each directional DOS standing sequence in their walk slots because their DOS animation files lack a walk sequence. Texture scaling keeps the hazards and boss within the available VRAM while retaining their frame dimensions and anchors.

### Level 9 Slasher combat preview

Use `--slasher-combat` as the first argument to build the cumulative preview with the Slasher’s seven DOS combat sequences. The Level 9 bank fits all 31 combat frames at 9/16 texture resolution for the Slasher, with the original DOS frame rectangles and hotspots. Fixed combat poses use the forward three views. The other views use directional standing sprites, and the death pose uses all eight views. Action values without a mapped pose keep the PlayStation renderer.

The expected Track 1 SHA-1 is `2895f48350a195d396015f515216b4c5718e1d63`. The preview also enables full-resolution combat art for imps, skeletons, and headless in their dedicated room banks. The imps have DOS casting sprites. See the [encounter audit](named-dialogue-audit.md#level-9-slasher-combat-preview) for the verified cases.

The combat preview also selects DOS action frames per actor family in 24 mixed room layouts (32 banks) on Levels 1–5, 7, and 8. The two lighting previews inherit these tables. Room pages may use a lower common texture scale to fit the extra frames. Actions without a usable DOS source keep the native sprite. The [mixed room audit](named-dialogue-audit.md#mixed-room-combat-and-casting) covers the renderer matrix and the [Level 5 AI-initiated Gazer cast](named-dialogue-audit.md#ai-initiated-gazer-cast).

The combat preview also enables the remaining DOS combat poses in the dedicated ghoul, Gazer, and wizard banks, including the Level 6 Academy banks and Level 7 Tyball. Ghoul casts keep the native renderer. See the [dedicated-bank audit](named-dialogue-audit.md#dedicated-ghoul-gazer-and-wizard-banks).

### Native sprite lighting preview

Use `--native-sprite-lighting` as the first argument to the preview builder. It includes the Slasher combat preview and enables PlayStation depth-based lighting on DOS sprites in the Level 3 bandit bank and the Level 4 bat, grub, and rat bank. The lighting uses the same depth table as the native polygons and preserves the existing sprite geometry, palette, and combat fallbacks in those rooms.

The expected Track 1 SHA-1 is `471716a2f5580833657508146b0c7560baaa70ab`. The [90% audit](named-dialogue-audit.md#90-native-sprite-lighting-preview) records the runtime and build checks.

### DOS shade maps and monochrome preview

The release builder selects `--dos-shade-maps` automatically. Pass the same flag to the preview builder to generate its xdelta without CHD packaging. It includes the native sprite lighting preview and adds the original DOS `LIGHT.DAT`, `MONO.DAT`, and `SHADES.DAT` behavior to idle and walking green goblins in the default Level 1 room bank. The bank uploads 16 normal and 16 monochrome shade rows for each of the four DOS palettes.

In the cumulative preview, the game resolves equipped lights and active spells into one effective light level. The DOS renderer reads that level for each supported goblin draw. Level 5 (Night Vision) selects the monochrome map. The other levels use the normal map. Room bank loads leave the effective level under the game's control.

The expected Track 1 SHA-1 is `691fea5eaf8d6925c170ed40fe35dd9a69709d0f`. The [gameplay audit](named-dialogue-audit.md#100-gameplay-driven-dos-lighting) records the torch and spell transitions and earlier disc checks.

### Context-sensitive menu controls development preview

Pass `--menu-controls` before the preview profile flag to add a button legend to the PSX Options, Inventory, map, Rune Bag, spell, and dialogue screens. For example, use `build-local-preview.sh --menu-controls --dos-shade-maps` with the usual source arguments. The top-level page shows Cross to exit. Submenus show Cross to go back. The legend uses single-glyph ○, □, △, and × icons in the native menu font. The opt-in recipe adds the icons to four unused font slots and draws the legend just before the frame is submitted. Save and load screens use their stock prompts.

The dedicated fire elemental combat preview includes this opt-in menu patch. Its Track 1 SHA-1 is `d01bb0fb5ab5de42951f4a4f6e19334c52a9d383`. All four CHD tracks passed byte-for-byte readback.

The legends list applicable buttons in this order: □, ○, △, ×. Inventory centers the footer and shifts long prompts left just enough to clear the health and mana icons. On an occupied slot, □ starts the native drop flow, ○ picks up the item, and △ opens a container or uses the item. While holding an item, ○ places it on a different slot. × cancels a held selection, closes an open container, or exits Inventory.

DuckStation restored the preview's executable hook into a disposable gameplay checkpoint and exercised the native Options loop. Down twice and Circle entered the first settings submenu. Cross returned to the top page and then closed Options. Both legend variants fit the 320-pixel screen and submitted text packets at (8, 218). The preview changed two executable sectors relative to v0.1.0, and all four CHD tracks passed readback. The preview Track 1 SHA-1 is `aae21a2b1438968adf1933f3f7b62cb112b98e00`.

The map footer shows × Exit. When the cursor is over a map tile, it also shows ○ Toggle marker. The footer uses the same button order and native glyphs as Inventory. The map image, quill, and map palette upload clear of the font’s VRAM regions. DuckStation cold-booted the preview and verified that Circle placed and cleared a marker, Cross returned to Inventory, and the dungeon HUD rendered after exiting Inventory. All four CHD tracks passed byte-for-byte readback. The map preview Track 1 SHA-1 is `6412262fe30c75cde1385faa08bacf5b3811b4ae`.

The ordered-footer preview cold-booted in DuckStation. The full □ Drop, ○ Pick up, △ Open, × Exit legend fit beside the HUD. A held torch over an empty slot showed centered ○ Place and × Cancel. An empty Inventory slot showed only centered × Exit, and an empty sack showed only centered × Back. All four CHD tracks passed byte-for-byte readback. The ordered-footer preview Track 1 SHA-1 is `a54b02bda4e475ad25a9586d08f0769e8a3f700d`.

The button-symbol preview cold-booted in DuckStation and loaded a memory-card copy. The full Inventory footer fit beside the HUD with a container selected. Mapped inputs opened the Rune Bag and sack, picked up and placed a torch, and opened and declined the native drop confirmation. The confirmation temporarily covers part of the footer. The Rune Bag and Main menu displayed only button prompts. All four CHD tracks passed byte-for-byte readback. The button-symbol preview Track 1 SHA-1 is `7989182515eb78d328349b6f9be2908309bc155a`.

The inventory actions preview cold-booted in DuckStation and loaded a memory-card copy. With test items staged, mapped inputs opened a sack and the Rune Bag with Triangle, canceled and moved a torch using Cross and Circle, and started the native drop flow with Square. After confirming and placing the torch on open floor with Circle, its inventory slot was empty. A wall obstructed the first placement attempt and the game returned the torch to its slot. All four CHD tracks passed byte-for-byte readback. The inventory actions preview Track 1 SHA-1 is `3e0517878546dd83aa85b58ab65eb6fa5a6daf31`.

The inventory preview was verified in the native loop from a disposable DuckStation checkpoint with a torch and sack staged. Circle selected the torch and placed it in an adjacent empty slot. Cross canceled a separate selection without moving the torch. Opening the sack changed the footer to Back, closing it restored Exit, and the original inventory exit returned to gameplay. The probe checked the font packets in each state and reran the Options navigation check on the same CHD. All four tracks passed readback. The inventory preview Track 1 SHA-1 is `cc1301642eeca6edb3a58e9cb527f57c4e46bf52`.

The Rune Bag footer shows × to return to Inventory. The spell menu footer shows ○ to choose. Cross exits the main spell menu and returns from the learned-mantra list. The PSX port prepares spells from the spell list using the runes the player has collected.

DuckStation loaded the rebuilt preview and restored its menu hooks from disc into a disposable Level 1 checkpoint. With a Rune Bag, runes, and a mantra staged, debugger-injected button masks exercised the native input loops. The Rune Bag cursor moved horizontally and vertically before returning to Inventory. The spell menu entered and left the mantra list, cleared the previous spell selection, prepared a spell, and exited. The native font submitted all three footers at y=218 within the 320-pixel frame. Three executable sectors differ from the inventory preview. All four CHD tracks passed byte-for-byte readback. The rune and spell preview Track 1 SHA-1 is `44918e7c273d28d8d43fe766111d6e0e1f863092`.

Dialogue shows a right-aligned footer with ○ Reply while a choice is active and ○ Continue when the script accepts input to advance text or close a farewell page. Leaving a conversation uses its existing farewell choice.

The right-aligned dialogue footer uses a 16-pixel right margin. Reply rows moved six pixels up to clear the footer on a full list. DuckStation cold-booted the preview from a memory-card copy and verified Hagbard’s four reply choices and farewell prompt. All four CHD tracks passed byte-for-byte readback. The dialogue footer preview Track 1 SHA-1 is `8a9f09c70412dcc0ed5e70c3193d2d28110ccd34`.

DuckStation loaded the dialogue preview into a disposable Level 1 checkpoint. Debugger-injected inputs moved the cursor in Hagbard’s four-reply English menu, confirmed a reply, and continued past his farewell. A separate long-text test staged a multi-page passage with nine undisplayed lines, confirmed that the text stopped at y=208 and the footer drew at y=218, and entered the native scroll routine with Circle. Two executable sectors differ from the rune and spell preview. All four CHD tracks passed byte-for-byte readback. The dialogue preview Track 1 SHA-1 is `905161ff88767cea513390b2ed52f92756a8a3ba`.

Options uses the space between the HUD icons. The Rune Bag and spell menu leave room below the item or spell name.

DuckStation loaded the final preview with disposable Level 1 checkpoints. Mapped keyboard inputs navigated Hagbard’s replies and farewell, advanced staged multi-page text, canceled a held torch, backed out of a sack, browsed runes, and returned from the Options submenu to gameplay. R2 + Square opened the spell menu. Circle prepared Light, Cross returned to gameplay, and Square cast it. The game recorded mana changing from 50 to 47 and effective light changing from 0 to 3. The debugger staged the checkpoints, restored the executable hooks from disc, and observed game state. The menu and cast inputs went through DuckStation’s normal mappings. All four CHD tracks passed byte-for-byte readback. The layout preview Track 1 SHA-1 is `97ae22dbe62a785ecb158873752a726c7f0064fa`.

A Batocera cold boot exposed a memory-lifetime bug in the earlier preview. The game reused the executable regions that held the menu routines, leaving the original hooks pointing at overwritten code. The previous DuckStation checkpoint tests wrote the routines into live RAM and missed the overwrite. The opt-in build now lowers the native stack and heap ceiling by 2 KiB, copies the menu routines into the space above the stack before heap initialization, and clears the startup copy so the game can reuse its original RAM.

The repaired CHD cold-booted through the PlayStation BIOS in DuckStation and loaded a copy of the Batocera memory card through the game’s Continue screen. Mapped inputs opened Main, entered Options, returned to the dungeon, and opened Inventory with the expected prompts. A read-only debugger check after both menus verified all 1,088 reserved bytes against the build. All four CHD tracks passed byte-for-byte readback. The repaired preview Track 1 SHA-1 is `d8bb6bc44bf8780681c8715543fa5109154df4a9`. Use a fresh game boot and a memory-card save to test this change because emulator save states restore the previous executable and RAM layout.

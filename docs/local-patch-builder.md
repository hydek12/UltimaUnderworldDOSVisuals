# Generate the combined patch locally

The combined xdelta is a local output. Its source dictionary is the clean Japanese PlayStation data track, so the delta can carry DOS sprite pixels, palettes, and English translation bytes that are absent from that source. Compressing or repacking the delta would still distribute those bytes. Generate a new delta from the original inputs instead of trying to strip the existing one.

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

To supply the separately obtained English v2.0 xdelta instead of a translated BIN, add `--english-patch` before the DOS folder argument and use the upstream xdelta as the English input. The builder decodes it locally and validates the resulting English track.

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
  build-local-preview.sh build-rev1-patch.sh main.swift docs/local-patch-builder.md \
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

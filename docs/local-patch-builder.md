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

The expected Track 1 SHA-1 is `846875b8f79e1342fd81b678c5bb3c4b94beb708`. This preview is one batch of the Level 6 and named dialogue work. Additional families need more texture capacity. For example, the two-page layout cannot add the Level 6 spectre alongside the current allocation without moving an existing family or changing the layout.

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
  lanugo/build_english.py lanugo/build_track.py lanugo/creature_atlas.py \
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

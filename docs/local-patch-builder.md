# Generate the combined patch locally

The combined xdelta is a local output. Its source dictionary is the clean Japanese PlayStation data track, so the delta can carry DOS sprite pixels, palettes, and English translation bytes that are absent from that source. Compressing or repacking the delta would still distribute those bytes. Generate a new delta from the original inputs instead of trying to strip the existing one.

## Run the current preview builder

Build the UnderworldVisuals scheme in Xcode. Use Python 3.11 or later and an installed xdelta3, or point the `XDELTA3` environment variable at the local executable.

1. Extract your DOS installation and select the folder containing `CRIT/ASSOC.ANM` and the creature animation pages.
2. Select your clean Japanese Rev 1 raw Mode 2 Track 1 BIN, SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`.
3. Prepare the English v2.0 raw Track 1 locally from the same revision with the separately obtained translation. The expected English track SHA-1 is `325585c11548538e323e8896c3fb8b1cc5d65521`.
4. Run the builder with the Xcode product and a new destination.

```sh
./build-local-preview.sh "/path/to/DOS/uu" \
  "/path/to/clean-japanese-track1.bin" "/path/to/english-v2-track1.bin" \
  "/path/to/UnderworldVisuals" "/path/to/english-dos-preview.xdelta"
```

The script exports sprites and palettes into temporary storage, applies the renderer changes, and builds the English preview data track. It uses the existing packager to encode the delta against the Japanese BIN, decodes it, and compares every output byte before publishing the local file. It cleans up the generated atlases and working BIN on exit. To use the result, decode it against the original Japanese BIN and point Track 1 in a copy of the original split-BIN CUE at the new BIN. Keep the three audio tracks and all original indexes. The current preview target SHA-1 is `18c839eec5fdbc311f6c0c5cd5c69d085279762c`.

## Separate release code from game assets

1. Freeze a tested build and record the Japanese and English baseline hashes, the final Track 1 hash, the exporter and builder revisions, and the supported DOS source versions. Record individual input signatures for the DOS files the exporter consumes, so unsupported releases fail with actionable errors.
2. Review each change to the final data track. Keep project-authored renderer logic, guarded hook offsets, actor-to-animation mapping, palette conversion rules, build configuration, and expected hashes in the release recipe. Read original instructions, graphics, indices, palettes, and other game-derived bytes from the local files wherever the builder needs them. Generate atlas pixels and palette rows at build time. Review hardcoded byte blocks individually, especially expected hook signatures and any copied instructions.
3. Let the user supply the upstream English translation separately. Verify the translated baseline before applying visual changes. Keep the upstream translation payload, translated disc, and regenerated combined delta out of the release.
4. Build the distributable with an explicit list of source files, tools, recipe, and documentation. Exclude game archives, binaries, executable dumps, textures, palettes, audio, disc images, intermediate build products, and screenshots from the package. Use synthetic fixtures for automated tests. Review the packaged files and repository history for prior asset commits before choosing what to publish. The existing documentation gallery contains gameplay screenshots, so use a separate package rather than the repository's automatic source archive for a release with no game media.
5. Rebuild from a clean checkout with only the supported local inputs and compare the target Track 1 hash. Exercise missing and wrong inputs and confirm that no partial output is published. Verify the CUE, audio tracks, fresh emulator boot, and representative scenes. Review permissions for anything the release would redistribute before publishing.

## Develop the macOS application

1. Add a SwiftUI macOS app target to the Xcode project. Keep the current command-line builder as the first backend so the GUI and CLI run the same recipe. Package the original exporter with the app and use a versioned recipe for source hashes, enabled features, and tool compatibility checks.
2. Present file pickers for the DOS folder, Japanese data track, and the upstream translation patch or locally translated track. For patch input, verify the Japanese hash, apply the upstream delta in temporary storage, and check the English hash before continuing. Start with an extracted DOS directory, then add local archive import with safe extraction if needed.
3. Run the tools off the main thread with explicit argument arrays. Show validation, export, track rebuild, and round-trip verification as distinct stages. On cancellation, terminate the active build and remove temporary files after it exits. Keep game data on the device and publish the xdelta to the selected destination only after verification.
4. Test that a build from the app matches the CLI output track, preserves input files, handles paths with spaces, and reports missing assets or tool versions clearly. During release QA, confirm the app bundle contains only reviewed tools, recipe data, and documentation. Check the applicable redistribution terms before bundling third-party tools.

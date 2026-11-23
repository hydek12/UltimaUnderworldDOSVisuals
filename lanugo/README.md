# Lanugo sprite prototype for Japanese Rev 1

Build the Xcode command-line scheme, then use the original Japanese Track 1 and your original DOS installation.

```sh
UnderworldVisuals export-lanugo-tim "/path/to/ultimaunderworld/uu" /tmp/lanugo-atlas
python3 lanugo/build_track.py japan-rev1-track01.bin /tmp/lanugo-atlas lanugo-track01.bin
./build-rev1-patch.sh japan-rev1-track01.bin lanugo-track01.bin lanugo.xdelta
```

The track builder needs Python 3.11 or newer. The patch builder needs xdelta3. The output CHD can be produced with chdman after pointing a copy of the original CUE at the newly patched Track 1. Preserve the three original audio tracks and their index settings.

Lanugo's original model still supplies camera projection bounds and selection geometry. The patch suppresses his original model's two GPU queue insertion paths and submits one textured quad in the same ordering table. It chooses one of eight idle views by comparing Lanugo's heading with camera yaw in 32 sectors, using the original DOS idle-view order, and scales the sprite with the original projected height and hotspot. The rendering functions are specific to Japanese Rev 1.

The loader places the texture and palette in a region that was empty in the captured Level 1 frame. The builder patches an executable region checked against the original BIN and uses initially empty data-track sectors 145980–145989 for the payload. It checks and recomputes Mode 2 Form 1 integrity data. It preserves the size of Track 1 so the CUE can keep its original layout.

This is an idle-sprite prototype for Lanugo. Walk, attack and death sprites, DOS lighting, and other actors are outside the prototype. Use a fresh boot for comparison since an emulator state may carry the original executable in RAM. Full-game play, hardware testing and VRAM use after a level transition require separate checks.

## English v2.0 and DOS Lanugo

Use the same DOS atlas exported by the Xcode scheme. Extract the raw Track 1 BIN from the English v2.0 CHD or obtain it by applying Gertius's v2.0 fan translation to clean Japanese Rev 1. The combined builder expects the English Track 1 SHA-1 `325585c11548538e323e8896c3fb8b1cc5d65521`.

```sh
python3 lanugo/build_english.py english-v2-track01.bin /tmp/lanugo-atlas english-dos-track01.bin
xdelta3 -e -A -s clean-japanese-rev1-track01.bin english-dos-track01.bin english-dos.xdelta
xdelta3 -d -s clean-japanese-rev1-track01.bin english-dos.xdelta verified-track01.bin
cmp english-dos-track01.bin verified-track01.bin
```

The clean Japanese Rev 1 input has SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`. The palette-aligned combined data track has SHA-1 `d5eae6826575db1f4404ad8e2a5c8a57c511301c`. The English release relocates movies. The builder appends ten atlas sectors after the English track, updates the ISO volume size and verifies each original executable hook before patching. The Japanese-only patch script's equal-size guard remains specific to that build. For a combined CHD, point a copy of the Japanese CUE at the combined BIN and preserve audio Tracks 2 through 4 and their indexes.

Translation credit and source are available from [Gertius's Ultima Underworld PSX English project](https://github.com/gertius1/UU_PSX_ENG).

The renderer sends an opaque raw-texture quad so that the PlayStation reads the DOS-derived RGB555 palette without a fixed tint. This matches the source sprite colors after quantization. It does not implement DOS distance or torch shading.

The combined build writes the ISO volume label `ULTIMA UNDERWORLD ENGLISH PATCH`. In DuckStation, set the image’s **Game Properties → Summary → Title** to **Ultima Underworld: The Stygian Abyss (English Patch)**. DuckStation uses the original PlayStation serial for its default database title and stores custom titles by file path.

The direction table follows the [DOS renderer reconstruction](https://github.com/abedegno/underworld-exhumed/blob/main/uw1/src/3d/DRAWOBJ.C#L110). At the fixed west-facing test position, a 33.75-degree turn now selects idle slot `0x23` for Lanugo facing east, matching the DOS capture.

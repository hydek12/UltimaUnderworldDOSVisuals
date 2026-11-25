# Lanugo sprite prototype for Japanese Rev 1

Build the Xcode command-line scheme, then use the original Japanese Track 1 and your original DOS installation.

```sh
UnderworldVisuals export-lanugo-tim "/path/to/ultimaunderworld/uu" /tmp/lanugo-atlas
python3 lanugo/build_track.py japan-rev1-track01.bin /tmp/lanugo-atlas lanugo-track01.bin
./build-rev1-patch.sh japan-rev1-track01.bin lanugo-track01.bin lanugo.xdelta
```

The track builder needs Python 3.11 or newer. The patch builder needs xdelta3. The output CHD can be produced with chdman after pointing a copy of the original CUE at the newly patched Track 1. Preserve the three original audio tracks and their index settings.

Lanugo's original model still supplies camera projection bounds and selection geometry. In the idle-only build, the patch suppresses his original model’s two GPU queue insertion paths and submits one textured quad in the same ordering table. The exporter packs 25 unique DOS idle images and maps four entries per facing to them. The renderer uses PSX animation frames 0–6 to select DOS phases 0, 0, 1, 1, 2, 2 and 3. Other PSX actions use their original mesh. It chooses one of eight idle views by comparing Lanugo's heading with camera yaw in 32 sectors, using the original DOS idle-view order, and scales the sprite with the original projected height and hotspot. The rendering functions are specific to Japanese Rev 1.

The loader places the texture and palette in a region that was empty in the captured Level 1 frame. The builder patches an executable region checked against the original BIN and uses initially empty data-track sectors 145980–145993 for the payload. It checks and recomputes Mode 2 Form 1 integrity data. It preserves the size of Track 1 so the CUE can keep its original layout.

Use a fresh boot for comparison since an emulator state may carry the original executable in RAM. Full-game play, hardware testing, and VRAM after a level transition need separate checks.

## Idle and walking sprites

```sh
UnderworldVisuals export-lanugo-walk-tim "/path/to/ultimaunderworld/uu" /tmp/lanugo-walk-atlas
python3 lanugo/build_english.py english-v2-track01.bin /tmp/lanugo-atlas english-dos-walk-track01.bin \
  --walk-atlas /tmp/lanugo-walk-atlas
```

The command exports `lanugo-walk.tim` and `lanugo-walk.csv` from DOS creature 70, slots `0x80` through `0x87`. The CSV records all four phases per facing, including repeated source frames, and the original sprite hotspots. The 30 unique images use 222 rows of a 256×224 atlas. The idle and walk atlases have the same 16 RGB555 values, including transparency, so the 4bpp renderer uses one CLUT for both.

Both disc builders accept the optional `--walk-atlas` argument. This enables DOS sprites for Level 1 creature type 70, which includes Lanugo and two unnamed green goblins. Masked PSX action `0x20` selects the idle texture. Action `0x2c` selects the walk texture after its upload completes. Each seven-frame PSX cycle maps to DOS phases 0, 0, 1, 1, 2, 2, 3. The two atlas textures use the same eight-direction table and their individual hotspots. Attack, hit and death animations use the PSX model. Native uploads that overlap the sprite textures switch rendering back to those models. The Select menu restores the atlases on return to Level 1.

The two-atlas build reads 29 sectors and uploads each texture in two bands from a shared 18 KiB buffer at `0x801f8800`. This keeps live memory near `0x801f8000` out of the transfer. It waits for the GPU after each band before reusing the buffer. Both atlas textures and the palette can be checked against a raw DuckStation GPU capture taken in Lanugo's room.

```sh
zstd -dc capture.psxgpu.zst > capture.psxgpu
python3 lanugo/verify_vram.py capture.psxgpu /tmp/lanugo-atlas /tmp/lanugo-walk-atlas
```

## Four green goblin palettes

Type 70 uses 16 RGB555 values including transparency. The three other palettes for the same DOS artwork use 17 to 23 values. Across the four palettes, 25 distinct index patterns preserve the original color for every pixel. The optional build below uses two 8-bit texture pages and four CLUT rows to preserve those colors. It enables types 70, 76, 77, and 78 on Level 1. Some frames are stored rotated to fit VRAM. Their four UV corners restore their original orientation.

```sh
mkdir -p /tmp/goblin-variants
for type in 76 77 78; do
  UnderworldVisuals export-goblin-atlases DOS_ROOT "$type" "/tmp/goblin-variants/type-$type"
done
python3 lanugo/build_english.py english-v2-track01.bin /tmp/lanugo-atlas english-dos-goblins.bin \
  --walk-atlas /tmp/lanugo-walk-atlas --goblin-variants /tmp/goblin-variants
./build-rev1-patch.sh --allow-expanded-track clean-japanese-rev1-track01.bin \
  english-dos-goblins.bin english-dos-goblins.xdelta
```

For a GPU capture of this build, pass `--goblin-variants /tmp/goblin-variants` to `verify_vram.py`. The four-palette build uses 49 payload sectors. Its second texture page shares VRAM coordinates with native textures on other floors. The render gates check the Level 1 model table before using it.

On DuckStation, crossing the original stairs to Level 2 disabled the sprite atlas. Opening and closing Select there kept it disabled. On climbing back to Level 1, the loader restored both pages and all four palettes. A GPU capture reproduced all 96,512 atlas bytes, and Lanugo’s 32 walking combinations and two idle draws passed again. Inventory and unarmed combat also preserved the atlas.

The final English data track sets the ISO volume label to `ULTIMA UNDERWORLD ENGLISH PATCH`. For a matching title in DuckStation, add the containing directory to its game list and set **Game Properties → Summary → Title** to `Ultima Underworld: The Stygian Abyss (English Patch - DOS Goblins)`. This property is keyed by image path. The original PSX disc serial remains `SLPS-00742`.

## Type 78 goblins on Levels 2, 5, and 7

Add `--lower-floor-goblins` to the English four-palette build command above. The builder appends a second payload for Levels 2, 5, and 7. The loader selects the atlas after loading the native floor and associates it with that floor’s model table. The normal Level 1 atlas is selected when returning upstairs. Main menu exit restores the current atlas if a native GPU upload has invalidated it.

The lower-floor renderer uses two 4-bit pages at VRAM x=384..511, y=256..505, and a CLUT at y=508..509. This leaves the native texture pages at x=512..639 available. A frame with more than 15 opaque colors uses two consecutive opaque textured quads with shared vertices and mutually exclusive texels. Both layers preserve the DOS RGB555 source palette. The substitution covers idle and walk. Other actor actions use their PSX renderer. When combined with `--dos-light-preview`, the DOS lighting applies only on Level 1.

For a GPU frame captured on Levels 2, 5, or 7, pass both `--lower-floor-goblins` and `--goblin-variants /tmp/goblin-variants` to `verify_vram.py`. On Level 1 pass the existing four-palette arguments. Generate the xdelta against the clean Japanese Rev 1 Track 1 through `build-rev1-patch.sh --allow-expanded-track`. Keep the three original audio tracks and their CUE indexes.

## DOS lizardmen on Levels 3 and 4

Export the three DOS lizardman palettes using the Xcode target.

```sh
mkdir -p /tmp/lizardmen
for type in 85 88 89; do
  UnderworldVisuals export-creature-atlases DOS_ROOT "$type" "/tmp/lizardmen/type-$type"
done
```

Add `--lower-floor-goblins --lizardmen /tmp/lizardmen` to the English four-palette build. The renderer selects the lizardman atlas on Levels 3 and 4 and covers native idle and walk actions for types 85, 88, and 89. Each action has eight views and four phases. The three source palettes share one index map. Exact duplicates and horizontal mirrors share texture space, with UVs maintaining the DOS pose and orientation. Each draw uses one 4-bit textured quad and the actor’s own palette.

The lizardman pages occupy x=384..511, y=256..503. Their three CLUT rows occupy x=384..399, y=504..506. Native level textures at x=512..639 remain available. Use `verify_vram.py` with `--lizardmen /tmp/lizardmen` to check both pages and palettes in a GPU capture from either floor. Apply the combined xdelta to clean Japanese Rev 1 Track 1, with the original CUE indexes and audio tracks.

The replacement preserves native model packets until the sprite passes projection and packet-capacity checks. An oversized or otherwise unsupported draw retains the native model. Type 85, 88, and 89 share this behavior with the rat renderer.

To include the optional DOS combat poses, add `--lizardman-combat` to the three Xcode export commands and to `build_english.py` and `verify_vram.py`. The preview covers combat stance, three melee actions, retreat and death. The DOS front-view rule selects a directional standing pose for views other than 3–5 during fixed-view actions. Death uses its fixed animation in all views. The preview maps native phases onto the available DOS frame counts while preserving the original gameplay code and timing. Other actions retain their PSX rendering.

## DOS rats on Level 8

```sh
mkdir -p /tmp/rat-atlases
UnderworldVisuals export-creature-atlases DOS_ROOT 72 /tmp/rat-atlases/type-72
```

Add `--level-eight-rats /tmp/rat-atlases` to the English four-palette build. The atlas covers type 72 idle and walk on Level 8, where their 20 initially linked records use the second DOS rat palette. The patch occupies one page at VRAM x=384..447, y=256..503, with one palette at y=504. Use the same flag in `verify_vram.py` to verify a Level 8 GPU capture.

## DOS lighting preview

To build the separate preview, add `--dos-light-preview DOS_ROOT` to the four-palette `build_english.py` command above. Pass the same argument to `verify_vram.py` with a GPU capture of the preview. The preview packs the normal and monochrome remap tables into 8,192 bytes of PSX CLUTs, with four palette variants per shade. It calculates a shade from signed three-dimensional actor distance before selecting the palette for each quad. The ordinary English DOS Goblins build remains the unshaded reference.

The preview starts at light level 0 to show the DOS game's no-light scene. In a DuckStation debug session, the resident byte at `0x801f6060` selects DOS levels 0–7, including monochrome level 5. The byte is reinitialized on a new Level 1 load. In-game torches, spells, and mushroom effects still need to be connected to this selector. The preview applies to the Level 1 goblin idle and walk sprites. The dungeon and all remaining art use their native lighting.

DuckStation emitted the expected CLUT in 288 controlled draws across the four palettes, all eight light levels, several horizontal distances, and nonzero vertical and lateral offsets. After opening and closing Select, its live VRAM matched both atlas pages and every palette byte.

The cumulative `--dos-shade-maps` recipe uses `0x801f7a00` for its Level 1 light selector because the cumulative room loader uses `0x801f6060` for its dispatch pointer. See the [local builder guide](../docs/local-patch-builder.md#dos-shade-maps-and-monochrome-preview).

## English v2.0 and DOS Lanugo

Use the same DOS atlas exported by the Xcode scheme. Extract the raw Track 1 BIN from the English v2.0 CHD or obtain it by applying Gertius's v2.0 fan translation to clean Japanese Rev 1. The combined builder expects the English Track 1 SHA-1 `325585c11548538e323e8896c3fb8b1cc5d65521`.

```sh
python3 lanugo/build_english.py english-v2-track01.bin /tmp/lanugo-atlas english-dos-track01.bin
./build-rev1-patch.sh --allow-expanded-track clean-japanese-rev1-track01.bin english-dos-track01.bin english-dos.xdelta
xdelta3 -d -s clean-japanese-rev1-track01.bin english-dos.xdelta verified-track01.bin
cmp english-dos-track01.bin verified-track01.bin
```

The clean Japanese Rev 1 input has SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`. The palette-aligned combined data track has SHA-1 `60ccc3b62635aadf48e003e8c9b1ba0eee5e36a4`. The English release relocates movies. The builder appends fourteen sectors for idle or twenty-nine for both atlases after the English track, updates the ISO volume size and verifies each original executable hook before patching. Use `--allow-expanded-track` to package the larger English build with the split-BIN CUE layout. For a combined CHD, point a copy of the Japanese CUE at the combined BIN and preserve audio Tracks 2 through 4 and their indexes.

Translation credit and source are available from [Gertius's Ultima Underworld PSX English project](https://github.com/gertius1/UU_PSX_ENG).

The renderer sends an opaque raw-texture quad so that the PlayStation reads the DOS-derived RGB555 palette without a fixed tint. This matches the source sprite colors after quantization. It does not implement DOS distance or torch shading.

The combined build writes the ISO volume label `ULTIMA UNDERWORLD ENGLISH PATCH`. In DuckStation, set the image’s **Game Properties → Summary → Title** to **Ultima Underworld: The Stygian Abyss (English Patch)**. DuckStation uses the original PlayStation serial for its default database title and stores custom titles by file path.

The direction table follows the [DOS renderer reconstruction](https://github.com/abedegno/underworld-exhumed/blob/main/uw1/src/3d/DRAWOBJ.C#L110). At the fixed west-facing test position, a 33.75-degree turn now selects idle slot `0x23` for Lanugo facing east, matching the DOS capture.

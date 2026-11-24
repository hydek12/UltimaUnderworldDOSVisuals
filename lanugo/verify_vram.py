"""Compare a DuckStation GPU frame capture against both Lanugo texture atlases."""

import argparse
from pathlib import Path
import struct

from build_track import lower_floor_atlas, read_atlas, variant_sources
import lower_atlas
import preview_lighting
import variant_atlas

DUMP_HEADER = b"PSXGPUDUMPv1\0\0"
VRAM_BYTES = 1024 * 512 * 2


def read_vram(dump):
    with dump.open("rb") as capture:
        if capture.read(len(DUMP_HEADER)) != DUMP_HEADER:
            raise ValueError("Expected an uncompressed DuckStation PSX GPU dump.")
        while header := capture.read(4):
            if len(header) != 4:
                raise ValueError("The GPU packet header is truncated.")
            count, packet = int.from_bytes(header[:3], "little"), header[3]
            if packet == 0 and count == 3 + VRAM_BYTES // 4:
                if capture.read(12) != struct.pack("<III", 0xa0000000, 0, 0):
                    raise ValueError("Unexpected initial VRAM upload rectangle.")
                data = capture.read(VRAM_BYTES)
                if len(data) != VRAM_BYTES:
                    raise ValueError("The VRAM upload is truncated.")
                return data
            capture.seek(count * 4, 1)
    raise ValueError("The capture does not contain an initial VRAM upload.")


def expected_rectangles(idle_directory, walk_directory, goblin_variants, dos_light_preview=None,
                        lower_floor_goblins=False):
    if lower_floor_goblins:
        if goblin_variants is None:
            raise ValueError("The lower-floor capture needs --goblin-variants.")
        images, clut, _, _ = lower_floor_atlas(goblin_variants)
        pages = tuple(
            (f"4-bit page {index}", x, y, 64, lower_atlas.HEIGHT, image)
            for index, ((x, y), image) in enumerate(zip(lower_atlas.TEXTURE_PAGES, images, strict=True), start=1)
        )
        return (*pages, ("Type 78 CLUTs", *lower_atlas.CLUT_RECT, clut))
    if dos_light_preview is not None and goblin_variants is None:
        raise ValueError("The DOS lighting preview needs the four-palette goblin atlas.")
    if goblin_variants is not None:
        sources = variant_sources(idle_directory, walk_directory, goblin_variants)
        rectangles = variant_atlas.TEXTURE_PAGES if dos_light_preview is None else preview_lighting.TEXTURE_PAGES
        images, clut, _ = variant_atlas.build(sources, rectangles)
        pages = tuple(
            (f"8-bit page {index}", x, y, variant_atlas.WIDTH // 2, rows, image)
            for index, ((x, y, rows), image) in enumerate(
                zip(rectangles, images, strict=True), start=1
            )
        )
        if dos_light_preview is not None:
            return (*pages, ("DOS shade CLUTs", *preview_lighting.CLUT_RECT,
                             preview_lighting.palette_banks(dos_light_preview, clut)))
        return (*pages, ("Four CLUTs", *variant_atlas.CLUT_RECT, clut))
    colors, idle, _ = read_atlas(idle_directory, "idle", 192, 0x20)
    walk_colors, walk, _ = read_atlas(walk_directory, "walk", 224, 0x80)
    if colors != walk_colors:
        raise ValueError("The atlases do not share an RGB555 palette.")
    return (
        ("Idle texture", 384, 256, 64, 192, idle),
        ("Walk texture", 448, 256, 64, 224, walk),
        ("Shared CLUT", 384, 448, 16, 1, struct.pack("<16H", *colors)),
    )


def verify(dump, idle_directory, walk_directory, goblin_variants=None, dos_light_preview=None,
           lower_floor_goblins=False):
    vram = read_vram(dump)
    rectangles = expected_rectangles(
        idle_directory, walk_directory, goblin_variants, dos_light_preview, lower_floor_goblins,
    )
    valid = True
    for name, x, y, width, height, expected in rectangles:
        start = 2 * (y * 1024 + x)
        observed = b"".join(vram[row:row + 2 * width] for row in range(
            start, start + height * 2048, 2048
        ))
        differences = sum(a != b for a, b in zip(observed, expected))
        print(f"{name}: {len(expected) - differences:,}/{len(expected):,} bytes match")
        valid &= differences == 0
    return valid


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    parser.add_argument("idle_directory", type=Path)
    parser.add_argument("walk_directory", type=Path)
    parser.add_argument("--goblin-variants", type=Path)
    parser.add_argument("--dos-light-preview", type=Path, metavar="DOS_ROOT")
    parser.add_argument("--lower-floor-goblins", action="store_true")
    raise SystemExit(0 if verify(**vars(parser.parse_args())) else 1)

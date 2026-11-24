"""Compare a DuckStation GPU frame capture against both Lanugo texture atlases."""

import argparse
from pathlib import Path
import struct

from build_track import read_atlas, variant_sources
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


def expected_rectangles(idle_directory, walk_directory, goblin_variants):
    if goblin_variants is not None:
        sources = variant_sources(idle_directory, walk_directory, goblin_variants)
        images, clut, _ = variant_atlas.build(sources)
        pages = tuple(
            (f"8-bit page {index}", x, y, variant_atlas.WIDTH // 2, rows, image)
            for index, ((x, y, rows), image) in enumerate(
                zip(variant_atlas.TEXTURE_PAGES, images, strict=True), start=1
            )
        )
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


def verify(dump, idle_directory, walk_directory, goblin_variants=None):
    vram = read_vram(dump)
    rectangles = expected_rectangles(idle_directory, walk_directory, goblin_variants)
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
    raise SystemExit(0 if verify(**vars(parser.parse_args())) else 1)

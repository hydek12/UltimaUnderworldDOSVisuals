"""Share 4-bit DOS creature textures across compatible palette variants."""

import struct

from variant_atlas import WIDTH, pack

LIZARD_TYPES = (85, 88, 89)
LEVEL_EIGHT_RAT_TYPES = (72,)
COMBAT_SLOTS = ((0, 4), (1, 5), (2, 5), (3, 5), (7, 4), (0x0c, 4))
DEATH_SLOT = 0x0c
SOURCE_HEIGHT = 512
TEXTURE_PAGES = ((384, 256, 248), (448, 256, 248))
RAT_TEXTURE_PAGES = TEXTURE_PAGES[:1]
CLUT_RECT = (384, 504, 16, len(LIZARD_TYPES))
CLUT_BASE = (CLUT_RECT[1] << 6) | (CLUT_RECT[0] >> 4)


def combat_actions():
    actions = bytearray([255] * 64)
    for index, slot in enumerate((0x20, 0x2c, *(slot for slot, _ in COMBAT_SLOTS))):
        actions[slot] = index
    phases = bytearray()
    first = 0
    for _, count in COMBAT_SLOTS:
        phases.extend(first + min((frame * count) // 8, count - 1) for frame in range(16))
        first += count
    return bytes(actions), bytes(phases)


def build(sources, texture_pages=TEXTURE_PAGES):
    variant_count = len(sources[0])
    patterns = {(0,) * variant_count}
    frames = {}
    placements = []
    for variants in sources:
        rows = variants[0][1]
        if len(variants) != variant_count or any(metadata != rows for _, metadata in variants):
            raise ValueError("Creature variants must share frame rectangles and hotspots.")
        pixels = tuple(image for image, _ in variants)
        by_rectangle = {}
        for u, v, w, h, hx, hy in rows:
            rect = u, v, w, h
            if rect not in by_rectangle:
                samples = tuple(
                    tuple(zip(*(image[start:start + w] for image in pixels), strict=True))
                    for start in range(v * WIDTH + u, (v + h) * WIDTH + u, WIDTH)
                )
                mirror = tuple(row[::-1] for row in samples)
                canonical = min(samples, mirror)
                flipped = canonical != samples
                if canonical not in frames:
                    frames[canonical] = (len(frames), 0, 0, w, h)
                    patterns.update(color for row in canonical for color in row)
                by_rectangle[rect] = frames[canonical], flipped
            key, flipped = by_rectangle[rect]
            placements.append((key, flipped, (w, h, hx, hy)))
    bank = sorted(patterns)
    if len(bank) > 16:
        raise ValueError("Creature variants require more than sixteen shared palette indices.")
    indices = {colors: index for index, colors in enumerate(bank)}
    textures = dict(pack(frames.values(), texture_pages))
    pages = [bytearray(WIDTH * rows) for _, _, rows in texture_pages]
    for canonical, key in frames.items():
        texture = textures[key]
        height = len(canonical)
        page = pages[texture.page]
        for y, row in enumerate(canonical):
            for x, colors in enumerate(row):
                u, v = (height - 1 - y, x) if texture.rotated else (x, y)
                page[WIDTH * (texture.v + v) + texture.u + u] = indices[colors]
    images = tuple(bytes(lo | hi << 4 for lo, hi in zip(page[::2], page[1::2], strict=True))
                   for page in pages)
    metadata = bytearray()
    for key, flipped, dimensions in placements:
        texture = textures[key]
        w, h, _, _ = dimensions
        corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
        if flipped:
            corners = tuple((w - 1 - x, y) for x, y in corners)
        if texture.rotated:
            corners = tuple((h - 1 - y, x) for x, y in corners)
        uvs = tuple((texture.u + x) | ((texture.v + y) << 8) for x, y in corners)
        page = 0x10 | (texture_pages[texture.page][0] >> 6)
        metadata.extend(struct.pack("<4B4HB3x", *dimensions, *uvs, page))
    clut = b"".join(struct.pack("<16H", *palette, *([0] * (16 - len(palette))))
                    for palette in zip(*bank, strict=True))
    return images, clut, bytes(metadata)

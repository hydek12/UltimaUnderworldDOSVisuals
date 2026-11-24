"""Share 4-bit DOS creature textures across compatible palette variants."""

import struct

from variant_atlas import WIDTH, pack

LIZARD_TYPES = (85, 88, 89)
LEVEL_EIGHT_RAT_TYPES = (72,)
LEVEL_SIX_WIZARD_TYPES = (103, 108, 109)
LEVEL_SIX_SPIDER_TYPE = 92
COMBAT_SLOTS = ((0, 4), (1, 5), (2, 5), (3, 5), (7, 4), (0x0c, 4))
DEATH_SLOT = 0x0c
CAST_SLOT = (0x0d, 5)
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


def wizard_actions(combat=False):
    slots = (*COMBAT_SLOTS, CAST_SLOT) if combat else (CAST_SLOT,)
    actions = bytearray([255] * 64)
    actions[0x20], actions[0x2c] = 0, 1
    phases = bytearray()
    first = 0
    for index, (slot, count) in enumerate(slots, 2):
        actions[slot] = index
        phases.extend(first + min(phase, count - 1) for phase in range(16))
        first += count
    return bytes(actions), bytes(phases)


def build(sources, texture_pages=TEXTURE_PAGES, *, bits=4, scale=16):
    if bits not in (4, 8) or not 1 <= scale <= 16:
        raise ValueError("Unsupported creature texture depth or scale.")
    page_width = WIDTH * 4 // bits
    palette_width = 32 if bits == 8 else 16
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
                scaled_w, scaled_h = max(1, w * scale // 16), max(1, h * scale // 16)
                if scale != 16:
                    samples = tuple(
                        tuple(samples[min(h - 1, (2*j + 1)*h // (2*scaled_h))]
                                     [min(w - 1, (2*i + 1)*w // (2*scaled_w))]
                              for i in range(scaled_w))
                        for j in range(scaled_h)
                    )
                mirror = tuple(row[::-1] for row in samples)
                canonical = min(samples, mirror)
                flipped = canonical != samples
                if canonical not in frames:
                    frames[canonical] = (len(frames), 0, 0, scaled_w, scaled_h)
                    patterns.update(color for row in canonical for color in row)
                by_rectangle[rect] = frames[canonical], flipped
            key, flipped = by_rectangle[rect]
            placements.append((key, flipped, (w, h, hx, hy)))
    bank = sorted(patterns)
    if len(bank) > palette_width:
        raise ValueError(f"Creature variants require more than {palette_width} shared palette indices.")
    indices = {colors: index for index, colors in enumerate(bank)}
    textures = dict(pack(frames.values(), texture_pages, width=page_width))
    pages = [bytearray(page_width * rows) for _, _, rows in texture_pages]
    for canonical, key in frames.items():
        texture = textures[key]
        height = len(canonical)
        page = pages[texture.page]
        for y, row in enumerate(canonical):
            for x, colors in enumerate(row):
                u, v = (height - 1 - y, x) if texture.rotated else (x, y)
                page[page_width * (texture.v + v) + texture.u + u] = indices[colors]
    images = tuple(
        bytes(page) if bits == 8 else bytes(lo | hi << 4 for lo, hi in zip(page[::2], page[1::2], strict=True))
        for page in pages
    )
    metadata = bytearray()
    for key, flipped, dimensions in placements:
        texture = textures[key]
        _, _, _, w, h = key
        corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
        if flipped:
            corners = tuple((w - 1 - x, y) for x, y in corners)
        if texture.rotated:
            corners = tuple((h - 1 - y, x) for x, y in corners)
        uvs = tuple((texture.u + x) | ((texture.v + y) << 8) for x, y in corners)
        page = (0x90 if bits == 8 else 0x10) | (texture_pages[texture.page][0] >> 6)
        metadata.extend(struct.pack("<4B4HB3x", *dimensions, *uvs, page))
    clut = b"".join(struct.pack(f"<{palette_width}H", *palette, *([0] * (palette_width - len(palette))))
                    for palette in zip(*bank, strict=True))
    return images, clut, bytes(metadata)


def build_families(families, page):
    """Pack independent palette banks in one page without sharing palette indices."""
    images, palettes, tables = [], [], []
    # Use the existing family packer for exact palette and layout agreement.
    # Repack its individual indexed rectangles into one shared GPU page.
    candidates = []
    for family in families:
        (image,), clut, table = build(family, (page,))
        images.append(image)
        palettes.extend(clut[i:i + 32] for i in range(0, len(clut), 32))
        tables.append(bytearray(table))
        rects = set()
        for offset in range(0, len(table), 16):
            uv = struct.unpack_from("<4H", table, offset + 4)
            x = min(u & 255 for u in uv)
            y = min(u >> 8 for u in uv)
            w = max(u & 255 for u in uv) - x + 1
            h = max(u >> 8 for u in uv) - y + 1
            rects.add((x, y, w, h))
        candidates.extend((len(images) - 1, *rect) for rect in sorted(rects))
    placements = dict(pack(candidates, (page,)))
    pixels = bytearray(WIDTH * page[2])
    for (family, x, y, w, h), placement in placements.items():
        for j in range(h):
            for i in range(w):
                index = (y + j) * WIDTH + x + i
                color = images[family][index // 2] >> (4 * (index & 1)) & 15
                u, v = (h - 1 - j, i) if placement.rotated else (i, j)
                pixels[(placement.v + v) * WIDTH + placement.u + u] = color
    for family, table in enumerate(tables):
        for offset in range(0, len(table), 16):
            uv = struct.unpack_from("<4H", table, offset + 4)
            xs, ys = [u & 255 for u in uv], [u >> 8 for u in uv]
            x, y = min(xs), min(ys)
            h = max(ys) - y + 1
            placement = placements[family, x, y, max(xs) - x + 1, h]
            corners = [(u - x, v - y) for u, v in zip(xs, ys, strict=True)]
            if placement.rotated:
                corners = [(h - 1 - v, u) for u, v in corners]
            struct.pack_into("<4H", table, offset + 4, *(
                placement.u + u | (placement.v + v) << 8 for u, v in corners
            ))
    image = bytes(lo | hi << 4 for lo, hi in zip(pixels[::2], pixels[1::2], strict=True))
    return image, palettes, tables


def compact_frame_table(table):
    """Index unique directional entries and omit their final two padding bytes."""
    keys = {}
    indices = bytearray()
    for offset in range(0, len(table), 16):
        entry = bytes(table[offset:offset + 14])
        indices.append(keys.setdefault(entry, len(keys)))
    if len(indices) != 64:
        raise ValueError("Expected four phases in each idle and walking direction.")
    return bytes(indices) + b"".join(keys)

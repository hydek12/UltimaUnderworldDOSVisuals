"""Pack the four DOS green goblin palettes into two shared 8-bit texture pages."""

from collections import namedtuple
import struct

GOBLIN_TYPES = (70, 76, 77, 78)
WIDTH = 256
# x and y in VRAM words, and the number of available pixel rows.
TEXTURE_PAGES = ((384, 256, 248), (512, 384, 128))
CLUT_RECT = (384, 504, 32, len(GOBLIN_TYPES))
Texture = namedtuple("Texture", "page u v width height rotated")


def subtract(free, placed):
    page, x, y, width, height = placed
    right, bottom = x + width, y + height
    fragments = []
    for current_page, fx, fy, fw, fh in free:
        fr, fb = fx + fw, fy + fh
        if current_page != page or right <= fx or fr <= x or bottom <= fy or fb <= y:
            fragments.append((current_page, fx, fy, fw, fh))
            continue
        for left, top, w, h in (
            (fx, fy, x - fx, fh),
            (right, fy, fr - right, fh),
            (fx, fy, fw, y - fy),
            (fx, bottom, fw, fb - bottom),
        ):
            if w > 0 and h > 0:
                fragments.append((page, left, top, w, h))
    rectangles = tuple(dict.fromkeys(fragments))
    return [
        rect for rect in rectangles
        if not any(
            other != rect and other[0] == rect[0] and other[1] <= rect[1] and other[2] <= rect[2]
            and other[1] + other[3] >= rect[1] + rect[3]
            and other[2] + other[4] >= rect[2] + rect[4]
            for other in rectangles
        )
    ]


class AtlasDoesNotFit(ValueError):
    pass


def pack(frames, texture_pages, width=WIDTH, *, scale=16):
    free = [(page, 0, 0, width, rows) for page, (_, _, rows) in enumerate(texture_pages)]
    for frame in sorted(frames, key=lambda item: (-item[4], -item[3], item)):
        _, _, _, width, height = frame
        width, height = max(1, width * scale // 16), max(1, height * scale // 16)
        choices = (
            (min(fw - w, fh - h), max(fw - w, fh - h), page, y, x, rotated, w, h)
            for rotated, w, h in ((False, width, height), (True, height, width))
            for page, x, y, fw, fh in free if w <= fw and h <= fh
        )
        best = min(choices, default=None)
        if best is None:
            raise AtlasDoesNotFit("The green goblin frames do not fit the two Level 1 VRAM regions.")
        _, _, page, y, x, rotated, w, h = best
        yield frame, Texture(page, x, y, w, h, rotated)
        free = subtract(free, (page, x, y, w, h))


def frame_metadata(texture, texture_pages, width, height, hotspot_x, hotspot_y):
    page_x, page_y, _ = texture_pages[texture.page]
    u = texture.u
    v = texture.v + page_y - 256
    right, bottom = u + texture.width - 1, v + texture.height - 1
    if texture.rotated:
        corners = ((right, v), (right, bottom), (u, v), (u, bottom))
    else:
        corners = ((u, v), (right, v), (u, bottom), (right, bottom))
    page_command = 0x90 | (page_x >> 6)  # 8 bits per pixel on the page at y=256.
    uv = [x | (y << 8) for x, y in corners]
    return struct.pack("<4B4HB3x", width, height, hotspot_x, hotspot_y, *uv, page_command)


def build(sources, texture_pages=TEXTURE_PAGES, *, minimum_scale=16):
    # The four exported atlases have identical rectangles and hotspots.
    palettes_by_mode = []
    metadata_by_mode = []
    for variants in sources:
        frame_rows = variants[0][1]
        if any(rows != frame_rows for _, rows in variants):
            raise ValueError("Green goblin variants must share identical frame layouts and hotspots.")
        palettes_by_mode.append(tuple(zip(*(pixels for pixels, _ in variants), strict=True)))
        metadata_by_mode.append(frame_rows)
    transparent = (0,) * len(GOBLIN_TYPES)
    patterns = sorted(set().union(*palettes_by_mode))
    if not patterns or patterns[0] != transparent or len(patterns) > CLUT_RECT[2]:
        raise ValueError("The joint DOS palette does not fit the reserved CLUT rows.")
    indices = {colors: index for index, colors in enumerate(patterns)}
    pages = [bytearray(WIDTH * rows) for _, _, rows in texture_pages]
    frames = {
        (mode, u, v, width, height)
        for mode, rows in enumerate(metadata_by_mode)
        for u, v, width, height, _, _ in rows
    }
    for scale in range(16, minimum_scale - 1, -1):
        try:
            textures = dict(pack(frames, texture_pages, scale=scale))
            break
        except AtlasDoesNotFit:
            if scale == minimum_scale:
                raise
    for (mode, src_u, src_v, width, height), texture in textures.items():
        dest = pages[texture.page]
        source = palettes_by_mode[mode]
        width_out, height_out = max(1, width * scale // 16), max(1, height * scale // 16)
        for y in range(height_out):
            for x in range(width_out):
                u, v = (height_out - 1 - y, x) if texture.rotated else (x, y)
                index = (texture.v + v) * WIDTH + texture.u + u
                source_x, source_y = x * width // width_out, y * height // height_out
                dest[index] = indices[source[(src_v + source_y) * WIDTH + src_u + source_x]]
    metadata = b"".join(
        frame_metadata(textures[mode, u, v, w, h], texture_pages, w, h, hx, hy)
        for mode, rows in enumerate(metadata_by_mode)
        for u, v, w, h, hx, hy in rows
    )
    palette_rows = list(zip(*patterns, strict=True))
    clut = b"".join(struct.pack("<32H", *row, *([0] * (32 - len(row)))) for row in palette_rows)
    return tuple(map(bytes, pages)), clut, metadata

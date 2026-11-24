"""Pack the DOS type 78 goblin into two 4-bit pages left of the native textures."""

from collections import namedtuple
from itertools import combinations, groupby
import struct

from variant_atlas import WIDTH, subtract

TEXTURE_PAGES = ((384, 256), (448, 256))
HEIGHT = 250
CLUT_RECT = (384, 508, 128, 2)
EMPTY = 16
Placement = namedtuple("Placement", "page u v transpose")


def palette(image):
    return tuple(sorted({0} | {color for row in image for color in row}))


def split_colors(image):
    bounds = {}
    for y, row in enumerate(image):
        for x, color in enumerate(row):
            if color == 0:
                continue
            l, t, r, b = bounds.get(color, (x, y, x, y))
            bounds[color] = min(l, x), min(t, y), max(r, x), max(b, y)
    if len(bounds) <= 15:
        return image, ()

    def area(colors):
        rectangles = [bounds[color] for color in colors]
        l = min(rect[0] for rect in rectangles)
        t = min(rect[1] for rect in rectangles)
        r = max(rect[2] for rect in rectangles)
        b = max(rect[3] for rect in rectangles)
        return (r - l + 1) * (b - t + 1)

    overlay = set(min(combinations(sorted(bounds), len(bounds) - 15), key=area))
    primary = tuple(tuple(0 if color in overlay else color for color in row) for row in image)
    secondary = tuple(tuple(color if color in overlay else 0 for color in row) for row in image)
    return primary, secondary


def indices(image, colors):
    lookup = {color: index for index, color in enumerate(colors)}
    return tuple(bytes(lookup[color] for color in row) for row in image)


def orient(image, transpose):
    if transpose:
        return tuple(bytes(row) for row in zip(*image, strict=True))
    return image


def spread(mask, width):
    length = 1
    while length * 2 < width:
        mask |= mask >> length
        length *= 2
    return mask | (mask >> (width - length))


class Page:
    def __init__(self):
        self.rows = [bytearray([EMPTY]) * WIDTH for _ in range(HEIGHT)]
        self.assigned = [0] * HEIGHT
        self.values = [[0] * 16 for _ in range(HEIGHT)]

    def place(self, image, x, y):
        coverage = ((1 << len(image[0])) - 1) << x
        for offset, row in enumerate(image, y):
            colors = self.rows[offset]
            for col, value in enumerate(row, x):
                if colors[col] not in (EMPTY, value):
                    raise ValueError("Goblin layers conflict in the texture atlas.")
                colors[col] = value
                self.values[offset][value] |= 1 << col
            self.assigned[offset] |= coverage

    def overlay_positions(self, image):
        width, height = len(image[0]), len(image)
        runs = []
        for row in image:
            start = 0
            row_runs = []
            for value, pixels in groupby(row):
                length = sum(1 for _ in pixels)
                row_runs.append((value, start, length))
                start += length
            runs.append(row_runs)
        mask = (1 << (WIDTH - width + 1)) - 1
        footprint = (1 << width) - 1
        for y in range(HEIGHT - height + 1):
            allowed = mask
            for offset, row_runs in enumerate(runs, y):
                assigned, values = self.assigned[offset], self.values[offset]
                for value, start, length in row_runs:
                    forbidden = spread(assigned ^ values[value], length) >> start
                    allowed &= ~forbidden
                if not allowed:
                    break
            while allowed:
                after = allowed & (allowed - 1)
                x = (allowed ^ after).bit_length() - 1
                region = footprint << x
                shared = sum((row & region).bit_count() for row in self.assigned[y:y + height])
                yield -shared, y, x
                allowed = after

    def packed(self):
        return bytes((left & 15) | ((right & 15) << 4)
                     for row in self.rows for left, right in zip(row[::2], row[1::2], strict=True))


def pack_layers(frames):
    pages = [Page() for _ in TEXTURE_PAGES]
    free = [(page, 0, 0, WIDTH, HEIGHT) for page in range(len(pages))]
    first, second = {}, {}
    for key in sorted(frames, key=lambda item: (-item[4], -item[3])):
        image = frames[key][0]
        w, h = key[3:5]
        choices = (
            (min(fw - width, fh - height), max(fw - width, fh - height), page, y, x, transpose, width, height)
            for transpose, width, height in ((False, w, h), (True, h, w))
            for page, x, y, fw, fh in free if width <= fw and height <= fh
        )
        best = min(choices, default=None)
        if best is None:
            raise ValueError("The full-size goblin sprite frames do not fit the lower-floor texture pages.")
        _, _, page, y, x, transpose, width, height = best
        pages[page].place(orient(image, transpose), x, y)
        first[key] = Placement(page, x, y, transpose)
        free = subtract(free, (page, x, y, width, height))

    overflow = [key for key, layers in frames.items() if layers[1]]
    for key in sorted(overflow, key=lambda item: -sum(value != 0 for row in frames[item][1] for value in row)):
        transpose = first[key].transpose
        image = orient(frames[key][1], transpose)
        choices = ((shared, page, y, x)
                   for page, atlas in enumerate(pages) for shared, y, x in atlas.overlay_positions(image))
        best = min(choices, default=None)
        if best is None:
            raise ValueError("The full-size goblin palette overlays do not fit the lower-floor texture pages.")
        _, page, y, x = best
        pages[page].place(image, x, y)
        second[key] = Placement(page, x, y, transpose)
    return tuple(page.packed() for page in pages), first, second


def sprite_metadata(placement, dimensions, clut):
    w, h, _, _ = dimensions
    page, u, v, transpose = placement
    corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
    if transpose:
        corners = tuple((y, x) for x, y in corners)
    uv = [(x + u) | ((y + v) << 8) for x, y in corners]
    tpage = 0x10 | (TEXTURE_PAGES[page][0] >> 6)
    return struct.pack("<4B4HBxH", *dimensions, *uv, tpage, clut)


def build(sources):
    frames = {}
    order = []
    for action, (pixels, metadata) in enumerate(sources):
        for x, y, w, h, hx, hy in metadata:
            key = action, x, y, w, h
            order.append((key, (w, h, hx, hy)))
            if key not in frames:
                image = tuple(pixels[(y + row) * WIDTH + x:(y + row) * WIDTH + x + w] for row in range(h))
                frames[key] = split_colors(image)
    colors = {key: tuple(palette(image) if image else () for image in layers) for key, layers in frames.items()}
    bank = sorted({p for pair in colors.values() for p in pair if p})
    x, y, width, height = CLUT_RECT
    cluts_per_row = width // 16
    size = cluts_per_row * height
    if len(bank) > size:
        raise ValueError("The lower-floor palettes do not fit the reserved CLUT rectangle.")
    clut_ids = {pal: ((y + i // cluts_per_row) << 6) | (x // 16 + i % cluts_per_row)
                for i, pal in enumerate(bank)}
    bank.extend([()] * (size - len(bank)))
    clut = b"".join(struct.pack("<16H", *pal, *([0] * (16 - len(pal)))) for pal in bank)
    indexed = {key: tuple(indices(image, pal) if image else () for image, pal in zip(layers, colors[key], strict=True))
               for key, layers in frames.items()}
    images, first, second = pack_layers(indexed)
    metadata = b"".join(sprite_metadata(first[key], dims, clut_ids[colors[key][0]]) for key, dims in order)
    layers = b"".join(sprite_metadata(second[key], dims, clut_ids[colors[key][1]]) if key in second else bytes(16)
                      for key, dims in order)
    return images, clut, metadata, layers

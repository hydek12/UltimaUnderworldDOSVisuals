"""Replace the verified Rev 1 spell graphics inside their original TIM sheets."""
import hashlib
from struct import pack_into, unpack_from

from build_track import AVATAR_LBA, form1_sector, read_sector

PALETTE = 20
PIXELS = 544
STRIDE = 256
IMPACT_TABLE = 2048 + 0x800AF2BC - 0x80010000
PROJECTILE_TABLE = 2048 + 0x800AEDBC - 0x80010000
IMPACT_SHEET = (0x2F0800, 160, "f64127cfc8368ee32f2a7f3a32afeff88424a46122e9c13d72b340ca0895e4fb")
OBJECT_SHEET = (0x2FB000, 256, "3cd2b05b9bf6f99861d0ea592c165058d938a2a1d7061a8cdb0d45caaa406d6b")


class Sheet:
    def __init__(self, source, spec):
        offset, height, digest = spec
        self.lba = AVATAR_LBA + offset // 2048
        size = PIXELS + STRIDE * height
        # Include the object resource's 12-byte trailer in its baseline check.
        if spec == OBJECT_SHEET:
            size += 12
        self.sectors = [read_sector(source, self.lba + i) for i in range((size + 2047) // 2048)]
        self.data = bytearray(b"".join(sector[24:2072] for sector in self.sectors))
        if hashlib.sha256(self.data[:size]).hexdigest() != digest:
            raise ValueError(f"Unexpected original TIM resource at LBA {self.lba}.")

    def offsets(self, rect):
        x, y, width, height = rect
        return [PIXELS + (y + row) * STRIDE + x + column
                for row in range(height) for column in range(width)]

    def color(self, index):
        return unpack_from("<H", self.data, PALETTE + index * 2)[0]

    def apply(self, rect, pixels, indices):
        for offset, color in zip(self.offsets(rect), pixels, strict=True):
            self.data[offset] = indices[color]

    def add_updates(self, updates):
        for i, original in enumerate(self.sectors):
            start = i * 2048
            data = self.data[start:start + 2048]
            if data != original[24:2072]:
                if form1_sector(original, original[24:2072]) != original:
                    raise ValueError(f"Invalid source TIM sector at LBA {self.lba+i}.")
                updates[self.lba + i] = form1_sector(original, data)


def load_frame(folder, name, frame):
    raw = (folder / f"{name}-{frame}.rgb555").read_bytes()
    if len(raw) < 2:
        raise ValueError(f"Truncated DOS frame {name} {frame}.")
    width, height = raw[:2]
    if not width or not height or len(raw) != 2 + width * height * 2:
        raise ValueError(f"Invalid DOS frame {name} {frame}.")
    return width, height, unpack_from(f"<{width * height}H", raw, 2)


def apply(source, executable, updates, folder):
    exe = bytearray(executable)
    objects = Sheet(source, OBJECT_SHEET)
    projectiles = [
        (item, load_frame(folder, name, 0))
        for item, name in ((0x14, "fireball"), (0x15, "lightning-bolt"), (0x17, "magic-missile"))
    ]
    # The flight packet is opaque. Match RGB555 and leave shared CLUT entries intact.
    free_entries = (179, 188, 0)
    indices = {objects.color(i): i for i in range(256) if i not in free_entries}
    free = iter(free_entries)
    for item, (width, height, pixels) in projectiles:
        rect = unpack_from("<4B", exe, PROJECTILE_TABLE + 4 * item)
        if rect[2:] != (width, height):
            raise ValueError(f"DOS projectile {item:#x} does not fit its Rev 1 rectangle.")
        rgb = tuple((color & 0x7FFF) or color for color in pixels)
        for color in sorted(set(rgb).difference(indices)):
            index = next(free, None)
            if index is None:
                raise ValueError("DOS projectile colors exceed the verified free CLUT entries.")
            pack_into("<H", objects.data, PALETTE + 2 * index, color)
            indices[color] = index
        objects.apply(rect, rgb, indices)

    impacts = Sheet(source, IMPACT_SHEET)
    indices = {impacts.color(i): i for i in range(176)}
    free = iter(range(176, 256))
    # Reserve blank space below the existing graphics. Relocate the smaller
    # DOS flames so adjacent or overlapping native rectangles stay intact.
    next_x = 160
    for name, first, count in (
        ("fireball-impact", 21, 5), ("fireball-flame-1", 26, 5),
        ("fireball-flame-2", 31, 5), ("lightning-impact", 50, 3)
    ):
        for phase in range(count):
            pos = IMPACT_TABLE + 6 * (first + phase)
            rect = unpack_from("<4B", exe, pos)
            width, height, pixels = load_frame(folder, name, phase)
            if first == 21:
                original = tuple(impacts.color(impacts.data[i]) for i in impacts.offsets(rect))
                if rect[2:] != (width, height) or original != pixels:
                    raise ValueError(f"DOS Fireball center frame {phase} differs from its verified original.")
                continue
            if first in (26, 31):
                rect = (next_x, 110, width, height)
                # This sheet starts at GPU V=96. The metadata stores sheet-relative V.
                if next_x + width > STRIDE or height > 12 or any(
                    impacts.data[i] != 175 for i in impacts.offsets(rect)
                ):
                    raise ValueError("DOS flame frames do not fit the verified transparent area.")
                pack_into("<4B", exe, pos, *rect)
                next_x += width
            elif rect[2:] != (width, height):
                raise ValueError("DOS lightning impact does not fit its Rev 1 rectangle.")
            for color in sorted(set(pixels).difference(indices)):
                index = next(free, None)
                if index is None:
                    raise ValueError("DOS impact colors exceed the available CLUT entries.")
                pack_into("<H", impacts.data, PALETTE + 2 * index, color)
                indices[color] = index
            impacts.apply(rect, pixels, indices)
    objects.add_updates(updates)
    impacts.add_updates(updates)
    return exe

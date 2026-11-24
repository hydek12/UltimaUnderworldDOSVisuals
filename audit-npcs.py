"""Inventory live DOS dungeon actors and candidate Japanese Rev 1 record matches."""

import argparse
import csv
from pathlib import Path
import struct
import sys

TILES_PER_LEVEL = 64 * 64
MOBILE_RECORD_BYTES = 27
STATIC_RECORD_BYTES = 8
MOBILE_SLOTS = 256
PSX_OBJECT_ENTRY = 133
PSX_RECORD_BYTES = 28
DOS_CREATURE_RANGE = range(64, 128)


def word(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def dos_actors(level_archive):
    for level, offset in enumerate(struct.unpack_from("<9I", level_archive, 2), start=1):
        table = offset + 4 * TILES_PER_LEVEL
        if not offset or table + MOBILE_SLOTS * MOBILE_RECORD_BYTES > len(level_archive):
            raise ValueError(f"Invalid DOS tile or object table for level {level}.")
        found = set()
        for tile in range(TILES_PER_LEVEL):
            slot = word(level_archive, offset + 4 * tile + 2) >> 6
            chain = set()
            while slot and slot not in chain:
                chain.add(slot)
                if slot < MOBILE_SLOTS:
                    address = table + MOBILE_RECORD_BYTES * slot
                    actor = word(level_archive, address) & 511
                    if actor in DOS_CREATURE_RANGE and slot not in found:
                        found.add(slot)
                        record = level_archive[address:address + MOBILE_RECORD_BYTES]
                        yield level, tile % 64, tile // 64, slot, actor, address, record
                else:
                    address = table + MOBILE_SLOTS * MOBILE_RECORD_BYTES
                    address += STATIC_RECORD_BYTES * (slot - MOBILE_SLOTS)
                slot = word(level_archive, address + 4) >> 6


def slot_frames(page):
    first, count = page[:2]
    segments = page[2 + count]
    by_slot = {}
    for index in range(count):
        segment = page[2 + index]
        if segment < segments:
            start = 3 + count + 8 * segment
            by_slot[first + index] = sum(frame != 255 for frame in page[start:start + 8])
    return by_slot


def asset_coverage(crit):
    associations = (crit / "ASSOC.ANM").read_bytes()
    if len(associations) != 384:
        raise ValueError("Expected the 384-byte DOS creature association table.")
    pages = {}
    for actor in DOS_CREATURE_RANGE:
        start = 256 + 2 * (actor - DOS_CREATURE_RANGE.start)
        animation, palette = associations[start:start + 2]
        if animation >= 32:
            continue
        if animation not in pages:
            slots = {}
            for index in range(2):
                page = crit / f"CR{animation:02o}PAGE.N{index:02o}"
                if page.is_file():
                    slots.update(slot_frames(page.read_bytes()))
            pages[animation] = slots
        slots = pages[animation]
        label = associations[8 * animation:8 * (animation + 1)].rstrip(b"\0").decode("ascii")
        idle = tuple(slots.get(slot, 0) for slot in range(0x20, 0x28))
        walk = tuple(slots.get(slot, 0) for slot in range(0x80, 0x88))
        yield actor, (animation, label, palette, idle, walk)


def record_offsets(objects, base, dos_record):
    # The first six bytes, packed home tile, and conversation ID survive the port.
    signature = dos_record[:6]
    position = 0
    while (position := objects.find(signature, position)) != -1:
        end = position + PSX_RECORD_BYTES
        record = objects[position:end]
        if len(record) == PSX_RECORD_BYTES and record[20:22] == dos_record[22:24]:
            if record[26] == dos_record[26]:
                yield base + position
        position += 1


def audit(dos_root, psx_avatar):
    levels = (dos_root / "DATA" / "LEV.ARK").read_bytes()
    assets = dict(asset_coverage(dos_root / "CRIT"))
    avatar = psx_avatar.read_bytes()
    base, end = struct.unpack_from("<II", avatar, 4 * PSX_OBJECT_ENTRY)
    if (base, end) != (0x9a4000, 0x9b3000):
        raise ValueError("Expected the clean Japanese Rev 1 AVATAR object entry.")
    objects = avatar[base:end]
    writer = csv.writer(sys.stdout)
    writer.writerow((
        "level", "tile_x", "tile_y", "dos_slot", "dos_type", "conversation_id", "dos_record_offset",
        "psx_candidate_offsets", "dos_animation", "dos_asset", "dos_palette",
        "idle_frames_by_direction", "walk_frames_by_direction",
    ))
    for level, x, y, slot, actor, address, record in dos_actors(levels):
        matches = " ".join(f"{offset:#08x}" for offset in record_offsets(objects, base, record))
        animation, label, palette, idle, walk = assets.get(actor, ("", "", "", (), ()))
        writer.writerow((
            level, x, y, slot, actor, record[26], f"{address:#08x}", matches, animation, label, palette,
            " ".join(map(str, idle)), " ".join(map(str, walk)),
        ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dos_root", type=Path)
    parser.add_argument("psx_avatar", type=Path)
    audit(**vars(parser.parse_args()))

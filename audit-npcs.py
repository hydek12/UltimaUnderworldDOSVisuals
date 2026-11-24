"""Inventory live DOS dungeon actors and candidate Japanese Rev 1 record matches."""

import argparse
from collections import defaultdict
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


def psx_creatures(avatar, object_range=(0x9a4000, 0x9b3000)):
    base, end = struct.unpack_from("<II", avatar, 4 * PSX_OBJECT_ENTRY)
    if (base, end) != object_range or end > len(avatar):
        raise ValueError("Unexpected AVATAR object entry for this disc revision.")
    previous_end = base + 9 * 8
    for level in range(1, 10):
        # Loader 0x8004b034 takes the low halfword count and shifts word +4 by ten.
        count, _, packed_offset = struct.unpack_from("<HHI", avatar, base + (level - 1) * 8)
        start = base + (packed_offset >> 10)
        stop = start + PSX_RECORD_BYTES * count
        if not 0 < count < MOBILE_SLOTS or not previous_end <= start < stop <= end:
            raise ValueError(f"Invalid PSX mobile record table for level {level}.")
        for address in range(start, stop, PSX_RECORD_BYTES):
            record = avatar[address:address + PSX_RECORD_BYTES]
            actor = word(record, 0) & 511
            if actor not in DOS_CREATURE_RANGE:
                raise ValueError(f"Unexpected PSX creature type {actor} at {address:#x}.")
            yield level, address, actor, record
        previous_end = stop


def crosswalk(dos_records, psx_records):
    by_identity = defaultdict(list)
    for level, address, actor, record in psx_records:
        by_identity[level, actor, record[26]].append((address, record))
    matches = {}
    reserved = set()
    for level, _, _, _, actor, address, record in dos_records:
        candidates = by_identity[level, actor, record[26]]
        exact = tuple(psx_address for psx_address, psx in candidates
                      if psx[:6] == record[:6] and psx[20:22] == record[22:24])
        if exact:
            matches[address] = ("exact", exact)
            reserved.update(exact)
    for level, x, y, _, actor, address, record in dos_records:
        if address in matches:
            continue
        candidates = [(psx_address, psx) for psx_address, psx in by_identity[level, actor, record[26]]
                      if psx_address not in reserved]
        same_tile = tuple(psx_address for psx_address, psx in candidates
                          if (word(psx, 4) & 63, word(psx, 6) & 63) == (x, y))
        if same_tile:
            matches[address] = ("spawn tile", same_tile)
        elif record[26] not in (0, 255) and len(candidates) == 1:
            matches[address] = ("conversation ID", (candidates[0][0],))
    return matches


def asset_columns(assets, actor):
    animation, label, palette, idle, walk = assets.get(actor, ("", "", "", (), ()))
    return animation, label, palette, " ".join(map(str, idle)), " ".join(map(str, walk))


def dos_personal_names(strings, identities):
    """Read only the personal-name entries in DOS string block 7."""
    node_count = word(strings, 0)
    directory = 2 + 4 * node_count
    if not 1 <= node_count <= 256:
        raise ValueError("Unexpected DOS string tree size.")
    blocks = dict(struct.iter_unpack("<HI", strings[directory + 2:directory + 2 + 6 * word(strings, directory)]))
    block = blocks[7]
    count = word(strings, block)
    offsets = block + 2
    text = offsets + 2 * count
    end = min((offset for offset in blocks.values() if offset > block), default=len(strings))
    for identity in sorted(identities):
        index = identity + 16
        if index >= count:
            continue
        start = text + word(strings, offsets + 2 * index)
        node = node_count - 1
        name = bytearray()
        for value in strings[start:end]:
            for bit in range(7, -1, -1):
                node = strings[2 + 4 * node + 2 + ((value >> bit) & 1)]
                if node >= node_count:
                    raise ValueError("Invalid DOS string tree child.")
                char, _, left, _ = strings[2 + 4 * node:6 + 4 * node]
                if left != 255:
                    continue
                if char in (ord("|"), 255):
                    break
                name.append(char)
                if len(name) >= 512:
                    raise ValueError("DOS personal name exceeds the string limit.")
                node = node_count - 1
            else:
                continue
            break
        else:
            raise ValueError("DOS personal name is unterminated.")
        personal_name = name.decode("cp437").strip()
        if personal_name:
            yield identity, personal_name


def dialogue_inventory(dos_root, psx_avatar, english_avatar=None):
    data_root = dos_root / "DATA"
    dos_records = list(dos_actors((data_root / "LEV.ARK").read_bytes()))
    psx_records = list(psx_creatures(psx_avatar.read_bytes()))
    english_records = {}
    english_shift = 0x100000
    if english_avatar is not None:
        english_records = {
            (level, address - english_shift): record
            for level, address, _, record in psx_creatures(english_avatar.read_bytes(), (0xaa4000, 0xab3000))
        }
    matched = crosswalk(dos_records, psx_records)
    identities = {record[26] for _, _, _, record in psx_records if 0 < record[26] < 0xf0}
    names = dict(dos_personal_names((data_root / "STRINGS.PAK").read_bytes(), identities))
    archive = (data_root / "CNV.ARK").read_bytes()
    offsets = struct.unpack_from(f"<{word(archive, 0)}I", archive, 2)
    assets = dict(asset_coverage(dos_root / "CRIT"))
    by_identity = defaultdict(list)
    for level, x, y, _, actor, address, record in dos_records:
        by_identity[record[26]].append((level, x, y, actor, address))
    writer = csv.writer(sys.stdout)
    writer.writerow(("level", "psx_record_offset", "psx_type", "conversation_id", "initially_linked",
                     "spawn_x", "spawn_y", "dos_name", "dos_script", "dos_level", "dos_spawn_x",
                     "dos_spawn_y", "dos_type", "dos_record_offset", "match_evidence", "dos_asset",
                     "dos_palette", "idle_frames_by_direction", "walk_frames_by_direction", "english_record_match"))
    for level, address, actor, record in psx_records:
        identity = record[26]
        if identity not in identities:
            continue
        script = identity < len(offsets) and 2 + 4 * len(offsets) <= offsets[identity] < len(archive)
        peers = by_identity[identity]
        strict = [(peer, matched[peer[-1]][0]) for peer in peers
                  if peer[-1] in matched and address in matched[peer[-1]][1]]
        if len(strict) == 1:
            candidate, evidence = strict[0]
        elif not strict and len(peers) == 1:
            candidate, evidence = peers[0], "unique DOS identity; verify in PSX dialogue"
        else:
            candidate, evidence = None, "ambiguous match" if peers else "no linked DOS record"
        if candidate:
            dos_level, dos_x, dos_y, dos_type, dos_offset = candidate
            _, asset, palette, idle, walk = asset_columns(assets, dos_type)
            detail = dos_level, dos_x, dos_y, dos_type, f"{dos_offset:#08x}", evidence, asset, palette, idle, walk
        else:
            detail = "", "", "", "", "", evidence, "", "", "", ""
        writer.writerow((level, f"{address:#08x}", actor, identity, int(bool(record[27])),
                         word(record, 4) & 63, word(record, 6) & 63,
                         names.get(identity, ""), int(script), *detail,
                         "" if english_avatar is None else int(english_records.get((level, address)) == record)))


def audit(dos_root, psx_avatar, psx_inventory=False):
    levels = (dos_root / "DATA" / "LEV.ARK").read_bytes()
    assets = dict(asset_coverage(dos_root / "CRIT"))
    dos_records = list(dos_actors(levels))
    psx_records = list(psx_creatures(psx_avatar.read_bytes()))
    matches = crosswalk(dos_records, psx_records)
    writer = csv.writer(sys.stdout)
    if psx_inventory:
        dos_candidates = defaultdict(list)
        for dos_address, (_, addresses) in matches.items():
            for address in addresses:
                dos_candidates[address].append(dos_address)
        writer.writerow((
            "level", "psx_record_offset", "psx_type", "conversation_id", "initially_linked",
            "spawn_x", "spawn_y", "home_x", "home_y", "dos_candidate_offsets", "dos_animation",
            "dos_asset", "dos_palette", "idle_frames_by_direction", "walk_frames_by_direction",
        ))
        for level, address, actor, record in psx_records:
            home = word(record, 20)
            writer.writerow((
                level, f"{address:#08x}", actor, record[26], int(bool(record[27])),
                word(record, 4) & 63, word(record, 6) & 63, home >> 10, (home >> 4) & 63,
                " ".join(f"{offset:#08x}" for offset in dos_candidates[address]),
                *asset_columns(assets, actor),
            ))
        return
    writer.writerow((
        "level", "tile_x", "tile_y", "dos_slot", "dos_type", "conversation_id", "dos_record_offset",
        "psx_candidate_offsets", "dos_animation", "dos_asset", "dos_palette",
        "idle_frames_by_direction", "walk_frames_by_direction", "match_evidence",
    ))
    for level, x, y, slot, actor, address, record in dos_records:
        evidence, addresses = matches.get(address, ("", ()))
        writer.writerow((
            level, x, y, slot, actor, record[26], f"{address:#08x}",
            " ".join(f"{offset:#08x}" for offset in addresses), *asset_columns(assets, actor), evidence,
        ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dos_root", type=Path)
    parser.add_argument("psx_avatar", type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--psx-inventory", action="store_true", help="List every PSX creature record.")
    modes.add_argument("--dialogue-inventory", action="store_true", help="Match PSX dialogue records to local DOS names.")
    parser.add_argument("--english-avatar", type=Path, help="Compare relocated records in the English v2.0 AVATAR.")
    args = parser.parse_args()
    if args.english_avatar and not args.dialogue_inventory:
        parser.error("--english-avatar requires --dialogue-inventory")
    if args.dialogue_inventory:
        dialogue_inventory(args.dos_root, args.psx_avatar, args.english_avatar)
    else:
        audit(args.dos_root, args.psx_avatar, args.psx_inventory)

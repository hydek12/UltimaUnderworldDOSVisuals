#!/usr/bin/env python3
"""Report sprite registration at archive spawn views in the cumulative release and combat preview."""

import argparse
import csv
import mmap
import re
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lanugo"))
import academy_banks as banks
import build_track as track
import creature_atlas as creatures
import variant_atlas

FIXED_ACTIONS = tuple(action for action, _ in (*creatures.COMBAT_SLOTS, creatures.CAST_SLOT))
ARCHIVE_ONLY = "Archive marker only"
NORMAL_ACTIVATIONS = {
    (3, 78, 35, 62): "Normal controller rest spawned actor",
    (5, 120, 19, 50): "Normal controller movement triggered native create trap",
    (6, 92, 45, 45): "Normal controller rest spawned actor",
    (6, 92, 4, 53): "Normal controller rest spawned actor",
    (6, 92, 47, 56): "Normal controller rest spawned actor",
}


def read_banks(filename):
    """Decode the floor directory and resident bank headers from a raw Track 1 BIN."""
    with filename.open("rb") as source, mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if len(data) % track.SECTOR_SIZE:
            raise ValueError("Expected a raw split Track 1 BIN.")

        def payload(lba, count=1):
            return b"".join(data[i*track.SECTOR_SIZE+24:i*track.SECTOR_SIZE+2072]
                            for i in range(lba, lba + count))

        exe = payload(track.EXE_LBA, 761856 // 2048)
        boot = 2048 + track.BOOT - track.EXE_LOAD
        offsets = struct.unpack_from("<9H", exe, boot + 0xac)
        magic = struct.pack("<I", track.PAYLOAD_MAGIC)
        first = next((i for i in range(len(data) // track.SECTOR_SIZE)
                      if data[i*track.SECTOR_SIZE+24:i*track.SECTOR_SIZE+28] == magic), None)
        if first is None:
            raise ValueError("No patched resident bank found.")
        if offsets[0] != 0 or len(set(offsets)) != 9:
            raise ValueError("Expected the cumulative nine-floor payload directory.")

        result = {}
        for level, offset in enumerate(offsets, 1):
            academy = level == 6
            named = banks.LEVEL_SIX_BANKS if academy else banks.room_banks(level, True)
            names = ("hazards-nine" if level == 9 else "default", *(name for name, _, _ in named))
            stride = (0x12800 if academy else banks.ROOM_STRIDE) // 2048
            if level == 1:
                # The DOS shade maps add one sector to each Level 1 bank.
                next_bank = payload(first + offset + stride, 2)
                if next_bank[:4] != magic:
                    stride += 1
            resident = [payload(first + offset + i*stride, 4) for i in range(len(names))]
            for i, bank in enumerate(resident):
                if bank[:4] != magic or struct.unpack_from("<I", bank, banks.ACTIVE)[0] != i:
                    raise ValueError(f"Unexpected payload at floor {level}, bank {i}.")
            result[level] = (names, resident)
        return result


def view_coverage(floor, x, z, actor, image, combat_preview):
    names, resident = image[floor]
    step, grid = (4, banks.GRID) if floor == 6 else (2, 0x1c00)
    cell = z // step * (64 // step) + x // step
    bank_id = resident[0][grid + cell // 2] >> (4 * (cell & 1)) & 15
    bank = resident[bank_id]
    name = names[bank_id]
    if bank_id == 0 and floor not in (6, 9):
        types = {
            1: variant_atlas.GOBLIN_TYPES, 2: (78,), 3: creatures.LIZARD_TYPES,
            4: creatures.LIZARD_TYPES, 5: (78,), 7: (78,), 8: creatures.LEVEL_EIGHT_RAT_TYPES,
        }[floor]
        actions = FIXED_ACTIONS[:-1] if actor in types and floor in (3, 4) else ()
        return name, actor in types, actions

    offset, palette = struct.unpack_from("<HH", bank, 0xf00 + 4 * (actor - 64))
    if not palette:
        return name, False, ()
    compact = combat_preview and (
        name in banks.MIXED_COMBAT_BANKS or name in banks.DEDICATED_ROOM_COMBAT_BANKS
        or floor == 6 and name in banks.ACADEMY_COMBAT_BANKS
        or floor == 6 and bank_id == 0 and struct.unpack_from("<H", bank, 0xf00 + 4 * (103 - 64))[0] != 0
    )
    selector = bank[banks.COMBAT_ACTIONS:banks.COMBAT_ACTIONS + 64]
    if compact:
        index = 0x800 + offset + creatures.MIXED_DIRECTIONAL_FRAMES
        actions = tuple(action for i, action in enumerate(FIXED_ACTIONS)
                        if bank[index + i * creatures.MIXED_COMBAT_PHASES] != 255)
    elif offset == 0:
        actions = tuple(action for action in FIXED_ACTIONS if 2 <= selector[action] < 255)
    else:
        actions = ()
    return name, True, actions


def activation_evidence(filename):
    evidence = {}
    if filename is None:
        return evidence
    pattern = re.compile(r"ACTOR (\d+) \d+ (\d+) (\d+) (\d+) (None|\(\d+, \d+\)) \[(.*?)\]")
    for line in filename.read_text().splitlines():
        match = pattern.fullmatch(line)
        if not match:
            continue
        floor, actor, x, z, linked, traps = match.groups()
        entry = ("Linked on floor load" if linked != "None" else
                 "Create trap identified" if traps else "No create trap identified in probe")
        key = tuple(map(int, (floor, actor, x, z)))
        evidence[key] = entry
    return evidence


def source_actions(directory, actor):
    if directory is None:
        return None
    manifest = directory / f"type-{actor}" / "creature-combat.csv"
    if manifest.is_file():
        with manifest.open(newline="") as source:
            return {int(row["slot"]) for row in csv.DictReader(source)}
    errors = directory / f"type-{actor}.err"
    if errors.is_file() and "Creature has no supported DOS combat frames." in errors.read_text():
        return set()
    return None


def format_actions(actions):
    return " ".join(f"{action:02x}" for action in sorted(actions))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path, help="audit-npcs.py --psx-inventory CSV")
    parser.add_argument("release", type=Path, help="default --dos-shade-maps raw Track 1")
    parser.add_argument("preview", type=Path, help="opt-in --slasher-combat raw Track 1")
    parser.add_argument("--dormant-audit", type=Path, help="optional native tile-chain audit log")
    parser.add_argument("--dos-actions", type=Path, help="per-type export-mixed-combat manifests")
    args = parser.parse_args()
    release, preview = read_banks(args.release), read_banks(args.preview)
    evidence = activation_evidence(args.dormant_audit)
    with args.records.open(newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        source_columns = reader.fieldnames
    if not rows or not source_columns:
        raise ValueError("Expected a nonempty archive inventory.")
    keys = [tuple(int(row[field]) for field in ("level", "psx_type", "spawn_x", "spawn_y")) for row in rows]
    counts = Counter(key for row, key in zip(rows, keys, strict=True) if row["initially_linked"] == "0")
    columns = (*source_columns, "spawn_bank", "west_bank", "preview_directional_views",
               "release_directional_views", "preview_spawn_dos_actions", "preview_west_dos_actions",
               "dos_source_actions", "preview_missing_actions", "activation_evidence")
    writer = csv.DictWriter(sys.stdout, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    dos_actions = {actor: source_actions(args.dos_actions, actor) for actor in range(64, 128)}
    for row, key in zip(rows, keys, strict=True):
        floor, actor, x, z = key
        positions = (x, max(0, x - 1))
        views = [view_coverage(floor, cx, z, actor, preview, True) for cx in positions]
        stock = [view_coverage(floor, cx, z, actor, release, False) for cx in positions]
        status = "Initially linked"
        if row["initially_linked"] == "0":
            if key in NORMAL_ACTIVATIONS:
                status = NORMAL_ACTIVATIONS[key]
            elif counts[key] == 1:
                status = evidence.get(key, ARCHIVE_ONLY)
            else:
                status = "Shared identity and spawn coordinates; review record separately"
        available = dos_actions[actor]
        missing = set()
        if available is not None:
            for _, eligible, actions in views:
                if eligible:
                    missing.update(available.difference(actions))
        writer.writerow({
            **row, "spawn_bank": views[0][0], "west_bank": views[1][0],
            "preview_directional_views": sum(view[1] for view in views),
            "release_directional_views": sum(view[1] for view in stock),
            "preview_spawn_dos_actions": format_actions(views[0][2]),
            "preview_west_dos_actions": format_actions(views[1][2]),
            "dos_source_actions": "unknown" if available is None else format_actions(available) or "none",
            "preview_missing_actions": "unknown" if available is None else format_actions(missing),
            "activation_evidence": status,
        })


if __name__ == "__main__":
    main()

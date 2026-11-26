#!/usr/bin/env python3
"""Build the experimental Japanese Rev 1 Lanugo patch on a scratch data track."""

import argparse
import csv
import hashlib
import shutil
import struct
from pathlib import Path

from mipswords import Code, ret
import academy_banks
import creature_atlas
import lower_atlas
import preview_lighting
import renderer
import variant_atlas

SECTOR_SIZE = 2352
OFFICIAL_HASH = "937ae8cf9a65526f2622c39d34205941f22c10cb"
EXE_LBA = 24
EXE_LOAD = 0x80010000
AVATAR_LBA = 397
PAYLOAD_LBA = 145980
PAYLOAD_RAM = 0x801F6000
IDLE_PAYLOAD_BYTES = 0x7000
WALK_PAYLOAD_BYTES = 0x7800
WALK_HEADER_BYTES = 0x800
WALK_MAGIC = 0x4B4C4157
PAYLOAD_MAGIC = 0x4C414E55
READY_MAGIC = 0x4C414E52
MENU_CODE_RAM = 0x801FF800
MENU_STARTUP = 0x800C77B0
MENU_STARTUP_CALL = 0x80012418
NATIVE_HEAP_INIT = 0x8008C6CC
NATIVE_STACK_TABLE_ENTRY = 0x8001243C
OPTIONS_HELP = MENU_CODE_RAM
OPTIONS_DRAW_ITEMS = 0x8005BEA0
OPTIONS_DRAW_CALL = 0x8005C3C0
INVENTORY_HELP = MENU_CODE_RAM + 0x1a0
RUNE_HELP = MENU_CODE_RAM + 0x500
MAP_HELP = MENU_CODE_RAM + 0x600
MAP_SUBMIT_CALL = 0x80013A34
RUNE_SUBMIT_CALL = 0x800445A0
SPELL_SUBMIT_CALL = 0x8004A204
DIALOGUE_HELP = MENU_CODE_RAM + 0xc0
DIALOGUE_SUBMIT_CALL = 0x80026284
INVENTORY_SUBMIT_CALL = 0x800210F0
SUBMIT_MENU_FRAME = 0x80072264
MENU_TEXT_WIDTH = 0x8007F478
MENU_TEXT_DRAW = 0x8007DA90
WARREN_TALK = MENU_CODE_RAM + 0x700
BOOT = 0x800C2300
SUPPRESS_NORMAL = 0x800C23C0
SUPPRESS_DELAY = 0x800C2400
DRAW_GATE = 0x800C2440
VRAM_UPLOAD_GATE = 0x800C2480
MENU_GATE = 0x800C24B0
ACTOR_GATE = 0x800C24E0
EXPANDED_MENU_GATE = 0x800C24A8
NATIVE_GP = 0x800C9260
LEVEL_ONE_MODELS = 0x800AB890
SUPPRESS_RAM = PAYLOAD_RAM + 0x100
SUPPRESS_DELAY_RAM = PAYLOAD_RAM + 0x160
WALK_SUPPRESS_DELAY_RAM = PAYLOAD_RAM + 0x180
WALK_READY_RAM = PAYLOAD_RAM + 8
DRAW_RAM = PAYLOAD_RAM + 0x200
UPLOAD_RAM = PAYLOAD_RAM + 0x700
WALK_UPLOAD_RAM = PAYLOAD_RAM + 0xa00
VARIANT_UPLOAD_RAM = PAYLOAD_RAM + 0xc00
MENU_RAM = PAYLOAD_RAM + 0xe00
VRAM_GUARD_RAM = PAYLOAD_RAM + 0xe80
RESIDENT_BYTES = 0x1000
LOWER_RESIDENT_BYTES = 0x1800
EXPANDED_RESIDENT_BYTES = 0x2000
LEVEL_SIX_ACADEMY = {name: academy_banks.BANK_FAMILIES[name][0] for name in ("wizb", "wizc")}
LEVEL_SIX_DIRECTIONAL = ((92,), (64, 82), (65, 69), (66, 73))
MODEL_OWNER_OFFSET = 0x58
ORDER_COUNT_OFFSET = 0x5c
ORDER_LOG_RAM = PAYLOAD_RAM + 0x1000
ORDER_WRITER_RAM = PAYLOAD_RAM + 0x600
TEXTURE_STAGING_RAM = 0x801F8800
BAND_BYTES = 0x4000

def jump(address, link=False):
    return struct.pack("<I", ((3 if link else 2) << 26) | ((address >> 2) & 0x3ffffff))

def gate(origin, destination, fallback_register=None, walking=False, floor_aware=False):
    c = Code(origin)
    if floor_aware:
        c.address("t8", PAYLOAD_RAM)
        c.mem("lw", "t9", 4, "t8")
        c.mem("lw", "t8", 0x998, "gp")
        c.branch("beq", "t9", "zero", "fallback")
        c.nop()
        c.branch("bne", "t8", "t9", "fallback")
        c.nop()
    else:
        if walking:
            require_level_one(c, "fallback")
        c.address("t8", PAYLOAD_RAM)
        c.mem("lw", "t8", 4, "t8")
        c.address("t9", READY_MAGIC)
        c.branch("bne", "t8", "t9", "fallback")
        c.nop()
    c.jump(destination)
    c.nop()
    c.label("fallback")
    if fallback_register is None:
        c.jump(0x800757c4)
        c.nop()
    else:
        c.jump(0x8002b684)
        c.mem("sw", "v0", 0, fallback_register)
    return c.out()

def require_level_one(c, fallback):
    # The native level loader installs a different model table for every floor.
    c.mem("lw", "t8", 0x998, "gp")
    c.address("t9", LEVEL_ONE_MODELS)
    c.branch("bne", "t8", "t9", fallback)
    c.nop()


def menu_gate(dialogue=False):
    c = Code(EXPANDED_MENU_GATE if dialogue else MENU_GATE)
    if dialogue:
        c.imm("lui", "t0", "zero", PAYLOAD_RAM >> 16)
        c.mem("lw", "t1", PAYLOAD_RAM & 0xffff, "t0")
    else:
        c.address("t0", PAYLOAD_RAM)
        c.mem("lw", "t1", 0, "t0")
    c.address("t2", PAYLOAD_MAGIC)
    c.branch("bne", "t1", "t2", "native")
    c.nop()
    c.jump(MENU_RAM)
    c.nop()
    c.label("native")
    if dialogue:
        c.branch("beq", "t7", "zero", "inventory")
        c.nop()
        c.jump(0x8003ea5c)
        c.nop()
        c.label("inventory")
    c.jump(0x8005b368)
    c.nop()
    return c.out()


def menu_return(upload_ram=WALK_UPLOAD_RAM, floor_aware=False, dialogue=False):
    c = Code(MENU_RAM)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
    if dialogue:
        c.imm("lui", "t9", "zero", 0x8005)
        c.branch("beq", "t7", "zero", "native_call")
        c.imm("ori", "t9", "t9", 0xb368)
        c.address("t9", 0x8003ea5c)
        c.label("native_call")
        c.add(0x0320f809)  # jalr ra, t9
    else:
        c.jump(0x8005b368, True)
    c.nop()
    c.mem("sw", "v0", 24, "sp")
    if not floor_aware:
        require_level_one(c, "done")
    c.address("t0", PAYLOAD_RAM)
    c.mem("lw", "t1", 0, "t0")
    c.address("t2", PAYLOAD_MAGIC)
    c.branch("bne", "t1", "t2", "done")
    if floor_aware:
        c.mem("lw", "t1", MODEL_OWNER_OFFSET, "t0")
        c.mem("lw", "t2", 0x998, "gp")
        c.branch("beq", "t1", "zero", "done")
        c.nop()
        c.branch("bne", "t1", "t2", "done")
        c.mem("lw", "t1", 4, "t0")
        c.nop()
        c.branch("bne", "t1", "zero", "done")
    else:
        c.mem("lw", "t1", 4, "t0")
        c.address("t2", READY_MAGIC)
        c.branch("beq", "t1", "t2", "done")
    c.nop()
    c.mem("lw", "a0", 12, "t0")
    c.jump(upload_ram, True)
    c.nop()
    c.label("done")
    c.mem("lw", "ra", 28, "sp")
    c.mem("lw", "v0", 24, "sp")
    ret(c, lambda: c.imm("addiu", "sp", "sp", 32))
    return c.out()


def resume_native_upload(c):
    # Replay the SDK routine's first two instructions.
    c.imm("addiu", "sp", "sp", -32)
    c.jump(0x800905dc)
    c.mem("sw", "s0", 16, "sp")


def vram_upload_gate(floor_aware=False, compact=False):
    c = Code(VRAM_UPLOAD_GATE)
    if compact:
        c.imm("lui", "t0", "zero", PAYLOAD_RAM >> 16)
        c.mem("lw", "t1", (PAYLOAD_RAM & 0xffff) + 4, "t0")
    else:
        c.address("t0", PAYLOAD_RAM)
        c.mem("lw", "t1", 4, "t0")
    if floor_aware:
        c.nop()
        c.branch("beq", "t1", "zero", "upload")
    else:
        c.address("t2", READY_MAGIC)
        c.branch("bne", "t1", "t2", "upload")
    c.nop()
    c.jump(VRAM_GUARD_RAM)
    c.nop()
    c.label("upload")
    resume_native_upload(c)
    return c.out()


def vram_guard(wide=False, lower_floor=False, right_edge=512):
    c = Code(VRAM_GUARD_RAM)
    # Native TIM uploads must invalidate sprites before sharing this VRAM region.
    c.mem("lhu", "t0", 0, "a0")
    c.mem("lhu", "t1", 2, "a0")
    c.mem("lhu", "t2", 4, "a0")
    c.mem("lhu", "t3", 6, "a0")
    if wide:
        c.alu("addu", "t2", "t0", "t2")
        c.alu("addu", "t3", "t1", "t3")
        c.imm("sltiu", "t4", "t0", 512)
        c.branch("beq", "t4", "zero", "second_page")
        c.imm("sltiu", "t4", "t2", 385)
        c.branch("bne", "t4", "zero", "second_page")
        c.imm("sltiu", "t4", "t3", 257)
        c.branch("beq", "t4", "zero", "invalidate")
        c.nop()
        c.label("second_page")
        c.imm("sltiu", "t4", "t0", 640)
        c.branch("beq", "t4", "zero", "upload")
        c.imm("sltiu", "t4", "t2", 513)
        c.branch("bne", "t4", "zero", "upload")
        c.imm("sltiu", "t4", "t3", 385)
        c.branch("bne", "t4", "zero", "upload")
        c.nop()
        c.label("invalidate")
    else:
        c.imm("sltiu", "t4", "t0", right_edge)
        c.branch("beq", "t4", "zero", "upload")
        if not lower_floor:
            c.imm("sltiu", "t4", "t1", 480)
            c.branch("beq", "t4", "zero", "upload")
        c.alu("addu", "t2", "t0", "t2")
        c.imm("sltiu", "t4", "t2", 385)
        c.branch("bne", "t4", "zero", "upload")
        c.alu("addu", "t3", "t1", "t3")
        c.imm("sltiu", "t4", "t3", 257)
        c.branch("bne", "t4", "zero", "upload")
        c.nop()
    c.address("t0", PAYLOAD_RAM)
    c.mem("sw", "zero", 4, "t0")
    c.label("upload")
    resume_native_upload(c)
    return c.out()


def loader(payload_lba=PAYLOAD_LBA, walking=False, wide=False):
    c = Code(BOOT)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
    c.mem("sw", "a0", 24, "sp")
    c.jump(0x80029f50, True)
    c.nop()
    c.mem("lw", "t0", 24, "sp")
    c.nop()
    c.address("t2", PAYLOAD_RAM)
    c.branch("bne", "t0", "zero", "done")
    c.nop()
    c.mem("sw", "zero", 4, "t2")
    offset = (payload_lba - AVATAR_LBA) * 2048
    c.address("a0", offset)
    c.address("a1", PAYLOAD_RAM)
    c.jump(0x8003f004, True)
    c.imm("ori", "a2", "zero", RESIDENT_BYTES if walking else IDLE_PAYLOAD_BYTES)
    c.address("t2", PAYLOAD_RAM)
    c.mem("lw", "t0", 0, "t2")
    c.address("t1", PAYLOAD_MAGIC)
    c.branch("bne", "t0", "t1", "done")
    c.nop()
    if walking:
        c.address("a0", offset)
        c.mem("sw", "a0", 12, "t2")
    upload_ram = VARIANT_UPLOAD_RAM if wide else WALK_UPLOAD_RAM if walking else UPLOAD_RAM
    c.jump(upload_ram, True)
    c.nop()
    c.label("done")
    c.mem("lw", "ra", 28, "sp")
    c.nop()
    ret(c, lambda: c.imm("addiu", "sp", "sp", 32))
    return c.out()

def actor_gate():
    c = Code(ACTOR_GATE)
    c.address("t0", PAYLOAD_RAM)
    c.mem("sw", "zero", ORDER_COUNT_OFFSET, "t0")
    c.jump(0x8002a260)
    c.mem("sw", "a1", 0xe0, "sp")
    return c.out()


def floor_loader(payload_lba, lower_payload_lba, lizard_payload_lba=None, rat_payload_lba=None,
                 wizard_payload_lba=None, expanded_level_six=False, academy_runtime=False, level_one_dialogue=False,
                 room_payload_lbas=None):
    c = Code(BOOT)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
    c.mem("sw", "a0", 24, "sp")
    c.address("t2", PAYLOAD_RAM)
    c.mem("sw", "zero", 4, "t2")
    c.mem("sw", "zero", MODEL_OWNER_OFFSET, "t2")
    c.jump(0x80029f50, True)
    if academy_runtime:
        c.mem("sw", "zero", academy_banks.POINTER, "t2")
    else:
        c.nop()
    has_creature_atlas = any(
        lba is not None for lba in (lizard_payload_lba, rat_payload_lba, wizard_payload_lba)
    )
    if not has_creature_atlas:
        c.mem("lw", "t0", 24, "sp")
        c.imm("ori", "a2", "zero", RESIDENT_BYTES)
        c.branch("beq", "t0", "zero", "level_one")
        c.imm("ori", "t1", "zero", 1)
        c.branch("beq", "t0", "t1", "lower")
        c.imm("ori", "t1", "zero", 4)
        c.branch("beq", "t0", "t1", "lower")
        c.imm("ori", "t1", "zero", 6)
        c.branch("bne", "t0", "t1", "done")
        c.nop()
        c.label("lower")
        c.address("a0", (lower_payload_lba - AVATAR_LBA) * 2048)
        c.branch("beq", "zero", "zero", "read")
        c.imm("ori", "a2", "zero", LOWER_RESIDENT_BYTES)
        c.label("level_one")
        c.address("a0", (payload_lba - AVATAR_LBA) * 2048)
        c.label("read")
    else:
        # The named-NPC profile uses halfword sector offsets. Older profiles
        # retain the identical byte table and executable for reproducible builds.
        missing = 0x7fff if level_one_dialogue else 0xff
        floor_table_ram = BOOT + (0xac if level_one_dialogue else 0xb4)
        payload_levels = [payload_lba, lower_payload_lba, lizard_payload_lba, lizard_payload_lba,
                          lower_payload_lba, wizard_payload_lba, lower_payload_lba, rat_payload_lba, None]
        for floor, lba in (room_payload_lbas or {}).items():
            payload_levels[floor - 1] = lba
        floor_offsets = [missing if lba is None else lba - payload_lba for lba in payload_levels]
        if any(lba is not None and not 0 < offset < missing
               for lba, offset in zip(payload_levels[1:], floor_offsets[1:], strict=True)):
            raise ValueError(f"The resident floor table requires additional payload starts within 1–{missing - 1} sectors.")
        floor_table = struct.pack(f"<{len(floor_offsets)}{'H' if level_one_dialogue else 'B'}", *floor_offsets)
        offset = (payload_lba - AVATAR_LBA) * 2048
        c.mem("lw", "t0", 24, "sp")
        c.imm("ori", "a2", "zero", EXPANDED_RESIDENT_BYTES if level_one_dialogue else RESIDENT_BYTES)
        c.imm("sltiu", "t2", "t0", len(floor_offsets))
        c.branch("beq", "t2", "zero", "done")
        if level_one_dialogue:
            c.shift("sll", "t0", "t0", 1)
        c.alu("addu", "t1", "gp", "t0")
        c.mem("lhu" if level_one_dialogue else "lbu", "t1", floor_table_ram - NATIVE_GP, "t1")
        c.imm("lui", "t3", "zero", offset >> 16)
        c.imm("sltiu", "t2", "t1", missing)
        c.branch("beq", "t2", "zero", "done")
        c.shift("sll", "a0", "t1", 11)
        if not level_one_dialogue:
            c.alu("sltu", "t2", "zero", "t1")
            if expanded_level_six:
                c.alu("subu", "t2", "zero", "t2")
                c.imm("andi", "t2", "t2", EXPANDED_RESIDENT_BYTES - RESIDENT_BYTES)
                c.alu("addu", "a2", "a2", "t2")
            else:
                c.shift("sll", "t2", "t2", 11)
                c.alu("OR", "a2", "a2", "t2")  # Level 1 uses 0x1000, other atlases use 0x1800.
        c.imm("ori", "t3", "t3", offset)
        c.alu("addu", "a0", "a0", "t3")
    c.mem("sw", "a0", 20, "sp")
    c.address("a1", PAYLOAD_RAM)
    c.jump(0x8003f004, True)
    c.nop()
    c.address("t2", PAYLOAD_RAM)
    c.mem("lw", "t0", 0, "t2")
    c.address("t1", PAYLOAD_MAGIC)
    c.branch("bne", "t0", "t1", "done")
    c.mem("lw", "a0", 20, "sp")
    c.mem("lw", "t0", 0x998, "gp")
    c.mem("sw", "a0", 12, "t2")
    c.jump(VARIANT_UPLOAD_RAM, True)
    c.mem("sw", "t0", MODEL_OWNER_OFFSET, "t2")
    c.label("done")
    c.mem("lw", "ra", 28, "sp")
    c.nop()
    ret(c, lambda: c.imm("addiu", "sp", "sp", 32))
    blob = c.out()
    if not has_creature_atlas:
        return blob
    gap = floor_table_ram - BOOT - len(blob)
    if gap < 0:
        raise ValueError(f"The {len(blob)}-byte loader overlaps its floor table.")
    return blob + bytes(gap) + floor_table


def mark_idle_ready(c, floor_aware=False):
    c.address("t0", PAYLOAD_RAM)
    if floor_aware:
        c.mem("lw", "t1", MODEL_OWNER_OFFSET, "t0")
    else:
        c.address("t1", READY_MAGIC)
    c.mem("lw", "ra", 28, "sp")
    c.mem("sw", "t1", 4, "t0")
    ret(c, lambda: c.imm("addiu", "sp", "sp", 32))


def upload_rectangle(c, rectangle, source):
    c.address("a0", PAYLOAD_RAM + rectangle)
    c.address("a1", source)
    c.jump(0x80091b34, True)
    c.nop()


def uploader():
    c = Code(UPLOAD_RAM)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
    upload_rectangle(c, 0x10, PAYLOAD_RAM + 0x1000)
    upload_rectangle(c, 0x18, PAYLOAD_RAM + 0x30)
    mark_idle_ready(c)
    return c.out()


def walking_uploader():
    c = Code(WALK_UPLOAD_RAM)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
    c.mem("sw", "a0", 24, "sp")
    c.address("t0", PAYLOAD_RAM)
    c.mem("sw", "zero", 8, "t0")
    # Upload in bands to keep DMA and GPU transfers clear of live game RAM at 0x801f8000.
    bands = (
        (0x10, RESIDENT_BYTES, BAND_BYTES, 0),
        (0x20, RESIDENT_BYTES + BAND_BYTES, 0x2000, 0),
        (0x50, IDLE_PAYLOAD_BYTES, WALK_HEADER_BYTES + BAND_BYTES, WALK_HEADER_BYTES),
        (0x58, IDLE_PAYLOAD_BYTES + WALK_HEADER_BYTES + BAND_BYTES, 0x3000, 0),
    )
    for rectangle, offset, size, header in bands:
        c.mem("lw", "a0", 24, "sp")
        c.address("a1", TEXTURE_STAGING_RAM)
        c.imm("ori", "t0", "zero", offset)
        c.alu("addu", "a0", "a0", "t0")
        if header:
            c.mem("sw", "zero", 0, "a1")
        c.jump(0x8003f004, True)
        c.imm("ori", "a2", "zero", size)
        if header:
            c.address("t0", TEXTURE_STAGING_RAM)
            c.mem("lw", "t1", 0, "t0")
            c.address("t2", WALK_MAGIC)
            c.branch("bne", "t1", "t2", "idle_ready")
            c.nop()
        upload_rectangle(c, rectangle, TEXTURE_STAGING_RAM + header)
        c.jump(0x800903ac, True)
        c.imm("ori", "a0", "zero", 0)
        if rectangle == 0x20:
            upload_rectangle(c, 0x18, PAYLOAD_RAM + 0x30)
            c.jump(0x800903ac, True)
            c.imm("ori", "a0", "zero", 0)
    c.address("t0", PAYLOAD_RAM)
    c.imm("ori", "t1", "zero", 1)
    c.mem("sw", "t1", 8, "t0")
    c.label("idle_ready")
    mark_idle_ready(c)
    return c.out()


def read_source_atlas(directory, name, height, first_slot, prefix="lanugo", poses=None):
    data = (directory / f"{prefix}-{name}.tim").read_bytes()
    image_size = 2 * 256 * height
    if len(data) != 20 + image_size or struct.unpack_from("<IIIHHHH", data) != (
        16, 2, 12 + image_size, 0, 0, 256, height
    ):
        raise ValueError(f"Expected the Xcode tool's 256×{height} 16-bit Lanugo {name} TIM.")
    texels = struct.unpack_from(f"<{256 * height}H", data, 20)
    with (directory / f"{prefix}-{name}.csv").open() as csv_file:
        rows = list(csv.DictReader(csv_file))
    if poses is None:
        poses = tuple((slot, 4) for slot in range(first_slot, first_slot + 8))
    expected = [(slot, phase) for slot, count in poses for phase in range(count)]
    if [(int(row["slot"]), int(row["phase"])) for row in rows] != expected:
        raise ValueError(f"The {name} texture manifest does not contain the expected slots and phases.")
    metadata = []
    for row in rows:
        u, v, w, h, hx, hy = (int(row[key]) for key in (
            "u", "v", "width", "height", "hotspot_x", "hotspot_y"
        ))
        if not (w > 0 and h > 0 and 0 <= u <= 256 - w and 0 <= v <= height - h):
            raise ValueError(f"Lanugo {name} frame lies outside its TIM.")
        if not (0 <= hx < 256 and 0 <= hy < 256):
            raise ValueError(f"Lanugo {name} hotspot is outside the supported byte range.")
        metadata.append((u, v, w, h, hx, hy))
    return texels, metadata


def read_atlas(directory, name, height, first_slot, texture_page=0):
    texels, rows = read_source_atlas(directory, name, height, first_slot)
    colors = sorted(set(texels))
    if len(colors) != 16 or colors[0] != 0:
        raise ValueError(f"The Lanugo {name} atlas must contain 16 RGB555 entries including transparency.")
    indexed = {color: index for index, color in enumerate(colors)}
    image = bytes(indexed[left] | indexed[right] << 4 for left, right in zip(texels[::2], texels[1::2]))
    metadata = b"".join(struct.pack("8B", *row, texture_page, 0) for row in rows)
    return colors, image, metadata


def variant_image_bands(texture_pages=variant_atlas.TEXTURE_PAGES, offset=RESIDENT_BYTES):
    for x, y, height in texture_pages:
        for start in range(0, height, 64):
            rows = min(64, height - start)
            size = variant_atlas.WIDTH * rows
            yield (x, y + start, variant_atlas.WIDTH // 2, rows), offset, size
            offset += size


def variant_uploader(bands, resident_clut=True, floor_aware=False, origin=VARIANT_UPLOAD_RAM):
    c = Code(origin)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
    c.mem("sw", "a0", 24, "sp")
    for index, (_, offset, size) in enumerate(bands):
        c.mem("lw", "a0", 24, "sp")
        c.address("a1", TEXTURE_STAGING_RAM)
        c.address("t0", offset)
        c.alu("addu", "a0", "a0", "t0")
        c.jump(0x8003f004, True)
        c.imm("ori", "a2", "zero", size)
        upload_rectangle(c, 0x10 + 8 * index, TEXTURE_STAGING_RAM)
        c.jump(0x800903ac, True)
        c.imm("ori", "a0", "zero", 0)
    if resident_clut:
        upload_rectangle(c, 0x10 + 8 * len(bands), PAYLOAD_RAM + 0xf00)
        c.jump(0x800903ac, True)
        c.imm("ori", "a0", "zero", 0)
    c.address("t0", PAYLOAD_RAM)
    c.imm("ori", "t1", "zero", 1)
    c.mem("sw", "t1", 8, "t0")
    mark_idle_ready(c, floor_aware)
    return c.out()


def variant_sources(idle_atlas, walk_atlas, variants):
    data = []
    for mode, height, slot, base in (("idle", 192, 0x20, idle_atlas), ("walk", 224, 0x80, walk_atlas)):
        sources = [read_source_atlas(base, mode, height, slot)]
        for actor in variant_atlas.GOBLIN_TYPES[1:]:
            directory = variants / f"type-{actor}" / mode
            sources.append(read_source_atlas(directory, mode, height, slot, prefix="goblin"))
        data.append(sources)
    return data


def variant_payload(idle_atlas, walk_atlas, variants, dos_light_preview=None, floor_aware=False,
                    bank_sections=None, bank_stride=academy_banks.ROOM_STRIDE):
    sources = variant_sources(idle_atlas, walk_atlas, variants)
    pages = variant_atlas.TEXTURE_PAGES if dos_light_preview is None else preview_lighting.TEXTURE_PAGES
    images, clut, metadata = variant_atlas.build(sources, pages)
    resident = EXPANDED_RESIDENT_BYTES if bank_sections is not None else RESIDENT_BYTES
    bands = tuple(variant_image_bands(pages, resident))
    atlas_end = resident + sum(map(len, images))
    clut_rect = variant_atlas.CLUT_RECT if dos_light_preview is None else preview_lighting.CLUT_RECT
    x, y, _, _ = clut_rect
    clut_id = (y << 6) | (x >> 4)
    shade_selector = None if dos_light_preview is None else PAYLOAD_RAM + preview_lighting.SELECTOR_OFFSET
    draw_code, shade_return = renderer.draw(
        DRAW_RAM, PAYLOAD_RAM + 0x800, PAYLOAD_RAM + 0x90, clut_id, WALK_READY_RAM,
        wide=True, shade_selector=shade_selector,
    )
    sections = {
        0: struct.pack("<I", PAYLOAD_MAGIC),
        0x90: renderer.DOS_IDLE_DIRECTIONS,
        0x100: renderer.suppress(SUPPRESS_RAM, walk_ready=WALK_READY_RAM, wide=True),
        0x180: renderer.suppress(WALK_SUPPRESS_DELAY_RAM, "a0", WALK_READY_RAM, wide=True),
        0x200: draw_code,
        0x800: metadata,
        MENU_RAM - PAYLOAD_RAM: menu_return(VARIANT_UPLOAD_RAM, floor_aware),
        VRAM_GUARD_RAM - PAYLOAD_RAM: vram_guard(wide=True),
        resident: b"".join(images),
    }
    if dos_light_preview is None:
        sections[0xf00] = clut
        rectangles = tuple(rect for rect, _, _ in bands) + (clut_rect,)
    else:
        palettes = preview_lighting.palette_banks(dos_light_preview, clut)
        bands += ((clut_rect, atlas_end, len(palettes)),)
        sections[atlas_end] = palettes
        atlas_end += len(palettes)
        native_level = bank_sections is not None
        settings_base = (preview_lighting.ROOM_LIGHT_SETTINGS_BASE if native_level else
                         preview_lighting.LIGHT_LEVEL_OFFSET)
        sections[settings_base + preview_lighting.SETTINGS_DELTA] = preview_lighting.light_settings(dos_light_preview)
        sections[preview_lighting.SELECTOR_OFFSET] = preview_lighting.select_clut(
            shade_selector, PAYLOAD_RAM + settings_base, shade_return, clut_id, native_level=native_level,
        )
        rectangles = tuple(rect for rect, _, _ in bands)
    sections[0x10] = b"".join(struct.pack("<4H", *rect) for rect in rectangles)
    if bank_sections is None:
        sections[VARIANT_UPLOAD_RAM - PAYLOAD_RAM] = variant_uploader(bands, dos_light_preview is None, floor_aware)
    else:
        sections[0x100] = jump(PAYLOAD_RAM + 0x700) + bytes(4)
        sections[0x180] = jump(PAYLOAD_RAM + 0xd00) + bytes(4)
        sections[0x700] = renderer.suppress(PAYLOAD_RAM + 0x700, walk_ready=WALK_READY_RAM, wide=True)
        sections[0xd00] = renderer.suppress(PAYLOAD_RAM + 0xd00, "a0", WALK_READY_RAM, wide=True)
        sections[0xc00] = jump(PAYLOAD_RAM + 0x1400) + bytes(4)
        sections[0x1400] = variant_uploader(bands, dos_light_preview is None, floor_aware, PAYLOAD_RAM + 0x1400)
        overlap = sections.keys() & bank_sections.keys()
        if overlap:
            raise ValueError(f"Level 1 renderer and room-bank sections share offsets: {sorted(overlap)}.")
        sections.update(bank_sections)
        atlas_end = bank_stride
    return assemble_payload(sections, atlas_end)


def lower_floor_atlas(variants):
    base = variants / f"type-{renderer.LOWER_GOBLIN_TYPE}"
    sources = (
        read_source_atlas(base / "idle", "idle", 192, 0x20, prefix="goblin"),
        read_source_atlas(base / "walk", "walk", 224, 0x80, prefix="goblin"),
    )
    return lower_atlas.build(sources)


def lower_floor_payload(variants, bank_sections=None):
    images, clut, metadata, overlay = lower_floor_atlas(variants)
    uploader_ram = PAYLOAD_RAM + 0x1400
    sections = {
        0: struct.pack("<I", PAYLOAD_MAGIC),
        0x90: renderer.DOS_IDLE_DIRECTIONS,
        0x100: renderer.suppress(SUPPRESS_RAM, walk_ready=WALK_READY_RAM, lower_floor=True),
        0x180: renderer.suppress(WALK_SUPPRESS_DELAY_RAM, "a0", WALK_READY_RAM, lower_floor=True),
        0x200: renderer.draw(
            DRAW_RAM, PAYLOAD_RAM + 0x800, PAYLOAD_RAM + 0x90,
            walk_ready=WALK_READY_RAM, wide=True, overlay_offset=0x800,
        )[0],
        0x800: metadata,
        0xc00: jump(uploader_ram) + bytes(4),
        0xe00: menu_return(VARIANT_UPLOAD_RAM, floor_aware=True),
        0xe80: vram_guard(lower_floor=True),
        0x1000: overlay,
    }
    resident = LOWER_RESIDENT_BYTES
    if bank_sections is not None:
        sections[0x100] = jump(PAYLOAD_RAM + 0x700) + bytes(4)
        sections[0x180] = jump(PAYLOAD_RAM + 0xd00) + bytes(4)
        sections[0x700] = renderer.suppress(PAYLOAD_RAM + 0x700, walk_ready=WALK_READY_RAM, lower_floor=True)
        sections[0xd00] = renderer.suppress(PAYLOAD_RAM + 0xd00, "a0", WALK_READY_RAM, lower_floor=True)
        sections.update(bank_sections)
        resident = EXPANDED_RESIDENT_BYTES
    blob = compact_payload(sections, images, clut, lower_atlas.TEXTURE_PAGES, lower_atlas.HEIGHT,
                           lower_atlas.CLUT_RECT, resident)
    return blob.ljust(academy_banks.ROOM_STRIDE, b"\0") if bank_sections is not None else blob


def creature_sources(variants, actor_types, combat=False, casting=False):
    modes = [("idle", 0x20, None), ("walk", 0x80, None)]
    if combat or casting:
        poses = creature_atlas.COMBAT_SLOTS if combat else ()
        if casting:
            poses += (creature_atlas.CAST_SLOT,)
        modes.append(("combat", 0, poses))

    def read_mode(actor, mode, slot, poses):
        if mode == "walk" and actor in (125, 126):
            mode, slot = "idle", 0x20
        return read_source_atlas(
            variants / f"type-{actor}" / mode, mode, creature_atlas.SOURCE_HEIGHT, slot,
            prefix="creature", poses=poses,
        )

    return tuple(
        tuple(read_mode(actor, mode, slot, poses) for actor in actor_types)
        for mode, slot, poses in modes
    )


def lizard_sources(variants, combat=False):
    return creature_sources(variants, creature_atlas.LIZARD_TYPES, combat)


def lizard_payload(variants, combat=False, bank_sections=None):
    return creature_payload(variants, creature_atlas.LIZARD_TYPES, creature_atlas.TEXTURE_PAGES, combat,
                            academy_sections=bank_sections, room_default=bank_sections is not None)


def rat_payload(variants, bank_sections=None):
    return creature_payload(variants, creature_atlas.LEVEL_EIGHT_RAT_TYPES, creature_atlas.RAT_TEXTURE_PAGES,
                            academy_sections=bank_sections, room_default=bank_sections is not None)


def mixed_combat_sources(variants, types):
    directory = variants / f"type-{types[0]}" / "mixed-combat"
    with (directory / "creature-combat.csv").open() as manifest:
        counts = {}
        for row in csv.DictReader(manifest):
            slot = int(row["slot"])
            counts[slot] = counts.get(slot, 0) + 1
    slots = tuple(sorted(counts.items()))
    allowed = {action for action, _ in (*creature_atlas.COMBAT_SLOTS, creature_atlas.CAST_SLOT)}
    if not slots or any(action not in allowed or not 1 <= count <= 8 for action, count in slots):
        raise ValueError(f"Invalid mixed combat action table for {types}.")
    frames = tuple(read_source_atlas(
        variants / f"type-{actor}" / "mixed-combat", "combat", creature_atlas.SOURCE_HEIGHT, 0,
        prefix="creature", poses=slots,
    ) for actor in types)
    return creature_sources(variants, types) + (frames,), slots


def pack_mixed_page(families, page, bits, scales):
    # Try the room's original texture scales first, then reduce both axes as needed.
    for cap in range(max(scales), 0, -1):
        try:
            return creature_atlas.build_families(
                families, page, bits=bits, scales=tuple(min(scale, cap) for scale in scales),
            )
        except variant_atlas.AtlasDoesNotFit:
            if cap == 1:
                raise


def mixed_table_locations(tables, room_bank, academy_default=False):
    # Gaps between renderer stubs, uploader, and camera grid.
    windows = [(0x804, 0xc00), (0x1000, 0x1400), (0x1600, 0x1c00), (0x1e00, 0x2000)]
    if academy_default:
        # The Academy camera grid lives at 0xc80.
        windows[-1] = (0x1c00, 0x2000)
    locations = [0] * len(tables)
    for index in sorted(range(len(tables)), key=lambda i: -len(tables[i])):
        size = len(tables[index])
        for i, (start, end) in enumerate(windows):
            if start + size <= end:
                locations[index] = start
                windows[i] = ((start + size + 3) & ~3, end)
                break
        else:
            raise ValueError(f"Mixed combat metadata does not fit {room_bank}: {[len(t) for t in tables]}.")
    return locations


def creature_payload(variants, actor_types, texture_pages, combat=False, extra_type=None, casting=False,
                     expanded_level_six=False, academy_bank=None, academy_sections=None, room_bank=None, room_default=False,
                     slasher_combat=False, room_combat=False, recurring_academy=False, native_sprite_lighting=False):
    sources = creature_sources(variants, actor_types, combat, casting)
    images, clut, metadata = creature_atlas.build(sources, texture_pages)
    base = actor_types[0]
    if len(actor_types) == 1:
        palette_types = base, base, 1
    else:
        palette_types = base, actor_types[1], len(actor_types) - 1
    x, y, width, _ = creature_atlas.CLUT_RECT
    clut_rect = x, y, width, len(actor_types)
    order_log = PAYLOAD_RAM + ORDER_COUNT_OFFSET, ORDER_LOG_RAM
    extra_atlas = None
    extra_sections = {}
    bank_combat_slots = None
    split_format = academy_banks.SPLIT_ROOM_FORMATS.get(room_bank)
    shared_format = academy_banks.SHARED_PAGE_FORMATS.get(room_bank)
    dedicated_combat = room_combat and (
        room_bank in academy_banks.DEDICATED_ROOM_COMBAT_BANKS or academy_bank in academy_banks.ACADEMY_COMBAT_BANKS
    )
    academy_default_combat = room_combat and academy_bank is None and room_bank is None
    mixed_combat = (dedicated_combat or academy_default_combat
                    or room_combat and room_bank in academy_banks.MIXED_COMBAT_BANKS)
    if expanded_level_six:
        # Keep persistent frame lookups below 0x801f8000, where the native floor load writes.
        if not (casting and combat and extra_type == 92 and texture_pages == creature_atlas.TEXTURE_PAGES[:1]):
            raise ValueError("The expanded Level 6 atlas requires the wizard-combat and spider preview.")
        # Both Academy families fit individually with all facing frames intact.
        # One table can occupy the two adjacent upper resident slots.
        families = academy_banks.BANK_FAMILIES[academy_bank] if academy_bank else LEVEL_SIX_DIRECTIONAL
        if recurring_academy and academy_bank == "trolls":
            families = ((96, 111, 112),)
        if room_bank:
            families = academy_banks.ROOM_FAMILIES[room_bank]
        if dedicated_combat and academy_bank == "imps":
            # Keep imp attack and casting poses on their own page beside the bats.
            families = (*families, (66, 73))
            shared_format = ((8, (16,)), (4, (16,)))
        if academy_default_combat or (dedicated_combat and academy_bank in ("wizb", "wizc", "warren")):
            # Preserve the primary wizard family carried by these Academy banks.
            families = (actor_types, *families)
            shared_format = ((4, (16,)), (4, (16,) * (len(families) - 1)))
        if mixed_combat:
            # The grub's DOS combat frames use colors absent from its directional atlas.
            if room_bank in ("grubs-slugs", "rats-grubs-five", "rats-grubs-eight"):
                split_format = 8, split_format[1]
            if room_bank in ("bats-grubs-rats", "grub-imp"):
                shared_format = ((8, shared_format[0][1]), shared_format[1])
            directional_only = {
                "warren": (97,),
                "imps": (66, 73),
                # Leave room for the goblin combat table and retain native lurker combat.
                "lurkers-goblins-seven": (87, 116),
            }.get(room_bank or academy_bank)
            mixed_sources, family_actions = zip(*(
                (creature_sources(variants, types), ())
                if types == directional_only or (academy_default_combat and types not in (actor_types, (92,)))
                else mixed_combat_sources(variants, types)
                for types in families
            ))
        if slasher_combat:
            table_slots = ((0x1000, 0x400), (0x1800, 0x200), (0x1a00, 0x200))
        elif room_bank == "hazards-nine":
            table_slots = ((0x804, 0x3fc), (0x1000, 0x400), (0x1800, 0x200), (0x1a00, 0x200))
        elif shared_format:
            table_slots = ((0x804, 0x3fc), (0x1000, 0x400), (0x1800, 0x400))[:len(families)]
        elif split_format:
            # The shared room needs two compact tables below the order log at 0x1800.
            table_slots = ((0x804, 0x3fc), (0x1000, 0x400))
        elif room_bank:
            table_slots = ((0x1000, 0x400),)
        elif academy_bank:
            table_slots = ((0x1c00, 0x400), (0x1000, 0x200))[:len(families)]
        else:
            table_slots = (
                (0x1000, 0x200), (0x1c00, 0x200), (0x1e00, 0x200), (0x1200, 0x200),
            )
        texture_pages = creature_atlas.TEXTURE_PAGES
        format_override = academy_banks.SPECIAL_FORMATS.get(academy_bank)
        if room_combat and room_bank in academy_banks.ROOM_COMBAT_BANKS:
            bits, scale = academy_banks.ROOM_FORMATS[room_bank]
            format_override = bits, scale, True
        primary_types = actor_types
        if shared_format:
            texture_pages = creature_atlas.TEXTURE_PAGES
            images, palettes, directional = [], [], []
            palette_stride = 64 if any(bits == 8 for bits, _ in shared_format) else 32
            next_family = 0
            for page, (bits, scales) in zip(texture_pages, shared_format, strict=True):
                end = next_family + len(scales)
                page_families = [creature_sources(variants, types) for types in families[next_family:end]]
                if mixed_combat:
                    page_families = mixed_sources[next_family:end]
                if slasher_combat and next_family == 0:
                    bank_combat_slots = (*creature_atlas.COMBAT_SLOTS, (13, 4))
                    combat_source = read_source_atlas(
                        variants / "type-124" / "combat", "combat", creature_atlas.SOURCE_HEIGHT, 0,
                        prefix="creature", poses=bank_combat_slots,
                    )
                    page_families[0] += ((combat_source,),)
                    # The extra 31 combat frames fit with the eye at this resolution.
                    scales = (9, *scales[1:])
                if mixed_combat:
                    art, colors, tables = pack_mixed_page(page_families, page, bits, scales)
                else:
                    art, colors, tables = creature_atlas.build_families(page_families, page, bits=bits, scales=scales)
                images.append(art)
                palettes.extend(clut.ljust(palette_stride, b"\0") for clut in colors)
                directional.extend(tables)
                next_family = end
            primary_types = ()
            if slasher_combat:
                primary_types = (124,)
                metadata, *directional = directional
                families = families[1:]
        elif split_format:
            bits, scales = split_format
            palette_stride = 64 if bits == 8 else 32
            if mixed_combat:
                packed = [
                    pack_mixed_page((sources,), page, bits, (scale,))
                    for sources, page, scale in zip(mixed_sources, texture_pages, scales, strict=True)
                ]
                images, palettes, directional = zip(*((image, colors, tables[0]) for image, colors, tables in packed))
                palettes = [clut for colors in palettes for clut in colors]
            else:
                packed = [
                    creature_atlas.build(creature_sources(variants, types), (page,), bits=bits, scale=scale)
                    for types, page, scale in zip(families, texture_pages, scales, strict=True)
                ]
                images = tuple(image for (image,), _, _ in packed)
                palettes = [clut[i:i + palette_stride] for _, clut, _ in packed
                            for i in range(0, len(clut), palette_stride)]
                directional = tuple(table for _, _, table in packed)
            primary_types = ()
        elif dedicated_combat:
            bits, scale = academy_banks.ROOM_FORMATS[room_bank] if room_bank else (8, 14)
            for frame_scale in range(scale, 0, -1):
                try:
                    images, palette_data, table = creature_atlas.build(
                        mixed_sources[0], texture_pages, bits=bits, scale=frame_scale,
                    )
                    break
                except variant_atlas.AtlasDoesNotFit:
                    if frame_scale == 1:
                        raise
            primary_types = ()
            palette_stride = 64 if bits == 8 else 32
            palettes = [palette_data[i:i + palette_stride] for i in range(0, len(palette_data), palette_stride)]
            directional = (table,)
        elif room_bank and format_override is None:
            bits, scale = academy_banks.ROOM_FORMATS[room_bank]
            images, palette_data, table = creature_atlas.build(
                creature_sources(variants, families[0]), texture_pages, bits=bits, scale=scale,
            )
            primary_types = ()
            palette_stride = 64 if bits == 8 else 32
            palettes = [palette_data[i:i + palette_stride] for i in range(0, len(palette_data), palette_stride)]
            directional = (table,)
        elif format_override:
            bits, scale, _ = format_override
            primary_types = families[0]
            available = creature_atlas.COMBAT_SLOTS
            if primary_types[0] in (75, 81):
                available += ((13, 4),)
            # The Academy ghoul keeps the two sequences that fit its existing atlas.
            bank_combat_slots = ((0, 4), (7, 4)) if academy_bank == "ghouls" else available
            special_sources = creature_sources(variants, primary_types)
            selected = []
            first = 0
            for slot, count in available:
                if (slot, count) in bank_combat_slots:
                    selected.extend(range(first, first + count))
                first += count
            pose_sources = tuple(
                read_source_atlas(variants / f"type-{actor}" / "combat", "combat",
                                  creature_atlas.SOURCE_HEIGHT, 0, prefix="creature", poses=available)
                for actor in primary_types
            )
            special_sources += (tuple((pixels, [frames[i] for i in selected]) for pixels, frames in pose_sources),)
            images, palette_data, metadata = creature_atlas.build(
                special_sources, texture_pages, bits=bits, scale=scale,
            )
            palette_stride = 64 if bits == 8 else 32
            palettes = [palette_data[i:i + palette_stride] for i in range(0, len(palette_data), palette_stride)]
            families, directional, table_slots = (), (), ()
        else:
            image, palettes, directional = creature_atlas.build_families(
                [creature_sources(variants, types) for types in families], texture_pages[1],
            )
            images += (image,)
            palette_stride = 32
        primary_palettes = (
            [] if bank_combat_slots or slasher_combat else [clut[i:i + 32] for i in range(0, len(primary_types) * 32, 32)]
        )
        if palette_stride == 64:
            # Each 8-bit sprite uses only the first 32 entries in its own CLUT row.
            rows = [palette.ljust(64, b"\0") for palette in primary_palettes] + list(palettes)
            clut = b"".join(rows).ljust(512, b"\0")
            palette_columns = len(rows)
        else:
            rows = primary_palettes + list(palettes)
            rows += [bytes(32)] * (16 - len(rows))
            clut = b"".join(rows[i] + rows[i + 8] for i in range(8))
            palette_columns = 8
        clut_rect = x, y, 32, 8
        registry_data = bytearray(64 * 4)
        for row, actor in enumerate(primary_types):
            struct.pack_into("<HH", registry_data, 4 * (actor - 64), 0, creature_atlas.CLUT_BASE + row * 64)
        row = len(primary_types)
        if mixed_combat:
            tables = tuple(creature_atlas.compact_frame_table(table, slots)
                           for table, slots in zip(directional, family_actions, strict=True))
            locations = mixed_table_locations(tables, room_bank, academy_default_combat)
        else:
            tables = tuple(creature_atlas.compact_frame_table(table) for table in directional)
            locations = []
            for table, (location, capacity) in zip(tables, table_slots[:len(tables)], strict=True):
                if len(table) > capacity:
                    raise ValueError("The compact Level 6 frame table exceeds its safe RAM range.")
                locations.append(location)
        for types, compact, location in zip(families, tables, locations, strict=True):
            extra_sections[location] = compact
            for actor in types:
                palette = creature_atlas.CLUT_BASE + (row % palette_columns) * 64 + row // palette_columns
                struct.pack_into("<HH", registry_data, 4 * (actor - 64), location - 0x800, palette)
                row += 1
        extra_sections[0xf00] = registry_data
        log_offset = EXPANDED_RESIDENT_BYTES if shared_format or mixed_combat else LOWER_RESIDENT_BYTES
        order_log = PAYLOAD_RAM + ORDER_COUNT_OFFSET, PAYLOAD_RAM + log_offset
    elif extra_type is not None:
        if (combat and not casting) or texture_pages != creature_atlas.TEXTURE_PAGES[:1]:
            raise ValueError("The extra atlas requires one primary wizard or directional page.")
        extra_page = creature_atlas.TEXTURE_PAGES[1:]
        extra_images, extra_clut, extra_metadata = creature_atlas.build(
            creature_sources(variants, (extra_type,)), extra_page,
        )
        images += extra_images
        texture_pages += extra_page
        clut += extra_clut
        clut_rect = x, y, width, len(actor_types) + 1
        extra_atlas = extra_type, PAYLOAD_RAM + 0x1000, creature_atlas.CLUT_BASE + 64 * len(actor_types)
        extra_sections[0x1000] = extra_metadata
        # The logger writes each entry before use. Keep it beyond the resident read
        # and below the texture DMA staging buffer.
        order_log = PAYLOAD_RAM + ORDER_COUNT_OFFSET, PAYLOAD_RAM + LOWER_RESIDENT_BYTES
    action_addresses = None
    combat_sections = {}
    if combat or casting:
        actions, phases = creature_atlas.wizard_actions(combat) if casting else creature_atlas.combat_actions()
        death_index = actions[creature_atlas.DEATH_SLOT]
        phase_offset = 0xc10 if casting else 0x700
        action_offset = academy_banks.COMBAT_ACTIONS if academy_sections is not None else 0xb0
        if bank_combat_slots:
            actions = bytearray(actions)
            phases = bytearray(len(phases))
            counts = dict(bank_combat_slots)
            first = 0
            for action, _ in (*creature_atlas.COMBAT_SLOTS, creature_atlas.CAST_SLOT):
                index = actions[action] - 2
                if action in counts:
                    count = counts[action]
                    phases[index*16:(index+1)*16] = bytes(first + min(frame, count-1) for frame in range(16))
                    first += count
                else:
                    actions[action] = 255
        combat_sections = {action_offset: actions}
        if not mixed_combat:
            combat_sections.update({phase_offset: phases, 0x1600: metadata[0x400:]})
        metadata = metadata[:0x400]
        action_addresses = (
            PAYLOAD_RAM + action_offset, PAYLOAD_RAM + phase_offset, PAYLOAD_RAM + 0x1600,
            death_index,
        )
    registry = PAYLOAD_RAM + 0xf00 if expanded_level_six else None
    suppress_addr = SUPPRESS_RAM if extra_type is None else PAYLOAD_RAM + 0x700
    delay_addr = WALK_SUPPRESS_DELAY_RAM if extra_type is None else PAYLOAD_RAM + 0xd00
    if room_default:
        suppress_addr = PAYLOAD_RAM + 0x1800
        delay_addr = PAYLOAD_RAM + 0x1900
    # Gazers and Tyball can exceed the polygon log limit. Keep one head per depth bucket.
    dense_models = mixed_combat and any(102 in family or 123 in family for family in families)
    unique_order_buckets = room_bank == "hazards-nine" or dense_models
    sections = {
        0: struct.pack("<I", PAYLOAD_MAGIC),
        0x90: renderer.DOS_IDLE_DIRECTIONS,
        suppress_addr - PAYLOAD_RAM: renderer.suppress(
            suppress_addr, walk_ready=WALK_READY_RAM, wide=True,
            palette_types=palette_types, order_writer=ORDER_WRITER_RAM,
            action_map=None if action_addresses is None else action_addresses[0], extra_type=extra_type,
            wizard_combat=casting and combat, registry=registry, mixed_combat=mixed_combat,
        ),
        delay_addr - PAYLOAD_RAM: renderer.suppress(
            delay_addr, "a0", WALK_READY_RAM, wide=True,
            palette_types=palette_types, order_writer=ORDER_WRITER_RAM,
            action_map=None if action_addresses is None else action_addresses[0], extra_type=extra_type,
            wizard_combat=casting and combat, registry=registry, mixed_combat=mixed_combat,
        ),
        0x200: renderer.draw(
            DRAW_RAM, PAYLOAD_RAM + 0x800, PAYLOAD_RAM + 0x90,
            clut=creature_atlas.CLUT_BASE, walk_ready=WALK_READY_RAM, wide=True,
            palette_types=palette_types, order_log=order_log, combat=action_addresses, extra_atlas=extra_atlas, wizard_combat=casting and combat, registry=registry,
            native_sprite_lighting=native_sprite_lighting, mixed_combat=mixed_combat,
        )[0],
        ORDER_WRITER_RAM - PAYLOAD_RAM: renderer.log_native_order(
            ORDER_WRITER_RAM, *order_log, unique_buckets=unique_order_buckets,
        ),
        0x800: b"" if mixed_combat or split_format or (shared_format and not slasher_combat) else metadata,
        0xc00: jump(PAYLOAD_RAM + 0x1400) + bytes(4),
        0xe00: menu_return(VARIANT_UPLOAD_RAM, floor_aware=True),
        0xe80: vram_guard(lower_floor=True, right_edge=texture_pages[-1][0] + 64),
    }
    if extra_type is None:
        sections[ORDER_LOG_RAM - PAYLOAD_RAM] = bytes(8 * renderer.ORDER_LOG_ENTRIES)
    if extra_type is not None or room_default:
        sections[SUPPRESS_RAM - PAYLOAD_RAM] = jump(suppress_addr) + bytes(4)
        sections[WALK_SUPPRESS_DELAY_RAM - PAYLOAD_RAM] = jump(delay_addr) + bytes(4)
    sections.update(extra_sections)
    sections.update(combat_sections)
    if academy_sections is not None:
        sections.update(academy_sections)
    pages = tuple((x, y) for x, y, _ in texture_pages)
    blob = compact_payload(sections, images, clut, pages, texture_pages[0][2], clut_rect,
                           EXPANDED_RESIDENT_BYTES if expanded_level_six or room_default else LOWER_RESIDENT_BYTES)
    return blob.ljust(academy_banks.ROOM_STRIDE, b"\0") if room_bank or room_default else blob


def compact_payload(sections, images, clut, pages, texture_height, clut_rect, resident_bytes=LOWER_RESIDENT_BYTES):
    bands = []
    offset = resident_bytes
    for (x, y), image in zip(pages, images, strict=True):
        sections[offset] = image
        bands.append(((x, y, 64, 128), offset, BAND_BYTES))
        bands.append(((x, y + 128, 64, texture_height - 128), offset + BAND_BYTES, BAND_BYTES))
        offset += BAND_BYTES * 2
    sections[offset] = clut
    bands.append((clut_rect, offset, 2048))
    sections[0x10] = b"".join(struct.pack("<4H", *rect) for rect, _, _ in bands)
    sections[0x1400] = variant_uploader(bands, False, True, PAYLOAD_RAM + 0x1400)
    return assemble_payload(sections, offset + 2048)


def payload(directory, walk_atlas=None, goblin_variants=None, dos_light_preview=None):
    if dos_light_preview is not None and goblin_variants is None:
        raise ValueError("The DOS lighting preview needs the four-palette goblin atlas.")
    if goblin_variants is not None:
        if walk_atlas is None:
            raise ValueError("The green goblin variants need the idle and walk atlases for type 70.")
        return variant_payload(directory, walk_atlas, goblin_variants, dos_light_preview)
    walking = walk_atlas is not None
    colors, image, metadata = read_atlas(directory, "idle", 192, 0x20, 0x16 if walking else 0)
    walk_ready = WALK_READY_RAM if walking else None
    delay_ram = WALK_SUPPRESS_DELAY_RAM if walking else SUPPRESS_DELAY_RAM
    clut_position = (384, 448) if walking else (448, 256)
    clut = (clut_position[1] << 6) | (clut_position[0] >> 4)
    if walking:
        walk_colors, walk_image, walk_metadata = read_atlas(walk_atlas, "walk", 224, 0x80, 0x17)
        if walk_colors != colors:
            raise ValueError("Idle and walk atlases use different RGB555 palettes.")
    sections = {
        0: struct.pack("<I", PAYLOAD_MAGIC),
        0x10: struct.pack("<8H", 384, 256, 64, 128 if walking else 192, *clut_position, 16, 1),
        0x30: struct.pack("<16H", *colors),
        0x90: renderer.DOS_IDLE_DIRECTIONS,
        0x100: renderer.suppress(SUPPRESS_RAM, walk_ready=walk_ready),
        delay_ram - PAYLOAD_RAM: renderer.suppress(delay_ram, "a0", walk_ready),
        0x200: renderer.draw(DRAW_RAM, PAYLOAD_RAM + 0x800, PAYLOAD_RAM + 0x90, clut, walk_ready)[0],
        0x800: metadata,
        0x1000: image,
    }
    if walking:
        sections[0x20] = struct.pack("<4H", 384, 384, 64, 64)
        sections[0x50] = struct.pack("<8H", 448, 256, 64, 128, 448, 384, 64, 96)
        sections[WALK_UPLOAD_RAM - PAYLOAD_RAM] = walking_uploader()
        sections[MENU_RAM - PAYLOAD_RAM] = menu_return()
        sections[VRAM_GUARD_RAM - PAYLOAD_RAM] = vram_guard()
        sections[0x900] = walk_metadata
        sections[IDLE_PAYLOAD_BYTES] = struct.pack("<I", WALK_MAGIC)
        sections[IDLE_PAYLOAD_BYTES + WALK_HEADER_BYTES] = walk_image
    else:
        sections[UPLOAD_RAM - PAYLOAD_RAM] = uploader()
    size = IDLE_PAYLOAD_BYTES + (WALK_PAYLOAD_BYTES if walking else 0)
    return assemble_payload(sections, size)


def assemble_payload(sections, size):
    result = bytearray(size)
    end = 0
    for offset, content in sorted(sections.items()):
        if offset < end or offset + len(content) > len(result):
            raise ValueError(f"Payload section {offset:#x}..{offset + len(content):#x} overlaps {end:#x} or exceeds {size:#x}.")
        end = offset + len(content)
        result[offset:end] = content
    return bytes(result)

def make_tables():
    edc = []
    forward = []
    backward = [0] * 256
    for index in range(256):
        accumulator = index
        for _ in range(8):
            accumulator = (accumulator >> 1) ^ (0xD8018001 if accumulator & 1 else 0)
        edc.append(accumulator)
        value = index << 1
        if value & 0x100:
            value ^= 0x11d
        forward.append(value)
        backward[index ^ value] = index
    return edc, forward, backward

EDC, ECC_FORWARD, ECC_BACKWARD = make_tables()

def parity(source, major_count, minor_count, major_mult, minor_increment):
    size = major_count * minor_count
    result = bytearray(2 * major_count)
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        a = b = 0
        for _ in range(minor_count):
            value = source[index]
            index = (index + minor_increment) % size
            a = ECC_FORWARD[a ^ value]
            b ^= value
        a = ECC_BACKWARD[ECC_FORWARD[a] ^ b]
        result[major] = a
        result[major + major_count] = a ^ b
    return result

def form1_sector(original, data):
    if len(original) != SECTOR_SIZE or len(data) != 2048 or original[15] != 2:
        raise ValueError("Expected a raw Mode 2 sector and exactly 2048 payload bytes.")
    if original[16:20] != original[20:24] or original[18] & 0x20:
        raise ValueError("Expected matching Mode 2 Form 1 subheaders.")
    result = bytearray(original)
    result[24:2072] = data
    accumulator = 0
    for value in result[16:2072]:
        accumulator = (accumulator >> 8) ^ EDC[(accumulator ^ value) & 255]
    struct.pack_into("<I", result, 2072, accumulator)
    result[12:16] = b"\0" * 4
    result[2076:2248] = parity(result[12:2076], 86, 24, 2, 86)
    result[2248:2352] = parity(result[12:2248], 52, 43, 86, 88)
    result[12:16] = original[12:16]
    return result

# The native font stores four monochrome glyph planes in each 4-bit texel.
# AVATAR section 7 contains two KiB of palettes followed by the texture.
MENU_BUTTON_GLYPHS = {
    "○": (0x80, ("..##..", ".#..#.", "#....#", "#....#", "#....#", "#....#", ".#..#.", "..##..")),
    "□": (0x81, ("######", "#....#", "#....#", "#....#", "#....#", "#....#", "#....#", "######")),
    "△": (0x82, ("..##..", "..##..", ".#..#.", ".#..#.", ".#..#.", "#....#", "#....#", "######")),
    "×": (0x83, ("#....#", ".#..#.", ".#..#.", "..##..", "..##..", ".#..#.", ".#..#.", "#....#")),
}


def menu_label(label):
    return b"".join(
        struct.pack(">H", MENU_BUTTON_GLYPHS[char][0]) if char in MENU_BUTTON_GLYPHS else char.encode("ascii")
        for char in label
    ) + b"\x1f"


def menu_font_sector(track):
    header = read_sector(track, AVATAR_LBA)
    font_start, font_end = struct.unpack_from("<II", header, 24 + 7 * 4)
    if font_start % 2048 or font_end - font_start != 0x8800:
        raise ValueError("Unexpected AVATAR menu font extent.")
    lba = AVATAR_LBA + font_start // 2048 + 1
    original = read_sector(track, lba)
    texture = bytearray(original[24:2072])
    if form1_sector(original, texture) != original:
        raise ValueError("Original menu font sector failed integrity check.")
    for code, rows in MENU_BUTTON_GLYPHS.values():
        # Codes 0x80–0x83 are blank eight-pixel glyphs in plane 3, row 0.
        x = (code - 0x80) * 8
        if any(texture[y * 128 + x // 2 + col] & 0x88 for y in range(16) for col in range(4)):
            raise ValueError(f"Menu button glyph slot {code:#x} is already occupied.")
        for y, row in enumerate(rows, 4):
            for offset, pixel in enumerate(row, 1):
                if pixel == "#":
                    col = x + offset
                    texture[y * 128 + col // 2] |= 8 << (4 * (col % 2))
    return lba, form1_sector(original, texture)


def draw_menu_legend(c, y=210, right_edge=None, align_right=False):
    c.mem("sw", "a0", 16, "sp")
    c.jump(MENU_TEXT_WIDTH, True)
    c.nop()
    c.mem("lw", "a2", 16, "sp")
    c.imm("ori", "a0", "zero", right_edge if align_right else 320)
    c.alu("subu", "a0", "a0", "v0")
    if not align_right:
        c.shift("sra", "a0", "a0", 1)
    if right_edge is not None and not align_right:
        c.imm("ori", "t0", "zero", right_edge)
        c.alu("subu", "t0", "t0", "v0")
        c.alu("slt", "t1", "a0", "t0")
        c.branch("bne", "t1", "zero", "legend_fits")
        c.nop()
        c.alu("addu", "a0", "t0", "zero")
        c.label("legend_fits")
    c.jump(MENU_TEXT_DRAW, True)
    c.imm("ori", "a1", "zero", y)


def options_help():
    """Append an options legend after the stock items and before frame submission."""
    root = menu_label("○ OK  × Exit")
    submenu = menu_label("○ OK  × Back")
    root_address = OPTIONS_HELP + 0x90
    submenu_address = root_address + len(root)
    c = Code(OPTIONS_HELP)
    c.imm("addiu", "sp", "sp", -24)
    c.mem("sw", "ra", 20, "sp")
    c.jump(OPTIONS_DRAW_ITEMS, True)
    c.nop()
    c.mem("lw", "t0", 0x398, "gp")  # Options page.
    c.imm("ori", "t1", "zero", 7)
    c.branch("beq", "t0", "t1", "submenu")
    c.imm("sltiu", "t1", "t0", 4)
    c.branch("beq", "t1", "zero", "done")  # Save/load pages and exit states.
    c.nop()
    c.branch("bne", "t0", "zero", "submenu")
    c.nop()
    c.address("a0", root_address)
    c.branch("beq", "zero", "zero", "measure")
    c.nop()
    c.label("submenu")
    c.address("a0", submenu_address)
    c.label("measure")
    draw_menu_legend(c)
    c.label("done")
    c.mem("lw", "ra", 20, "sp")
    c.nop()
    ret(c, lambda: c.imm("addiu", "sp", "sp", 24))
    code = c.out()
    if len(code) > root_address - OPTIONS_HELP:
        raise ValueError("Options controls routine overlaps its labels.")
    return code.ljust(root_address - OPTIONS_HELP, b"\0") + root + submenu


def inventory_help():
    """Build the current item actions and Cross prompt into one footer."""
    actions = [
        menu_label("".join(action + " " for action in (square, circle, triangle) if action))
        for circle in ("", "○ Pick up", "○ Place")
        for square in ("", "□ Drop")
        for triangle in ("", "△ Use", "△ Open")
    ]
    navigation = [menu_label(f"× {action}") for action in ("Exit", "Back", "Cancel")]
    if max(map(len, actions)) - 1 + max(map(len, navigation)) > 40:
        raise ValueError("Inventory controls exceed the footer string buffer.")
    table_offset = 0x160
    table = INVENTORY_HELP + table_offset
    address = table + 4 * len(actions)
    pointers = []
    for label in actions + navigation:
        pointers.append(address)
        address += len(label)

    c = Code(INVENTORY_HELP)
    c.imm("addiu", "sp", "sp", -64)
    c.mem("sw", "ra", 60, "sp")
    c.shift("sll", "t0", "s1", 1)
    c.alu("addu", "t0", "s6", "t0")
    c.mem("lh", "a0", 0, "t0")
    c.jump(0x80045380, True)  # Same read-only item lookup as native Triangle.
    c.imm("ori", "a1", "zero", 2)

    # Triangle contributes 0, 1 or 2 to the action row index.
    c.branch("beq", "v0", "zero", "circle")
    c.imm("ori", "t0", "zero", 0)
    c.mem("lhu", "t1", 0, "v0")
    c.imm("ori", "t2", "zero", 0x13)  # Native Square excludes this cursor.
    c.imm("andi", "t1", "t1", 0x1ff)
    c.imm("addiu", "t1", "t1", -0x80)
    c.imm("sltiu", "t1", "t1", 0x10)  # Containers, including the Rune Bag.
    c.branch("beq", "s1", "t2", "circle")
    c.imm("addiu", "t0", "t1", 1)
    c.imm("addiu", "t0", "t0", 3)  # Square is available on this occupied slot.

    c.label("circle")
    c.branch("bne", "s3", "zero", "held")
    c.nop()
    c.branch("beq", "v0", "zero", "actions")
    c.nop()
    c.branch("beq", "zero", "zero", "actions")
    c.imm("addiu", "t0", "t0", 6)  # Pick up.
    c.label("held")
    c.branch("beq", "s1", "s7", "actions")
    c.nop()
    c.imm("addiu", "t0", "t0", 12)  # Place on a different slot.

    c.label("actions")
    c.shift("sll", "t0", "t0", 2)
    c.address("t1", table)
    c.alu("addu", "t1", "t1", "t0")
    c.mem("lw", "t1", 0, "t1")
    c.imm("addiu", "a0", "sp", 20)  # Up to 39 bytes before the saved return address.
    c.imm("ori", "t2", "zero", 0x1f)
    c.label("copy_actions")
    c.mem("lbu", "t0", 0, "t1")
    c.imm("addiu", "t1", "t1", 1)
    c.branch("beq", "t0", "t2", "navigation")
    c.mem("sb", "t0", 0, "a0")
    c.branch("beq", "zero", "zero", "copy_actions")
    c.imm("addiu", "a0", "a0", 1)

    c.label("navigation")
    c.address("a1", pointers[-1])
    c.branch("bne", "s3", "zero", "append")
    c.mem("lw", "t0", 0x31c, "gp")  # Container pointer.
    c.address("a1", pointers[-3])
    c.branch("beq", "t0", "zero", "append")
    c.nop()
    c.address("a1", pointers[-2])
    c.label("append")
    c.jump(0x8007F698, True)  # Native encoded string copy.
    c.nop()
    c.imm("addiu", "a0", "sp", 20)
    draw_menu_legend(c, right_edge=264)  # Shift left only when the text would reach the HUD.
    c.mem("lw", "ra", 60, "sp")
    c.nop()
    c.jump(SUBMIT_MENU_FRAME)
    c.imm("addiu", "sp", "sp", 64)

    code = c.out()
    if len(code) > table_offset:
        raise ValueError("Inventory controls routine overlaps its labels.")
    return code.ljust(table_offset, b"\0") + struct.pack(f"<{len(actions)}I", *pointers[:len(actions)]) + b"".join(actions + navigation)


def rune_spell_help():
    """Append footers to the rune grid and spell book before frame submission."""
    labels = (
        menu_label("× Back"),
        menu_label("○ Pick  × Exit"),
        menu_label("○ Pick  × Back"),
    )
    label_address = RUNE_HELP + 0x70
    c = Code(RUNE_HELP)
    c.address("a0", label_address)
    c.branch("beq", "zero", "zero", "draw")
    c.nop()
    spell_help = c.origin + 4 * len(c.words)
    # The spell book's s3 is set while browsing learned mantras.
    c.address("a0", label_address + len(labels[0]))
    c.branch("beq", "s3", "zero", "draw")
    c.nop()
    c.address("a0", label_address + len(labels[0]) + len(labels[1]))
    c.label("draw")
    c.imm("addiu", "sp", "sp", -24)
    c.mem("sw", "ra", 20, "sp")
    draw_menu_legend(c, y=215)
    c.mem("lw", "ra", 20, "sp")
    c.nop()
    c.jump(SUBMIT_MENU_FRAME)
    c.imm("addiu", "sp", "sp", 24)
    code = c.out()
    if len(code) > label_address - RUNE_HELP:
        raise ValueError("Rune and spell controls routine overlaps its labels.")
    return spell_help, code.ljust(label_address - RUNE_HELP, b"\0") + b"".join(labels)


def dialogue_help():
    """Show controls only when the conversation loop is waiting for input."""
    advance = menu_label("○ Continue")
    replies = menu_label("○ Reply")
    text = DIALOGUE_HELP + 0xc0
    c = Code(DIALOGUE_HELP)
    # The shared frame routine saves its caller at sp+16. The callers below
    # are all in 0x8002xxxx, so their low half identifies the dialogue state.
    c.mem("lw", "t0", 16, "sp")
    c.imm("ori", "t1", "zero", 0x6f9c)  # Reply selection.
    c.imm("andi", "t0", "t0", 0xffff)
    c.branch("beq", "t0", "t1", "replies")
    c.imm("ori", "t1", "zero", 0x8c9c)  # Scripted wait.
    c.branch("bne", "t0", "t1", "overflow")
    c.imm("ori", "t1", "zero", 0x9204)  # Wait for the next page.
    c.branch("bne", "s2", "zero", "advance")  # Input-enabled dialogue wait.
    c.nop()
    c.label("native")
    c.jump(SUBMIT_MENU_FRAME)
    c.nop()
    c.label("overflow")
    c.branch("beq", "t0", "t1", "more")
    c.imm("ori", "t1", "zero", 0x93ec)  # Wait for the next page (initial fill).
    c.branch("bne", "t0", "t1", "native")
    c.nop()
    c.label("more")
    c.branch("blez", "s7", "zero", "native")  # No undisplayed lines.
    c.nop()
    c.label("advance")
    c.imm("lui", "a0", "zero", text >> 16)
    c.branch("beq", "zero", "zero", "draw")
    c.imm("ori", "a0", "a0", text)
    c.label("replies")
    c.branch("beq", "s0", "zero", "native")  # The reply was just confirmed.
    c.imm("lui", "a0", "zero", text >> 16)
    c.imm("ori", "a0", "a0", text + len(advance))
    c.label("draw")
    c.imm("addiu", "sp", "sp", -24)
    c.mem("sw", "ra", 20, "sp")
    draw_menu_legend(c, y=217, right_edge=304, align_right=True)
    c.mem("lw", "ra", 20, "sp")
    c.nop()
    c.jump(SUBMIT_MENU_FRAME)
    c.imm("addiu", "sp", "sp", 24)
    code = c.out()
    if len(code) > text - DIALOGUE_HELP:
        raise ValueError("Dialogue controls routine overlaps its labels.")
    return code.ljust(text - DIALOGUE_HELP, b"\0") + advance + replies


def map_help():
    """Offer the marker toggle only where the native cursor can mark a tile."""
    exit_label = menu_label("× Exit")
    mark_label = menu_label("○ Toggle marker  × Exit")
    labels = MAP_HELP + 0x80
    c = Code(MAP_HELP)
    c.imm("addiu", "sp", "sp", -24)
    c.mem("sw", "ra", 20, "sp")
    # The map renderer passes the current cursor packet as a physical RAM address.
    c.imm("lui", "t0", "zero", 0x8000)
    c.alu("OR", "t0", "t0", "a2")
    c.mem("lh", "t1", 8, "t0")  # Cursor X.
    c.mem("lh", "t2", 0x1a, "t0")  # Cursor Y.
    c.imm("addiu", "t1", "t1", -20)
    # The native tile conversion truncates (y - 27) / 3 toward zero.
    c.imm("addiu", "t2", "t2", -25)
    c.imm("sltiu", "t1", "t1", 64 * 3)
    c.imm("sltiu", "t2", "t2", 64 * 3 + 2)
    c.alu("AND", "t1", "t1", "t2")
    c.address("a0", labels)
    c.branch("beq", "t1", "zero", "draw")
    c.nop()
    c.address("a0", labels + len(exit_label))
    c.label("draw")
    draw_menu_legend(c, y=217)
    c.mem("lw", "ra", 20, "sp")
    c.nop()
    c.jump(SUBMIT_MENU_FRAME)
    c.imm("addiu", "sp", "sp", 24)
    code = c.out()
    if len(code) > labels - MAP_HELP:
        raise ValueError("Map controls routine overlaps its labels.")
    return code.ljust(labels - MAP_HELP, b"\0") + exit_label + mark_label


def menu_startup(spell_code, warren_dialogue=False):
    """Copy the menu code above the lowered stack before native heap setup."""
    sections = {
        OPTIONS_HELP - MENU_CODE_RAM: options_help(),
        DIALOGUE_HELP - MENU_CODE_RAM: dialogue_help(),
        INVENTORY_HELP - MENU_CODE_RAM: inventory_help(),
        RUNE_HELP - MENU_CODE_RAM: spell_code,
        MAP_HELP - MENU_CODE_RAM: map_help(),
    }
    cleanup_offset = 0x6b0
    length = cleanup_offset + 0x40
    if warren_dialogue:
        offset = WARREN_TALK - MENU_CODE_RAM
        sections[offset] = warren_talk()
        length = (offset + len(sections[offset]) + 3) & ~3
    source = MENU_STARTUP + 0x40

    # The native game can reuse the on-disc template's RAM after boot.
    cleanup = Code(MENU_CODE_RAM + cleanup_offset)
    cleanup.address("t0", MENU_STARTUP)
    cleanup.imm("ori", "t2", "zero", source - MENU_STARTUP + length)
    cleanup.label("clear")
    cleanup.mem("sw", "zero", 0, "t0")
    cleanup.imm("addiu", "t2", "t2", -4)
    cleanup.branch("bne", "t2", "zero", "clear")
    cleanup.imm("addiu", "t0", "t0", 4)
    cleanup.jump(NATIVE_HEAP_INIT)
    cleanup.nop()
    sections[cleanup_offset] = cleanup.out()
    if MENU_CODE_RAM + length > 0x80200000:
        raise ValueError("Menu controls exceed the reserved space above the stack.")
    c = Code(MENU_STARTUP)
    c.address("t0", source)
    c.address("t1", MENU_CODE_RAM)
    c.imm("ori", "t2", "zero", length)
    c.label("copy")
    c.mem("lw", "t3", 0, "t0")
    c.imm("addiu", "t0", "t0", 4)
    c.mem("sw", "t3", 0, "t1")
    c.imm("addiu", "t2", "t2", -4)
    c.branch("bne", "t2", "zero", "copy")
    c.imm("addiu", "t1", "t1", 4)
    c.jump(cleanup.origin)
    c.nop()
    boot = c.out()
    if len(boot) > source - MENU_STARTUP:
        raise ValueError("Menu startup routine overlaps its source data.")
    return boot.ljust(source - MENU_STARTUP, b"\0") + assemble_payload(sections, length)


def warren_talk():
    # This entry replaces the native branch after the conversation lookup.
    # The stock Talk action has already checked the actor's eligibility.
    c = Code(WARREN_TALK)
    line = menu_label("I remember the sun.")
    text = WARREN_TALK + 0xa0
    c.branches.append((len(c.words), "check_failure"))
    c.add(0x04400000)  # bltz v0, check_failure
    c.imm("ori", "a0", "zero", 0xe01)
    c.jump(0x80025fb4)
    c.nop()
    c.label("check_failure")
    c.mem("lhu", "t0", 0x1f0, "gp")
    c.imm("ori", "t1", "zero", 207)
    c.branch("bne", "t0", "t1", "no_response")
    c.mem("lw", "t0", 0x998, "gp")
    c.address("t1", LEVEL_ONE_MODELS + 5 * 0x380)
    c.branch("bne", "t0", "t1", "no_response")
    c.mem("lw", "t0", 0xd28, "gp")
    c.nop()
    c.mem("lhu", "t0", 0, "t0")
    c.nop()
    c.imm("andi", "t0", "t0", 0x1ff)
    c.imm("ori", "t1", "zero", 97)
    c.branch("bne", "t0", "t1", "no_response")
    c.nop()
    # Open the native portrait panel, display Warren's line, and let the
    # standard input-enabled wait handle Circle and the dialogue footer.
    # Talk and the stock conversation wrapper share the same frame layout.
    c.jump(0x800260fc, True)
    c.nop()
    # For this actor the stock name builder returns a long description.
    # Fit the panel's nameplate with the personal name.
    c.address("a0", 0x800ca3a4)
    c.address("a1", text + len(line))
    c.jump(0x8007f698, True)
    c.nop()
    c.address("a0", text)
    c.jump(0x80027180, True)
    c.mem("sh", "zero", 0x928, "gp")  # No reply choices on this page.
    c.imm("ori", "a1", "zero", 1)
    c.jump(0x80028c28, True)
    c.imm("ori", "a0", "zero", 0)
    c.jump(0x800260cc)  # Native panel cleanup and return to the dungeon.
    c.nop()
    c.label("no_response")
    c.jump(0x80025ff8)
    c.nop()
    code = c.out()
    assert len(code) <= 0xa0
    return code.ljust(text - WARREN_TALK, b"\0") + line + menu_label("Warren")


def edit_executable(original, payload_lba=PAYLOAD_LBA, walking=False, wide=False,
                    lower_payload_lba=None, lizard_payload_lba=None, rat_payload_lba=None,
                    wizard_payload_lba=None, expanded_level_six=False, academy_runtime=False, level_one_dialogue=False,
                    room_payload_lbas=None, menu_controls=False, warren_dialogue=False):
    target = bytearray(original)
    deferred_ordering = any(
        lba is not None for lba in (lizard_payload_lba, rat_payload_lba, wizard_payload_lba)
    )
    floor_aware = lower_payload_lba is not None or deferred_ordering
    code = {
        BOOT: (
            floor_loader(payload_lba, lower_payload_lba, lizard_payload_lba, rat_payload_lba, wizard_payload_lba,
                         expanded_level_six, academy_runtime, level_one_dialogue, room_payload_lbas)
            if floor_aware else loader(payload_lba, walking, wide)
        ),
        SUPPRESS_NORMAL: gate(SUPPRESS_NORMAL, SUPPRESS_RAM, "v1", walking, floor_aware),
        SUPPRESS_DELAY: gate(SUPPRESS_DELAY, WALK_SUPPRESS_DELAY_RAM if walking else SUPPRESS_DELAY_RAM, "a0", walking, floor_aware),
        DRAW_GATE: gate(DRAW_GATE, DRAW_RAM, walking=walking, floor_aware=floor_aware),
    }
    if warren_dialogue and not menu_controls:
        raise ValueError("Warren dialogue requires the menu controls runtime.")
    if menu_controls:
        spell_help, spell_code = rune_spell_help()
        code[MENU_STARTUP] = menu_startup(spell_code, warren_dialogue)
    if academy_runtime:
        code.update(academy_banks.gates())
    if walking:
        code[EXPANDED_MENU_GATE if expanded_level_six else MENU_GATE] = menu_gate(expanded_level_six)
        code[VRAM_UPLOAD_GATE] = vram_upload_gate(floor_aware, expanded_level_six)
    if deferred_ordering:
        code[ACTOR_GATE] = actor_gate()
    for (address, blob), next_address in zip(sorted(code.items()), sorted(code)[1:]):
        if address + len(blob) > next_address:
            raise ValueError(f"Overlapping executable stubs at 0x{address:08x} and 0x{next_address:08x}.")
    for address, blob in code.items():
        offset = 2048 + address - EXE_LOAD
        if any(target[offset:offset + len(blob)]):
            raise ValueError(f"Unexpected nonzero data at resident stub 0x{address:08x}.")
        target[offset:offset + len(blob)] = blob

    hooks = (
        (0x800728a0, jump(0x80029f50, True), jump(BOOT, True)),
        (0x80072998, jump(0x80029f50, True), jump(BOOT, True)),
        (0x80072bbc, jump(0x80029f50, True), jump(BOOT, True)),
        (0x8002a650, jump(0x800757c4, True), jump(DRAW_GATE, True)),
        (0x8002b680, struct.pack("<I", 0xac620000), jump(SUPPRESS_NORMAL)),
        (0x8002aedc, jump(0x8002b684) + struct.pack("<I", 0xac820000), jump(SUPPRESS_DELAY) + bytes(4)),
    )
    if walking:
        hooks += (
            (0x8006f2c8, jump(0x8005b368, True) + bytes(4),
             jump(EXPANDED_MENU_GATE, True) + struct.pack("<I", 0x340f0000))
            if expanded_level_six else (0x8006f2c8, jump(0x8005b368, True), jump(MENU_GATE, True)),
            (0x800905d4, bytes.fromhex("e0ffbd271000b0af"), jump(VRAM_UPLOAD_GATE) + bytes(4)),
        )
    if deferred_ordering:
        stack_prologue = bytes.fromhex("b8febd27")
        save_actor = bytes.fromhex("e000a5af")
        hooks += ((0x8002a258, stack_prologue + save_actor, jump(ACTOR_GATE) + stack_prologue),)
    if expanded_level_six:
        hooks += ((0x800260e4, jump(0x8003ea5c, True) + bytes(4),
                   jump(EXPANDED_MENU_GATE, True) + struct.pack("<I", 0x340f0001)),)
    if academy_runtime:
        hooks += ((academy_banks.FRAME_HOOK, bytes.fromhex("a0048397e8ffbd27"),
                   jump(academy_banks.GATE) + bytes(4)),)
    if menu_controls:
        hooks += (
            # CRT reads this stack ceiling for both SP and the heap size.
            (NATIVE_STACK_TABLE_ENTRY, struct.pack("<I", 0x200000),
             struct.pack("<I", MENU_CODE_RAM & 0x1fffff)),
            (MENU_STARTUP_CALL, jump(NATIVE_HEAP_INIT, True), jump(MENU_STARTUP, True)),
            (OPTIONS_DRAW_CALL, jump(OPTIONS_DRAW_ITEMS, True), jump(OPTIONS_HELP, True)),
            (INVENTORY_SUBMIT_CALL, jump(SUBMIT_MENU_FRAME, True), jump(INVENTORY_HELP, True)),
            (RUNE_SUBMIT_CALL, jump(SUBMIT_MENU_FRAME, True), jump(RUNE_HELP, True)),
            (MAP_SUBMIT_CALL, jump(SUBMIT_MENU_FRAME, True), jump(MAP_HELP, True)),
            # Keep the map and cursor uploads beyond the font texture. Move the
            # map CLUT past the font's palettes on the shared last VRAM row.
            (0x8001367C, struct.pack("<I", 0x34070140), struct.pack("<I", 0x34070180)),
            (0x800136EC, struct.pack("<I", 0x340701E0), struct.pack("<I", 0x34070220)),
            (0x80013718, struct.pack("<I", 0x00002821), struct.pack("<I", 0x34050100)),
            (SPELL_SUBMIT_CALL, jump(SUBMIT_MENU_FRAME, True), jump(spell_help, True)),
            (DIALOGUE_SUBMIT_CALL, jump(SUBMIT_MENU_FRAME, True), jump(DIALOGUE_HELP, True)),
            # Raise the lower panel's reply rows six pixels to clear the footer.
            (0x80028AB8, struct.pack("<I", 0x34110090), struct.pack("<I", 0x3411008A)),
        )
    if warren_dialogue:
        hooks += ((0x80025fac, bytes.fromhex("12004004"), jump(WARREN_TALK)),)
    for address, expect, replace in hooks:
        offset = 2048 + address - EXE_LOAD
        if target[offset:offset + len(expect)] != expect:
            raise ValueError(f"Unexpected instruction at 0x{address:08x}.")
        target[offset:offset + len(replace)] = replace
    return target

def read_sector(track, lba):
    track.seek(lba * SECTOR_SIZE)
    return track.read(SECTOR_SIZE)

def write_sector(track, lba, sector):
    track.seek(lba * SECTOR_SIZE)
    track.write(sector)

def build(source, atlas, output, walk_atlas=None, goblin_variants=None):
    with source.open("rb") as track:
        if hashlib.file_digest(track, "sha1").hexdigest() != OFFICIAL_HASH:
            raise ValueError("Source is not the verified original Japanese Rev 1 Track 1.")
        filename = b"SLPS_007.42;1"
        root = read_sector(track, 22)
        marker = root.index(filename)
        extent, = struct.unpack_from("<I",root,marker - 31)
        length, = struct.unpack_from("<I",root,marker - 23)
        if extent != EXE_LBA or length != 761856:
            raise ValueError("Unexpected Japanese boot executable extent.")
        exe_sectors = [read_sector(track, extent + index) for index in range(length // 2048)]
        exe = b"".join(sector[24:2072] for sector in exe_sectors)
        disk_payload = payload(atlas, walk_atlas, goblin_variants)
        edited = edit_executable(exe, walking=walk_atlas is not None, wide=goblin_variants is not None)
        modified = {}
        for index, sector in enumerate(exe_sectors):
            offset = index * 2048
            previous = exe[offset:offset + 2048]
            data = edited[offset:offset + 2048]
            if data == previous:
                continue
            if form1_sector(sector, previous) != sector:
                raise ValueError(f"Original integrity bytes did not round trip at LBA {extent+index}.")
            modified[extent + index] = form1_sector(sector, data)
        for index in range(len(disk_payload) // 2048):
            lba = PAYLOAD_LBA + index
            sector = read_sector(track, lba)
            if any(sector[24:2072]) or form1_sector(sector, bytes(2048)) != sector:
                raise ValueError(f"Reserved LBA {lba} is not an empty valid Form 1 sector.")
            begin = index * 2048
            modified[lba] = form1_sector(sector, disk_payload[begin:begin + 2048])

        with output.open("xb") as target:
            track.seek(0)
            shutil.copyfileobj(track, target, length=1024 * 1024)
            for lba, sector in modified.items():
                write_sector(target, lba, sector)
    print("Modified LBAs:", ", ".join(map(str, sorted(modified))))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("japanese_track", type=Path)
    parser.add_argument("atlas_directory", type=Path)
    parser.add_argument("output_track", type=Path)
    parser.add_argument("--walk-atlas", type=Path)
    parser.add_argument("--goblin-variants", type=Path)
    args = parser.parse_args()
    build(args.japanese_track, args.atlas_directory, args.output_track, args.walk_atlas, args.goblin_variants)

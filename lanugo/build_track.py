#!/usr/bin/env python3
"""Build the experimental Japanese Rev 1 Lanugo patch on a scratch data track."""

import argparse
import csv
import hashlib
import shutil
import struct
from pathlib import Path

from mipswords import Code, ret
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
BOOT = 0x800C2300
SUPPRESS_NORMAL = 0x800C23C0
SUPPRESS_DELAY = 0x800C2400
DRAW_GATE = 0x800C2440
VRAM_UPLOAD_GATE = 0x800C2480
MENU_GATE = 0x800C24B0
ACTOR_GATE = 0x800C24E0
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


def menu_gate():
    c = Code(MENU_GATE)
    c.address("t0", PAYLOAD_RAM)
    c.mem("lw", "t1", 0, "t0")
    c.address("t2", PAYLOAD_MAGIC)
    c.branch("bne", "t1", "t2", "native")
    c.nop()
    c.jump(MENU_RAM)
    c.nop()
    c.label("native")
    c.jump(0x8005b368)
    c.nop()
    return c.out()


def menu_return(upload_ram=WALK_UPLOAD_RAM, floor_aware=False):
    c = Code(MENU_RAM)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
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


def vram_upload_gate(floor_aware=False):
    c = Code(VRAM_UPLOAD_GATE)
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
                 wizard_payload_lba=None, expanded_level_six=False):
    c = Code(BOOT)
    c.imm("addiu", "sp", "sp", -32)
    c.mem("sw", "ra", 28, "sp")
    c.mem("sw", "a0", 24, "sp")
    c.address("t2", PAYLOAD_RAM)
    c.mem("sw", "zero", 4, "t2")
    c.mem("sw", "zero", MODEL_OWNER_OFFSET, "t2")
    c.jump(0x80029f50, True)
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
        # One byte per native floor index, measured in sectors from the Level 1 payload.
        floor_table_ram = BOOT + 0xb4
        payload_levels = (None, lower_payload_lba, lizard_payload_lba, lizard_payload_lba,
                          lower_payload_lba, wizard_payload_lba, lower_payload_lba, rat_payload_lba, None)
        floor_offsets = [255 if lba is None else lba - payload_lba for lba in payload_levels]
        floor_offsets[0] = 0
        if any(not 0 <= offset <= 255 for offset in floor_offsets):
            raise ValueError("The resident floor table requires payload starts within 254 sectors.")
        if any(lba is not None and not 0 < offset < 255
               for lba, offset in zip(payload_levels, floor_offsets, strict=True)):
            raise ValueError("Additional floor payloads must follow Level 1 in the resident floor table.")
        floor_table = bytes(floor_offsets)
        offset = (payload_lba - AVATAR_LBA) * 2048
        c.mem("lw", "t0", 24, "sp")
        c.imm("ori", "a2", "zero", RESIDENT_BYTES)
        c.imm("sltiu", "t2", "t0", len(floor_table))
        c.branch("beq", "t2", "zero", "done")
        c.alu("addu", "t1", "gp", "t0")
        c.mem("lbu", "t1", floor_table_ram - NATIVE_GP, "t1")
        c.imm("lui", "t3", "zero", offset >> 16)
        c.imm("sltiu", "t2", "t1", 255)
        c.branch("beq", "t2", "zero", "done")
        c.shift("sll", "a0", "t1", 11)
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


def variant_image_bands(texture_pages=variant_atlas.TEXTURE_PAGES):
    offset = RESIDENT_BYTES
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


def variant_payload(idle_atlas, walk_atlas, variants, dos_light_preview=None, floor_aware=False):
    sources = variant_sources(idle_atlas, walk_atlas, variants)
    pages = variant_atlas.TEXTURE_PAGES if dos_light_preview is None else preview_lighting.TEXTURE_PAGES
    images, clut, metadata = variant_atlas.build(sources, pages)
    bands = tuple(variant_image_bands(pages))
    atlas_end = RESIDENT_BYTES + sum(map(len, images))
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
        RESIDENT_BYTES: b"".join(images),
    }
    if dos_light_preview is None:
        sections[0xf00] = clut
        rectangles = tuple(rect for rect, _, _ in bands) + (clut_rect,)
    else:
        palettes = preview_lighting.palette_banks(dos_light_preview, clut)
        bands += ((clut_rect, atlas_end, len(palettes)),)
        sections[atlas_end] = palettes
        atlas_end += len(palettes)
        light = PAYLOAD_RAM + preview_lighting.LIGHT_LEVEL_OFFSET
        sections[preview_lighting.LIGHT_LEVEL_OFFSET] = bytes(1)
        sections[preview_lighting.SETTINGS_OFFSET] = preview_lighting.light_settings(dos_light_preview)
        sections[preview_lighting.SELECTOR_OFFSET] = preview_lighting.select_clut(
            shade_selector, light, shade_return, clut_id,
        )
        rectangles = tuple(rect for rect, _, _ in bands)
    sections[0x10] = b"".join(struct.pack("<4H", *rect) for rect in rectangles)
    sections[VARIANT_UPLOAD_RAM - PAYLOAD_RAM] = variant_uploader(bands, dos_light_preview is None, floor_aware)
    return assemble_payload(sections, atlas_end)


def lower_floor_atlas(variants):
    base = variants / f"type-{renderer.LOWER_GOBLIN_TYPE}"
    sources = (
        read_source_atlas(base / "idle", "idle", 192, 0x20, prefix="goblin"),
        read_source_atlas(base / "walk", "walk", 224, 0x80, prefix="goblin"),
    )
    return lower_atlas.build(sources)


def lower_floor_payload(variants):
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
    return compact_payload(sections, images, clut, lower_atlas.TEXTURE_PAGES, lower_atlas.HEIGHT, lower_atlas.CLUT_RECT)


def creature_sources(variants, actor_types, combat=False, casting=False):
    modes = [("idle", 0x20, None), ("walk", 0x80, None)]
    if combat or casting:
        poses = creature_atlas.COMBAT_SLOTS if combat else ()
        if casting:
            poses += (creature_atlas.CAST_SLOT,)
        modes.append(("combat", 0, poses))
    return tuple(
        tuple(read_source_atlas(
            variants / f"type-{actor}" / mode, mode, creature_atlas.SOURCE_HEIGHT, slot,
            prefix="creature", poses=poses,
        ) for actor in actor_types)
        for mode, slot, poses in modes
    )


def lizard_sources(variants, combat=False):
    return creature_sources(variants, creature_atlas.LIZARD_TYPES, combat)


def lizard_payload(variants, combat=False):
    return creature_payload(variants, creature_atlas.LIZARD_TYPES, creature_atlas.TEXTURE_PAGES, combat)


def rat_payload(variants):
    return creature_payload(variants, creature_atlas.LEVEL_EIGHT_RAT_TYPES, creature_atlas.RAT_TEXTURE_PAGES)


def creature_payload(variants, actor_types, texture_pages, combat=False, extra_type=None, casting=False,
                     expanded_level_six=False):
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
    if expanded_level_six:
        # Keep persistent frame lookups below 0x801f8000, where the native floor load writes.
        if not (casting and combat and extra_type == 92 and texture_pages == creature_atlas.TEXTURE_PAGES[:1]):
            raise ValueError("The expanded Level 6 atlas requires the wizard-combat and spider preview.")
        image, palettes, directional = creature_atlas.build_families(
            [creature_sources(variants, types) for types in LEVEL_SIX_DIRECTIONAL],
            creature_atlas.TEXTURE_PAGES[1],
        )
        images += (image,)
        texture_pages += creature_atlas.TEXTURE_PAGES[1:]
        # Each 16-color palette is one row of an eight-row, two-column CLUT.
        rows = [clut[i:i + 32] for i in range(0, len(clut), 32)] + list(palettes)
        rows += [bytes(32)] * (16 - len(rows))
        clut = b"".join(rows[i] + rows[i + 8] for i in range(8))
        clut_rect = x, y, 32, 8
        registry_data = bytearray(64 * 4)
        for row, actor in enumerate(actor_types):
            struct.pack_into("<HH", registry_data, 4 * (actor - 64), 0, creature_atlas.CLUT_BASE + row * 64)
        row = len(actor_types)
        table_offsets = (0x1000, 0x1c00, 0x1e00, 0x1200)
        for types, table, location in zip(LEVEL_SIX_DIRECTIONAL, directional, table_offsets, strict=True):
            compact = creature_atlas.compact_frame_table(table)
            if len(compact) > 0x200:
                raise ValueError("The compact Level 6 frame table exceeds its safe RAM range.")
            extra_sections[location] = compact
            for actor in types:
                palette = creature_atlas.CLUT_BASE + (row % 8) * 64 + row // 8
                struct.pack_into("<HH", registry_data, 4 * (actor - 64), location - 0x800, palette)
                row += 1
        extra_sections[0xf00] = registry_data
        order_log = PAYLOAD_RAM + ORDER_COUNT_OFFSET, PAYLOAD_RAM + LOWER_RESIDENT_BYTES
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
        phase_offset = 0xc10 if casting else 0x700
        combat_sections = {0xb0: actions, phase_offset: phases, 0x1600: metadata[0x400:]}
        metadata = metadata[:0x400]
        action_addresses = (
            PAYLOAD_RAM + 0xb0, PAYLOAD_RAM + phase_offset, PAYLOAD_RAM + 0x1600,
            actions[creature_atlas.DEATH_SLOT],
        )
    registry = PAYLOAD_RAM + 0xf00 if expanded_level_six else None
    suppress_addr = SUPPRESS_RAM if extra_type is None else PAYLOAD_RAM + 0x700
    delay_addr = WALK_SUPPRESS_DELAY_RAM if extra_type is None else PAYLOAD_RAM + 0xd00
    sections = {
        0: struct.pack("<I", PAYLOAD_MAGIC),
        0x90: renderer.DOS_IDLE_DIRECTIONS,
        suppress_addr - PAYLOAD_RAM: renderer.suppress(
            suppress_addr, walk_ready=WALK_READY_RAM, wide=True,
            palette_types=palette_types, order_writer=ORDER_WRITER_RAM,
            action_map=None if action_addresses is None else action_addresses[0], extra_type=extra_type,
            wizard_combat=casting and combat, registry=registry,
        ),
        delay_addr - PAYLOAD_RAM: renderer.suppress(
            delay_addr, "a0", WALK_READY_RAM, wide=True,
            palette_types=palette_types, order_writer=ORDER_WRITER_RAM,
            action_map=None if action_addresses is None else action_addresses[0], extra_type=extra_type,
            wizard_combat=casting and combat, registry=registry,
        ),
        0x200: renderer.draw(
            DRAW_RAM, PAYLOAD_RAM + 0x800, PAYLOAD_RAM + 0x90,
            clut=creature_atlas.CLUT_BASE, walk_ready=WALK_READY_RAM, wide=True,
            palette_types=palette_types, order_log=order_log, combat=action_addresses, extra_atlas=extra_atlas, wizard_combat=casting and combat, registry=registry,
        )[0],
        ORDER_WRITER_RAM - PAYLOAD_RAM: renderer.log_native_order(ORDER_WRITER_RAM, *order_log),
        0x800: metadata,
        0xc00: jump(PAYLOAD_RAM + 0x1400) + bytes(4),
        0xe00: menu_return(VARIANT_UPLOAD_RAM, floor_aware=True),
        0xe80: vram_guard(lower_floor=True, right_edge=texture_pages[-1][0] + 64),
    }
    if extra_type is None:
        sections[ORDER_LOG_RAM - PAYLOAD_RAM] = bytes(8 * renderer.ORDER_LOG_ENTRIES)
    else:
        sections[SUPPRESS_RAM - PAYLOAD_RAM] = jump(suppress_addr) + bytes(4)
        sections[WALK_SUPPRESS_DELAY_RAM - PAYLOAD_RAM] = jump(delay_addr) + bytes(4)
    sections.update(extra_sections)
    sections.update(combat_sections)
    pages = tuple((x, y) for x, y, _ in texture_pages)
    return compact_payload(sections, images, clut, pages, texture_pages[0][2], clut_rect,
                           EXPANDED_RESIDENT_BYTES if expanded_level_six else LOWER_RESIDENT_BYTES)


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
            raise ValueError("Payload sections overlap or exceed the reserved RAM.")
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

def edit_executable(original, payload_lba=PAYLOAD_LBA, walking=False, wide=False,
                    lower_payload_lba=None, lizard_payload_lba=None, rat_payload_lba=None,
                    wizard_payload_lba=None, expanded_level_six=False):
    target = bytearray(original)
    deferred_ordering = any(
        lba is not None for lba in (lizard_payload_lba, rat_payload_lba, wizard_payload_lba)
    )
    floor_aware = lower_payload_lba is not None or deferred_ordering
    code = {
        BOOT: (
            floor_loader(payload_lba, lower_payload_lba, lizard_payload_lba, rat_payload_lba, wizard_payload_lba,
                         expanded_level_six)
            if floor_aware else loader(payload_lba, walking, wide)
        ),
        SUPPRESS_NORMAL: gate(SUPPRESS_NORMAL, SUPPRESS_RAM, "v1", walking, floor_aware),
        SUPPRESS_DELAY: gate(SUPPRESS_DELAY, WALK_SUPPRESS_DELAY_RAM if walking else SUPPRESS_DELAY_RAM, "a0", walking, floor_aware),
        DRAW_GATE: gate(DRAW_GATE, DRAW_RAM, walking=walking, floor_aware=floor_aware),
    }
    if walking:
        code[MENU_GATE] = menu_gate()
        code[VRAM_UPLOAD_GATE] = vram_upload_gate(floor_aware)
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
            (0x8006f2c8, jump(0x8005b368, True), jump(MENU_GATE, True)),
            (0x800905d4, bytes.fromhex("e0ffbd271000b0af"), jump(VRAM_UPLOAD_GATE) + bytes(4)),
        )
    if deferred_ordering:
        stack_prologue = bytes.fromhex("b8febd27")
        save_actor = bytes.fromhex("e000a5af")
        hooks += ((0x8002a258, stack_prologue + save_actor, jump(ACTOR_GATE) + stack_prologue),)
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

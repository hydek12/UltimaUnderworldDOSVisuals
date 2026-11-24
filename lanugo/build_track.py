#!/usr/bin/env python3
"""Build the experimental Japanese Rev 1 Lanugo patch on a scratch data track."""

import argparse
import csv
import hashlib
import shutil
import struct
from pathlib import Path

from mipswords import Code, ret
import renderer

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
SUPPRESS_RAM = PAYLOAD_RAM + 0x100
SUPPRESS_DELAY_RAM = PAYLOAD_RAM + 0x160
WALK_SUPPRESS_DELAY_RAM = PAYLOAD_RAM + 0x180
WALK_READY_RAM = PAYLOAD_RAM + 8
DRAW_RAM = PAYLOAD_RAM + 0x200
UPLOAD_RAM = PAYLOAD_RAM + 0x700
WALK_UPLOAD_RAM = PAYLOAD_RAM + 0xa00
RESIDENT_BYTES = 0x1000
TEXTURE_STAGING_RAM = 0x801F8800
BAND_BYTES = 0x4000

def jump(address, link=False):
    return struct.pack("<I", ((3 if link else 2) << 26) | ((address >> 2) & 0x3ffffff))

def gate(origin, destination, fallback_register=None):
    c = Code(origin)
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

def loader(payload_lba=PAYLOAD_LBA, walking=False):
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
    c.jump(WALK_UPLOAD_RAM if walking else UPLOAD_RAM, True)
    c.nop()
    c.label("done")
    c.mem("lw", "ra", 28, "sp")
    c.nop()
    ret(c, lambda: c.imm("addiu", "sp", "sp", 32))
    return c.out()

def mark_idle_ready(c):
    c.address("t0", PAYLOAD_RAM)
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


def read_atlas(directory, name, height, first_slot, texture_page=0):
    data = (directory / f"lanugo-{name}.tim").read_bytes()
    image_size = 2 * 256 * height
    if len(data) != 20 + image_size or struct.unpack_from("<IIIHHHH", data) != (
        16, 2, 12 + image_size, 0, 0, 256, height
    ):
        raise ValueError(f"Expected the Xcode tool's 256×{height} 16-bit Lanugo {name} TIM.")
    texels = struct.unpack_from(f"<{256 * height}H", data, 20)
    colors = sorted(set(texels))
    if len(colors) != 16 or colors[0] != 0:
        raise ValueError(f"The Lanugo {name} atlas must contain 16 RGB555 entries including transparency.")
    indexed = {color: index for index, color in enumerate(colors)}
    image = bytes(indexed[left] | indexed[right] << 4 for left, right in zip(texels[::2], texels[1::2]))
    with (directory / f"lanugo-{name}.csv").open() as csv_file:
        rows = list(csv.DictReader(csv_file))
    if [(int(row["slot"]), int(row["phase"])) for row in rows] != [
        (slot, phase) for slot in range(first_slot, first_slot + 8) for phase in range(4)
    ]:
        raise ValueError(f"Expected four frames for each of the eight Lanugo {name} slots.")
    metadata = bytearray()
    for row in rows:
        u, v, w, h, hx, hy = (int(row[key]) for key in (
            "u", "v", "width", "height", "hotspot_x", "hotspot_y"
        ))
        if not (w > 0 and h > 0 and 0 <= u <= 256 - w and 0 <= v <= height - h):
            raise ValueError(f"Lanugo {name} frame lies outside its TIM.")
        if not (0 <= hx < 256 and 0 <= hy < 256):
            raise ValueError(f"Lanugo {name} hotspot is outside the supported byte range.")
        metadata += struct.pack("8B", u, v, w, h, hx, hy, texture_page, 0)
    return colors, image, bytes(metadata)


def payload(directory, walk_atlas=None):
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
        0x200: renderer.draw(DRAW_RAM, PAYLOAD_RAM + 0x800, PAYLOAD_RAM + 0x90, clut, walk_ready),
        0x800: metadata,
        0x1000: image,
    }
    if walking:
        sections[0x20] = struct.pack("<4H", 384, 384, 64, 64)
        sections[0x50] = struct.pack("<8H", 448, 256, 64, 128, 448, 384, 64, 96)
        sections[WALK_UPLOAD_RAM - PAYLOAD_RAM] = walking_uploader()
        sections[0x900] = walk_metadata
        sections[IDLE_PAYLOAD_BYTES] = struct.pack("<I", WALK_MAGIC)
        sections[IDLE_PAYLOAD_BYTES + WALK_HEADER_BYTES] = walk_image
    else:
        sections[UPLOAD_RAM - PAYLOAD_RAM] = uploader()
    size = IDLE_PAYLOAD_BYTES + (WALK_PAYLOAD_BYTES if walking else 0)
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

def edit_executable(original, payload_lba=PAYLOAD_LBA, walking=False):
    target = bytearray(original)
    code = {
        BOOT: loader(payload_lba, walking),
        SUPPRESS_NORMAL: gate(SUPPRESS_NORMAL, SUPPRESS_RAM, "v1"),
        SUPPRESS_DELAY: gate(SUPPRESS_DELAY, WALK_SUPPRESS_DELAY_RAM if walking else SUPPRESS_DELAY_RAM, "a0"),
        DRAW_GATE: gate(DRAW_GATE, DRAW_RAM),
    }
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

def build(source, atlas, output, walk_atlas=None):
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
        edited = edit_executable(exe, walking=walk_atlas is not None)
        disk_payload = payload(atlas, walk_atlas)
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
    args = parser.parse_args()
    build(args.japanese_track, args.atlas_directory, args.output_track, args.walk_atlas)

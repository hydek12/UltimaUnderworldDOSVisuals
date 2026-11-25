"""DOS distance shading with a fixed light level for renderer comparison."""

from struct import iter_unpack, pack, unpack

from mipswords import Code

TEXTURE_PAGES = ((384, 256, 224), (512, 384, 128))
CLUT_RECT = (384, 480, 128, 32)
SELECTOR_OFFSET = 0x500
LIGHT_LEVEL_OFFSET = 0x60
ROOM_LIGHT_LEVEL_OFFSET = 0x1a00
SETTINGS_DELTA = 4


def light_settings(dos_root):
    data = (dos_root / "DATA" / "SHADES.DAT").read_bytes()
    if len(data) != 96:
        raise ValueError("SHADES.DAT must contain eight 12-byte rows.")
    settings = bytearray()
    for level, (divisor, base, lowpass, *_) in enumerate(iter_unpack("<6h", data)):
        settings.extend(pack("<BBbB", max(1, divisor), base & 255, lowpass, 16 if level == 5 else 0))
    return bytes(settings)


def palette_banks(dos_root, fullbright_clut):
    page = (dos_root / "CRIT" / "CR00PAGE.N01").read_bytes()
    if len(page) < 3 or len(page) <= 2 + page[1]:
        raise ValueError("The DOS green goblin animation page is truncated.")
    slots = page[1]
    header = 3 + slots + 8 * page[2 + slots]
    if len(page) < header + 129 or page[header] != 4:
        raise ValueError("Expected four palettes in the DOS green goblin animation page.")
    vga = [page[header + 1 + p * 32:header + 1 + (p + 1) * 32] for p in range(4)]
    colors = (dos_root / "DATA" / "PALS.DAT").read_bytes()[:768]
    normal = (dos_root / "DATA" / "LIGHT.DAT").read_bytes()
    mono = (dos_root / "DATA" / "MONO.DAT").read_bytes()
    if len(colors) != 768 or any(len(table) != 4096 for table in (normal, mono)):
        raise ValueError("Expected the DOS VGA palette and two 16-row remap tables.")

    def rgb555(index):
        if index == 0:
            return 0
        r, g, b = ((channel * 255 // 63) >> 3 for channel in colors[index * 3:index * 3 + 3])
        return (r | (g << 5) | (b << 10)) or 0x8000

    original_indices = {}
    for indices in zip(*vga, strict=True):
        pattern = tuple(rgb555(index) for index in indices)
        if pattern in original_indices and original_indices[pattern] != indices:
            raise ValueError("The DOS VGA palettes require separate texture indices for shading.")
        original_indices[pattern] = indices
    patterns = tuple(zip(*(unpack("<32H", fullbright_clut[p:p + 64])
                           for p in range(0, len(fullbright_clut), 64)), strict=True))
    if any(pattern not in original_indices for pattern in patterns):
        raise ValueError("The atlas colors do not match the source VGA palette indices.")
    banks = bytearray()
    for table in (normal, mono):
        for row in range(16):
            for palette in range(4):
                shaded = []
                for pattern in patterns:
                    index = original_indices[pattern][palette]
                    remap = table[row * 256 + index]
                    shaded.append((rgb555(remap) or 0x8000) if index else 0)
                banks.extend(pack("<32H", *shaded))
    if bytes(banks[:len(fullbright_clut)]) != fullbright_clut:
        raise ValueError("The unshaded palette row must match the release atlas.")
    return bytes(banks)


def select_clut(origin, light_selector, continuation, clut):
    c = Code(origin)
    # Native horizontal deltas use the DOS world-unit scale. Use player height
    # before the PSX camera offset and the original creature anchor height.
    c.mem("lh", "t1", 0xe8, "sp")
    c.mem("lh", "t2", 0xf8, "sp")
    c.shift("sra", "t1", "t1", 5)
    c.muldiv("mult", "t1", "t1")
    c.shift("sra", "t2", "t2", 5)
    c.nop()
    c.mflo("t1")
    c.muldiv("mult", "t2", "t2")
    c.mem("lw", "t3", 0xe0, "sp")
    c.nop()
    c.mem("lhu", "t6", 2, "t3")
    c.address("t9", 0x801d9704)
    c.mem("lhu", "v0", 0, "t9")
    c.imm("andi", "t6", "t6", 127)
    c.shift("sll", "t6", "t6", 3)
    c.alu("subu", "t6", "t6", "v0")
    c.shift("sra", "t6", "t6", 5)
    c.mflo("t2")
    c.muldiv("mult", "t6", "t6")
    c.alu("addu", "t1", "t1", "t2")
    c.nop()
    c.mflo("t2")
    c.alu("addu", "t1", "t1", "t2")
    c.shift("sll", "t1", "t1", 16)
    c.shift("sra", "t1", "t1", 16)
    c.branch("blez", "t1", "zero", "scaled")
    c.alu("OR", "t2", "zero", "zero")
    c.imm("sltiu", "t6", "t1", 256)
    c.branch("beq", "t6", "zero", "seed")
    c.imm("ori", "t2", "zero", 64)
    c.imm("ori", "t2", "zero", 4)
    c.label("seed")
    # DOS uses five integer Newton steps for a positive signed 16-bit square.
    c.imm("ori", "t6", "zero", 5)
    c.label("sqrt")
    c.muldiv("divu", "t1", "t2")
    c.imm("addiu", "t6", "t6", -1)
    c.nop()
    c.mflo("t8")
    c.alu("addu", "t2", "t2", "t8")
    c.branch("bgtz", "t6", "zero", "sqrt")
    c.shift("srl", "t2", "t2", 1)
    c.label("scaled")
    # The resident light-level byte indexes four constants from SHADES.DAT.
    c.address("t8", light_selector)
    c.mem("lbu", "t6", 0, "t8")
    c.nop()
    c.imm("andi", "t6", "t6", 7)
    c.shift("sll", "t6", "t6", 2)
    c.alu("addu", "t8", "t8", "t6")
    c.mem("lbu", "t6", SETTINGS_DELTA, "t8")
    c.mem("lb", "t9", SETTINGS_DELTA + 2, "t8")
    c.muldiv("multu", "t2", "t6")
    c.mem("lbu", "v0", SETTINGS_DELTA + 1, "t8")
    c.mem("lbu", "v1", SETTINGS_DELTA + 3, "t8")
    c.mflo("t2")
    c.shift("srl", "t2", "t2", 6)
    c.alu("addu", "t2", "t2", "t9")
    c.branch("bgtz", "t2", "zero", "clamp")
    c.nop()
    c.alu("OR", "t2", "zero", "zero")
    c.label("clamp")
    c.alu("addu", "t2", "t2", "v0")
    c.imm("andi", "t2", "t2", 255)
    c.imm("sltiu", "v0", "t2", 15)
    c.branch("bne", "v0", "zero", "shade")
    c.nop()
    c.imm("ori", "t2", "zero", 14)
    c.label("shade")
    # The sixteen monochrome rows follow the sixteen ordinary rows in VRAM.
    c.alu("addu", "t2", "t2", "v1")
    c.shift("sll", "t2", "t2", 6)
    c.imm("addiu", "t2", "t2", clut)
    c.mem("lhu", "v0", 0, "t3")
    c.imm("ori", "v1", "zero", 70)
    c.imm("andi", "v0", "v0", 0x1ff)
    c.branch("beq", "v0", "v1", "packet")
    c.nop()
    c.imm("addiu", "v0", "v0", -75)
    c.shift("sll", "v0", "v0", 1)
    c.alu("addu", "t2", "t2", "v0")
    c.label("packet")
    c.shift("sll", "t6", "t2", 16)
    c.jump(continuation)
    c.nop()
    return c.out()

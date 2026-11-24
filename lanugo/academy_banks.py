"""Select a Level 6 secondary sprite page before building the next frame."""

import struct

from mipswords import Code

GATE = 0x800C23F0
GATE_BRANCH = 0x800C2430
GATE_DISPATCH = 0x800C2470
FRAME_HOOK = 0x800720A8
RESUME_FRAME_SETUP = GATE_BRANCH + 4
PAYLOAD = 0x801F6000
SELECTOR = PAYLOAD + 0x108
SWITCH = PAYLOAD + 0x188
POINTER = 0x60
GRID = 0x68
ACTIVE = 0xC08

# Bank 0 has the expanded creature roster. Assign the Academy's cells by
# distance to the original spawn points, with a bounded coverage radius.
LEVEL_SIX_BANKS = (
    ("wizb", ((106, 115),), ((15, 21), (39, 23), (21, 8))),
    ("wizc", ((107,),), ((43, 11), (21, 16))),
    ("warren", ((97,), (102,)), ((4, 5), (52, 54))),
    ("trolls", ((111, 112),), ((58, 42), (13, 57))),
    ("golem", ((119,),), ((6, 22),)),
    ("fire-elemental", ((120,),), ((55, 6),)),
)
ACADEMY_NPCS = tuple(
    (x, z, index)
    for index, (_, _, tiles) in enumerate(LEVEL_SIX_BANKS, 1)
    for x, z in tiles
)
BANK_FAMILIES = {name: families for name, families, _ in LEVEL_SIX_BANKS}


def room_grid():
    banks = []
    for z in range(4, 64, 8):
        for x in range(4, 64, 8):
            distance, bank = min((abs(x - px) + abs(z - pz), bank) for px, pz, bank in ACADEMY_NPCS)
            banks.append(bank if distance <= 9 else 0)
    for x, z, bank in ACADEMY_NPCS:
        # The gameplay camera is one tile west of the map's teleport coordinate.
        for camera_x in (x - 1, x):
            banks[(z // 8) * 8 + camera_x // 8] = bank
    return bytes(a | b << 4 for a, b in zip(banks[::2], banks[1::2], strict=True))


def gates():
    """Use the gaps between resident render stubs to dispatch to the Level 6 payload."""
    c = Code(GATE)
    c.imm("lui", "t8", "zero", PAYLOAD >> 16)
    c.mem("lw", "t9", (PAYLOAD & 0xffff) + POINTER, "t8")
    c.jump(GATE_BRANCH)
    c.nop()
    branch = Code(GATE_BRANCH)
    branch.branch("bne", "t9", "zero", "dispatch")
    # Replay the two displaced SDK frame-setup instructions on both paths.
    branch.mem("lhu", "v1", 0x4a0, "gp")
    branch.jump(FRAME_HOOK + 8)
    branch.imm("addiu", "sp", "sp", -24)
    branch.labels["dispatch"] = (GATE_DISPATCH - GATE_BRANCH) // 4
    dispatch = Code(GATE_DISPATCH)
    dispatch.add(0x03200008)  # jr t9, preserving the frame's return address
    dispatch.nop()
    return {GATE: c.out(), GATE_BRANCH: branch.out(), GATE_DISPATCH: dispatch.out()}


def sections(base_byte_offset, bank_bytes, bank):
    """Keep the switch routine below the part of RAM it will replace."""
    c = Code(SELECTOR)
    c.imm("ori", "t8", "t8", PAYLOAD & 0xffff)  # High half remains in t8 from the gate.
    c.mem("lw", "t7", 4, "t8")
    c.imm("lui", "t0", "zero", 0x801E)
    c.branch("beq", "t7", "zero", "native")
    c.mem("lhu", "t1", -0x6900, "t0")
    c.mem("lhu", "t2", -0x68FE, "t0")
    c.shift("srl", "t1", "t1", 11)
    c.shift("srl", "t2", "t2", 11)
    c.imm("andi", "t1", "t1", 7)
    c.imm("andi", "t2", "t2", 7)
    c.shift("sll", "t2", "t2", 3)
    c.alu("addu", "t1", "t1", "t2")
    c.shift("srl", "t2", "t1", 1)
    c.alu("addu", "t2", "t8", "t2")
    c.mem("lbu", "t2", GRID, "t2")
    c.imm("andi", "t1", "t1", 1)
    c.shift("sll", "t1", "t1", 2)
    c.add((9 << 21) | (10 << 16) | (10 << 11) | 6)  # srlv t2, t2, t1
    c.imm("andi", "t2", "t2", 15)
    c.mem("lw", "t3", ACTIVE, "t8")
    c.address("a0", base_byte_offset)
    c.branch("beq", "t2", "t3", "native")
    c.address("t0", bank_bytes)
    c.muldiv("multu", "t2", "t0")
    c.jump(SWITCH)
    c.nop()
    c.label("native")
    c.jump(RESUME_FRAME_SETUP)
    c.nop()

    switch = Code(SWITCH)
    switch.mflo("t1")
    switch.alu("addu", "a0", "a0", "t1")
    switch.imm("addiu", "sp", "sp", -32)
    switch.mem("sw", "ra", 28, "sp")
    switch.mem("sw", "a0", 24, "sp")
    switch.mem("sw", "zero", 4, "t8")
    switch.jump(0x800903AC, True)
    switch.alu("addu", "a0", "zero", "zero")
    # Keep the selector, ownership and return address below the disc read.
    switch.mem("lw", "a0", 24, "sp")
    switch.address("a1", PAYLOAD + 0x800)
    switch.imm("addiu", "a0", "a0", 0x800)
    switch.jump(0x8003F004, True)
    switch.imm("ori", "a2", "zero", 0x1800)
    switch.mem("lw", "a0", 24, "sp")
    switch.address("t8", PAYLOAD)
    switch.mem("sw", "a0", 12, "t8")
    switch.jump(PAYLOAD + 0xC00, True)
    switch.nop()
    switch.mem("lw", "ra", 28, "sp")
    switch.imm("addiu", "sp", "sp", 32)
    switch.jump(RESUME_FRAME_SETUP)
    switch.nop()
    return {
        POINTER: struct.pack("<I", SELECTOR), GRID: room_grid(),
        SELECTOR - PAYLOAD: c.out(), SWITCH - PAYLOAD: switch.out(),
        ACTIVE: struct.pack("<I", bank),
    }

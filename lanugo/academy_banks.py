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
GRID = 0xC80
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
    ("imps", ((75, 81),), ((60, 36), (37, 50), (36, 52))),
    ("skeletons", ((74,),), ((22, 57), (23, 58))),
    ("ghouls", ((105,),), ((41, 37), (44, 37))),
    ("headless", ((91,),), ((51, 48), (27, 53), (26, 55), (46, 60))),
)
ACADEMY_NPCS = tuple(
    (x, z, index)
    for index, (_, _, tiles) in enumerate(LEVEL_SIX_BANKS, 1)
    for x, z in tiles
)
COMBAT_ACTIONS = 0x1580
BANK_FAMILIES = {name: families for name, families, _ in LEVEL_SIX_BANKS}
LEVEL_ONE_BANKS = (
    ("gray-goblins", ((71, 80),), ((15, 35), (2, 57), (60, 51), (57, 55))),
    ("fighters", ((90,),), ((17, 7), (22, 19), (33, 20))),
)
LEVEL_ONE_FAMILIES = {name: families for name, families, _ in LEVEL_ONE_BANKS}
LEVEL_ONE_FORMATS = {"gray-goblins": (4, 16), "fighters": (8, 15)}
LEVEL_ONE_STRIDE = 0x19800
# (texture depth, sixteenths of original size, uses both pages)
SPECIAL_FORMATS = {"imps": (8, 16, True), "skeletons": (4, 16, True),
                   "ghouls": (8, 14, True), "headless": (8, 16, True)}


def room_grid(points=ACADEMY_NPCS, radius=9, *, x_step=4, z_step=4):
    banks = []
    for z in range(z_step // 2, 64, z_step):
        for x in range(x_step // 2, 64, x_step):
            distance, bank = min((abs(x - px) + abs(z - pz), bank) for px, pz, bank in points)
            banks.append(bank if distance <= radius else 0)
    for x, z, bank in points:
        # The gameplay camera is one tile west of the map's teleport coordinate.
        for camera_x in (x - 1, x):
            banks[(z // z_step) * (64 // x_step) + camera_x // x_step] = bank
    if x_step == 2:
        for x, z in ((4, 56), (45, 52), (45, 56)):
            for camera_x in (x - 1, x):
                banks[(z // z_step) * 32 + camera_x // 2] = 0
        banks[(58 // z_step) * 32 + 2 // x_step] = 1  # Vernix from the south, across the Lanugo cell.
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


def sections(base_byte_offset, bank_bytes, bank, *, level_one=False):
    """Keep the switch routine below the part of RAM it will replace."""
    c = Code(SELECTOR)
    c.imm("ori", "t8", "t8", PAYLOAD & 0xffff)  # High half remains in t8 from the gate.
    c.mem("lw", "t7", 4, "t8")
    c.imm("lui", "t0", "zero", 0x801E)
    c.branch("beq", "t7", "zero", "native")
    c.mem("lhu", "t1", -0x6900, "t0")
    c.mem("lhu", "t2", -0x68FE, "t0")
    grid_at = 0x1c00 if level_one else GRID
    c.shift("srl", "t1", "t1", 9 if level_one else 10)
    c.shift("srl", "t2", "t2", 9 if level_one else 10)
    c.imm("andi", "t1", "t1", 31 if level_one else 15)
    c.imm("andi", "t2", "t2", 31 if level_one else 15)
    c.shift("sll", "t2", "t2", 5 if level_one else 4)
    c.alu("addu", "t1", "t1", "t2")
    c.shift("srl", "t2", "t1", 1)
    c.alu("addu", "t2", "t8", "t2")
    c.mem("lbu", "t2", grid_at, "t2")
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
    if level_one:
        # The Level 1 banks use different draw routines. Each carries identical
        # selector and switch instructions, including the return point below.
        switch.mem("lw", "a0", 24, "sp")
        switch.address("a1", PAYLOAD)
        switch.jump(0x8003F004, True)
        switch.imm("ori", "a2", "zero", 0x2000)
    else:
        switch.mem("lw", "a0", 24, "sp")
        switch.address("a1", PAYLOAD + 0x800)
        switch.imm("addiu", "a0", "a0", 0x800)
        switch.jump(0x8003F004, True)
        switch.imm("ori", "a2", "zero", 0x1800)
    switch.mem("lw", "a0", 24, "sp")
    switch.address("t8", PAYLOAD)
    switch.mem("sw", "a0", 12, "t8")
    if level_one:
        switch.mem("lw", "t0", 0x998, "gp")
        switch.nop()
        switch.jump(PAYLOAD + 0xC00, True)
        switch.mem("sw", "t0", 0x58, "t8")
    else:
        switch.jump(PAYLOAD + 0xC00, True)
        switch.nop()
    switch.mem("lw", "ra", 28, "sp")
    switch.imm("addiu", "sp", "sp", 32)
    switch.jump(RESUME_FRAME_SETUP)
    switch.nop()
    points = tuple(
        (x, z, index)
        for index, (_, _, tiles) in enumerate(LEVEL_ONE_BANKS, 1)
        for x, z in tiles
    ) if level_one else ACADEMY_NPCS
    return {
        POINTER: struct.pack("<I", SELECTOR),
        grid_at: room_grid(points, 6 if level_one else 9, x_step=2 if level_one else 4, z_step=2 if level_one else 4),
        SELECTOR - PAYLOAD: c.out(), SWITCH - PAYLOAD: switch.out(),
        ACTIVE: struct.pack("<I", bank),
    }

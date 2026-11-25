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
LEVEL_ONE_FORMATS = {"gray-goblins": (4, 16), "fighters": (8, 15)}
LEVEL_TWO_BANKS = (
    ("dwarves", ((84, 86),), ((60, 3), (40, 5), (37, 7), (9, 8), (9, 14), (12, 28), (19, 36))),
    ("corby", ((98,),), ((28, 22),)),
)
LEVEL_THREE_BANKS = (
    ("bandits", ((93, 94),), ((40, 11), (29, 9), (36, 9), (33, 12), (20, 41))),
    ("prisoner", ((85, 88, 89), (106,)), ((25, 21), (27, 22))),
    ("zak", ((104,),), ((47, 38),)),
)
LEVEL_FOUR_BANKS = (
    ("town", ((90, 95, 98, 104), (93, 94)),
     ((5, 2), (8, 4), (5, 5), (14, 5), (13, 7), (22, 10), (13, 16), (3, 23), (13, 23), (12, 29))),
    ("fighters-four", ((90, 95, 98, 104),), ((40, 19), (20, 43), (32, 61))),
    ("trolls-four", ((96, 112),), ((58, 9), (58, 15), (49, 22))),
)
LEVEL_FIVE_BANKS = (
    ("judy", ((107,),), ((34, 8),)),
    ("ghouls-five", ((99,),), ((54, 20), (49, 22), (34, 23), (58, 26))),
    ("anjor", ((106,),), ((17, 36),)),
)
LEVEL_SEVEN_BANKS = (
    ("tyball", ((123,),), ((54, 10),)),
    ("cardon", ((104,),), ((19, 14),)),
    ("gray-guards-seven", ((80,),), ((27, 22), (27, 24), (29, 24), (30, 24))),
    ("prison-seven", ((108, 109), (86,), (90, 98, 104)),
     ((13, 47), (10, 51), (1, 52), (12, 53), (2, 55), (6, 55), (7, 57), (20, 58))),
    ("troll-seven", ((111,),), ((26, 56),)),
    ("imp-seven", ((75,),), ((35, 37),)),
)
LEVEL_EIGHT_BANKS = (
    ("carasso", ((72,), (104,)), ((47, 44),)),
)
ROOM_BANKS = {1: LEVEL_ONE_BANKS, 2: LEVEL_TWO_BANKS, 3: LEVEL_THREE_BANKS, 4: LEVEL_FOUR_BANKS,
              5: LEVEL_FIVE_BANKS, 7: LEVEL_SEVEN_BANKS, 8: LEVEL_EIGHT_BANKS, 9: ()}
# Additional banks for recurring encounters in the cumulative preview.
RECURRING_BANKS = {
    1: (
        ("grubs-slugs", ((64, 82), (65, 69)), ((58, 2), (55, 4), (5, 6), (59, 14), (26, 33), (37, 60))),
        ("bats-rats", ((66, 73), (67, 72)),
         ((45, 6), (50, 6), (22, 8), (18, 12), (2, 15), (12, 16), (2, 17), (2, 19), (2, 22),
          (31, 23), (23, 43), (24, 43))),
        ("spiders", ((68, 83, 92),), ((29, 26), (27, 46), (37, 54), (19, 54))),
        ("skeletons", ((74,),), ((54, 35),)),
        ("lurkers", ((87, 116),), ((14, 23), (26, 38), (51, 55))),
        ("entrance-imp", ((75,),), ((12, 20),)),
    ),
    2: (
        ("grubs-slugs", ((64, 82), (65, 69)),
         ((27, 11), (50, 21), (8, 34), (10, 34), (15, 34), (8, 36), (10, 36), (2, 37), (10, 38),
          (4, 44), (26, 58), (27, 58), (26, 59))),
        ("rats-spiders", ((67, 72), (68, 83, 92)),
         ((58, 14), (36, 22), (34, 38), (35, 38), (37, 44), (35, 54), (36, 55))),
        ("skeletons", ((74,),), ((22, 4), (51, 53), (59, 53))),
        ("lurkers", ((87, 116),), ((60, 26), (49, 54))),
        ("headless", ((91,),), ((28, 42), (21, 52))),
        ("gazers-golems", ((102,), (114, 121)), ((48, 23), (5, 23))),
        ("gray-goblins", ((71, 80),), ((56, 60),)),
    ),
    3: (
        ("grubs-slugs", ((64, 82), (65, 69)), ((47, 55), (51, 56), (53, 61))),
        ("bats-rats", ((66, 73), (67, 72)), ((21, 2), (21, 3), (23, 7), (1, 20), (2, 21), (40, 40))),
        ("spiders", ((68, 83, 92),), ((47, 4), (13, 23), (35, 39), (35, 40))),
        ("skeletons", ((74,),), ((10, 26), (12, 26), (49, 53))),
        ("lurkers", ((87, 116),), ((20, 7), (7, 17), (35, 17), (52, 22), (1, 26), (7, 34), (51, 37), (19, 49), (35, 51), (52, 50), (3, 52), (11, 52), (11, 59), (55, 61))),
        ("headless", ((91,),), ((43, 38),)),
        ("imps", ((81,),), ((29, 57),)),
        ("gazers-golems", ((102,), (114, 121)), ((24, 44), (12, 55))),
        ("ghosts-shadows", ((97, 113), (117,)), ((57, 8), (2, 55), (2, 56), (3, 56))),
        ("reapers", ((118,),), ((7, 55),)),
        ("south-green-goblin", ((78,),), ((35, 62),)),
        ("skeletons-spiders-headless", ((74,), (68, 83, 92), (91,)), ()),
    ),
    4: (
        ("grubs-slugs", ((64, 82), (65, 69)), ((26, 40), (36, 51))),
        ("bats-grubs-rats", ((66, 73), (82,), (67, 72)),
         ((36, 51), (33, 44), (32, 45), (18, 49), (36, 50), (31, 52), (12, 53), (20, 55))),
        ("spiders", ((68, 83, 92),), ((60, 22), (59, 24), (3, 44), (4, 44), (2, 45), (4, 45), (5, 45), (3, 46), (32, 48), (29, 58))),
        ("skeletons", ((74,),), ((38, 2), (61, 30), (59, 32), (60, 34))),
        ("lurkers", ((87, 116),), ((20, 23), (23, 33))),
        ("imps", ((81,),), ((32, 50), (28, 53), (35, 53))),
        ("headless", ((91,),), ((60, 38), (60, 39), (59, 41), (60, 41), (5, 59))),
        ("gazers-wisps", ((102,), (122,)), ((8, 47), (3, 50))),
        ("reapers", ((118,),), ((4, 40),)),
        ("wizards", ((106,),), ((8, 55), (8, 56))),
        ("grub-imp", ((82,), (81,)), ()),
    ),
    5: (
        ("rats-grubs-five", ((72,), (82,)),
         ((6, 34), (2, 36), (26, 37), (39, 37), (6, 40), (22, 40), (41, 43), (41, 47), (22, 49))),
        ("skeletons", ((74,),), ((47, 41), (53, 42), (49, 48), (45, 54), (38, 59), (46, 59), (39, 60), (47, 60))),
        ("imps-five", ((81,),), ((25, 44),)),
        ("headless", ((91,),), ((34, 39), (25, 40), (36, 41), (35, 44))),
        ("spiders", ((68, 83, 92),), ((36, 52), (27, 53), (35, 53), (37, 54), (29, 55), (36, 55), (26, 56))),
        ("ghosts-five", ((97, 100, 101, 113),), ((9, 2), (52, 3), (42, 3), (17, 8), (6, 11), (60, 13), (11, 14), (15, 18), (8, 36), (9, 36), (48, 36), (53, 49), (57, 49), (54, 53))),
        # The Gazer and the green goblins share the same two-tile camera cells.
        ("gazers-goblins", ((102,), (78,)), ((3, 42), (4, 42), (5, 42), (4, 43))),
        ("reapers", ((118,),), ((18, 44), (14, 46))),
        ("fire", ((120,),), ((19, 50),)),
    ),
    7: (
        ("bats-rats-seven", ((66,), (72,)),
         ((3, 8), (35, 20), (10, 22), (37, 22), (4, 23), (36, 24), (38, 26), (38, 30), (44, 61))),
        ("lurkers", ((87, 116),), ((7, 1), (9, 2), (2, 6), (4, 7), (2, 9), (15, 9), (6, 23), (23, 23))),
        ("spiders", ((68, 83, 92),), ((11, 39), (15, 40), (3, 41), (4, 43), (13, 43), (19, 45))),
        ("ghosts-shadows", ((97, 113), (117,)),
         ((36, 15), (16, 26), (19, 34), (19, 35), (33, 40), (50, 44), (40, 50), (51, 54))),
        ("gazers-golems", ((102,), (114, 121)), ((39, 2), (30, 10), (34, 36), (36, 38), (42, 57), (61, 57))),
        ("bats-lurkers", ((66,), (87, 116)), ((3, 8), (4, 23))),
        ("fire", ((120,),), ((47, 40), (51, 40), (42, 41), (56, 41), (38, 43), (60, 43), (35, 45), (33, 49), (34, 53), (35, 56), (35, 59), (32, 61))),
        ("reapers", ((118,),), ((27, 3), (33, 8))),
        ("golems-imp", ((114, 121), (75,)), ()),
    ),
    8: (
        ("rats-imps", ((72,), (81,)),
         ((15, 3), (49, 3), (7, 12), (36, 13), (7, 17), (13, 31), (50, 38), (31, 39), (7, 43), (39, 46),
          (1, 47), (25, 48), (39, 53), (59, 59), (51, 60), (8, 61), (30, 61))),
        ("rats-grubs-eight", ((72,), (82,)), ((54, 2), (35, 3), (10, 12), (7, 26), (3, 41), (30, 49), (35, 58))),
        ("rats-spiders", ((67, 72), (68, 83, 92)),
         ((2, 2), (7, 7), (12, 41), (58, 45), (23, 48), (34, 51), (2, 52), (60, 52), (50, 54), (8, 58),
          (14, 62))),
        ("headless", ((91,),), ((12, 3), (44, 7), (48, 7), (46, 8), (52, 13), (56, 26), (56, 27), (21, 40), (50, 48), (27, 49), (6, 60), (36, 60), (30, 62))),
        ("ghosts-eight", ((97, 113),), ((31, 1), (10, 3), (7, 20), (4, 24), (52, 25), (20, 40), (37, 45), (6, 51), (26, 58), (9, 60))),
        ("gazers-wisps-rats", ((102,), (122,), (72,)), ((25, 32), (39, 32), (39, 36), (56, 55))),
        ("ghouls-eight", ((110,),), ((49, 36),)),
        ("troll-seven", ((111,),), ((60, 49), (31, 54))),
        ("reapers", ((118,),), ((31, 3), (52, 18), (46, 29), (8, 40), (28, 47), (58, 47), (15, 57))),
        ("golems-wisps", ((114, 119, 121), (122,)),
         ((39, 2), (4, 14), (10, 20), (37, 28), (38, 32), (53, 32), (55, 47), (61, 47))),
        ("fire", ((120,),), ((22, 5), (54, 7), (23, 15), (41, 22), (31, 27), (33, 27), (9, 30), (4, 36), (53, 37), (33, 38), (41, 51))),
        ("demon", ((124,),), ((32, 33),)),
        ("imps-ghosts", ((81,), (97, 113)), ((8, 61),)),
        ("ghosts-rat-headless", ((97, 113), (72,), (91,)), ()),
    ),
}

# Override the nearest-spawn grid around these encounters.
# Keys name the bank that owns the two-tile cells, with None selecting bank zero.
ROOM_CELL_OVERRIDES = {
    1: {"spiders": ((13, 7), (14, 7))},
    2: {
        "headless": ((9, 44),),
        "rats-spiders": ((43, 48),),
        None: ((31, 57), (32, 57), (31, 58)),
    },
    3: {
        "bats-rats": ((31, 3), (32, 3), (42, 42)),
        "skeletons": ((1, 8),),
        "bandits": ((3, 9),),
        "spiders": ((57, 12), (58, 12), (17, 34), (18, 34), (44, 38)),
        "skeletons-spiders-headless": ((43, 38), (49, 52)),
        "lurkers": ((3, 59),),
        "headless": ((43, 55), (44, 55), (45, 62)),
    },
    4: {
        "bats-grubs-rats": ((35, 15), (27, 51), (29, 54), (33, 55)),
        "grub-imp": ((29, 52),),
    },
    7: {"imp-seven": ((33, 35), (34, 35)), "golems-imp": ((32, 36), (34, 37))},
    8: {
        # Keep the ghosts in these approach cells and add the adjacent rats and headless.
        "ghosts-rat-headless": ((21, 40), (27, 49), (11, 3), (5, 22), (25, 61)),
        "rats-spiders": ((14, 58),),
    },
}

RECURRING_FORMATS = {
    "grubs-slugs": (4, (16, 16)),
    "rats-grubs-five": (4, (16, 16)),
    "rats-grubs-eight": (4, (16, 16)),
    "bats-rats-seven": (4, (16, 16)),
    "rats-imps": (8, (16, 16)),
    "bats-lurkers": (8, (16, 16)),
    "golems-wisps": (4, (16, 16)),
    "imps-ghosts": (8, (16, 16)),
    "bats-rats": (4, (16, 16)),
    "rats-spiders": (4, (16, 16)),
    "gazers-golems": (4, (16, 16)),
    "ghosts-shadows": (4, (16, 16)),
    "gazers-wisps": (4, (16, 16)),
}
RECURRING_SINGLE_FORMATS = {
    "spiders": (4, 16), "skeletons": (4, 16), "lurkers": (8, 16),
    "headless": (8, 16), "imps": (8, 16), "reapers": (4, 16), "wizards": (4, 16),
    "imps-five": (8, 16), "ghosts-five": (4, 16), "fire": (4, 16),
    "entrance-imp": (8, 16), "south-green-goblin": (8, 13),
    "ghosts-eight": (4, 16), "ghouls-eight": (8, 14), "golems-eight": (4, 16),
    "ghouls-five-recurring": (8, 14), "demon": (8, 16),
}


def room_banks(floor, recurring=False):
    banks = ROOM_BANKS[floor]
    if recurring and floor == 1:
        banks = (
            ("gray-goblins", ((71, 80),), (*banks[0][2], (4, 47), (52, 59))),
            ("fighters", ((90,),), (*banks[1][2], (33, 12), (33, 15))),
        )
    if recurring and floor == 2:
        dwarves, corby = banks
        banks = ((dwarves[0], dwarves[1], (*dwarves[2], (12, 6), (14, 6), (18, 6),
                 (12, 10), (14, 10), (18, 10), (29, 17), (20, 23))), corby)
    if recurring and floor == 5:
        judy, ghouls, anjor = banks
        banks = (judy, ("ghouls-five-recurring", ((99, 110),), (*ghouls[2], *((43, 9), (52, 9), (43, 17)))), anjor)
    if recurring and floor == 7:
        troll = banks[4]
        troll_spawns = (*troll[2], (24, 2), (23, 3), (20, 5), (6, 29),
                        (4, 31), (3, 33), (7, 34), (25, 57), (52, 59))
        banks = (*banks[:4], ("troll-seven-recurring", ((111, 112),), troll_spawns), *banks[5:])
    if recurring and floor == 4:
        troll_spawns = (*banks[2][2], (54, 9), (53, 14), (47, 23), (43, 33), (47, 38))
        banks = (*banks[:2], ("trolls-four-recurring", ((96, 111, 112),), troll_spawns))
    return banks + (RECURRING_BANKS.get(floor, ()) if recurring else ())


ROOM_FAMILIES = {name: families for banks in (*ROOM_BANKS.values(), *RECURRING_BANKS.values())
                 for name, families, _ in banks}
ROOM_FAMILIES.update({
    "trolls-four-recurring": ((96, 111, 112),),
    "troll-seven-recurring": ((111, 112),),
    "ghouls-five-recurring": ((99, 110),),
    "hazards-nine": ((124,), (126,), (79,), (125,)),
})
# Each entry gives one texture page's bit depth and scales for its families.
SHARED_PAGE_FORMATS = {
    "prison-seven": ((4, (16,)), (8, (9, 8))),
    "bats-grubs-rats": ((4, (16, 16)), (4, (16,))),
    "hazards-nine": ((8, (10, 10)), (8, (10, 10))),
    "gazers-wisps-rats": ((4, (16, 16)), (4, (16,))),
    "gazers-goblins": ((4, (16,)), (8, (9,))),
    "skeletons-spiders-headless": ((4, (12, 12)), (8, (13,))),
    "grub-imp": ((4, (16,)), (8, (16,))),
    "golems-imp": ((4, (16,)), (8, (16,))),
    "ghosts-rat-headless": ((4, (16, 16)), (8, (13,))),
}
ROOM_FORMATS = {**LEVEL_ONE_FORMATS, "dwarves": (8, 16), "corby": (8, 15),
                "bandits": (8, 15), "zak": (8, 15), "fighters-four": (8, 15), "trolls-four": (4, 16), "trolls-four-recurring": (4, 16),
                "judy": (4, 16), "ghouls-five": (8, 14), "anjor": (4, 16),
                "tyball": (4, 16), "cardon": (8, 15), "gray-guards-seven": (4, 16),
                "troll-seven": (4, 16), "troll-seven-recurring": (4, 16), "imp-seven": (8, 16), **RECURRING_SINGLE_FORMATS}
SPLIT_ROOM_FORMATS = {"prisoner": (4, (12, 16)), "town": (8, (11, 11)), "carasso": (8, (16, 11)),
                      **RECURRING_FORMATS}
MIXED_COMBAT_BANKS = (SHARED_PAGE_FORMATS.keys() | SPLIT_ROOM_FORMATS.keys()) - {"hazards-nine"}
DEDICATED_ROOM_COMBAT_BANKS = frozenset((
    "wizards", "judy", "anjor", "tyball", "ghouls-five", "ghouls-five-recurring", "ghouls-eight",
))
ACADEMY_COMBAT_BANKS = frozenset(("wizb", "wizc", "warren", "ghouls"))

ROOM_STRIDE = 0x19800
# (texture depth, sixteenths of original size, uses both pages)
SPECIAL_FORMATS = {"imps": (8, 16, True), "skeletons": (4, 16, True),
                   "ghouls": (8, 14, True), "headless": (8, 16, True)}

# Single-family banks can use the resident fixed-pose table at full scale.
ROOM_COMBAT_BANKS = frozenset((
    "entrance-imp", "imps", "imps-five", "imp-seven", "skeletons", "headless",
))


def room_grid(points=ACADEMY_NPCS, radius=9, *, x_step=4, z_step=4, level_one=True):
    banks = []
    for z in range(z_step // 2, 64, z_step):
        for x in range(x_step // 2, 64, x_step):
            distance, bank = min((abs(x - px) + abs(z - pz), bank) for px, pz, bank in points)
            banks.append(bank if distance <= radius else 0)
    for x, z, bank in points:
        # The gameplay camera is one tile west of the map's teleport coordinate.
        for camera_x in (x - 1, x):
            banks[(z // z_step) * (64 // x_step) + camera_x // x_step] = bank
    if x_step == 2 and level_one:
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


def sections(base_byte_offset, bank_bytes, bank, *, floor=None, recurring=False, full_resident=False):
    """Build the selector and switch shared by every bank on this floor."""
    c = Code(SELECTOR)
    c.imm("ori", "t8", "t8", PAYLOAD & 0xffff)  # High half remains in t8 from the gate.
    c.mem("lw", "t7", 4, "t8")
    c.imm("lui", "t0", "zero", 0x801E)
    c.branch("beq", "t7", "zero", "native")
    c.mem("lhu", "t1", -0x6900, "t0")
    c.mem("lhu", "t2", -0x68FE, "t0")
    has_rooms = floor is not None
    load_full_bank = has_rooms or full_resident
    grid_at = 0x1c00 if has_rooms else GRID
    c.shift("srl", "t1", "t1", 9 if has_rooms else 10)
    c.shift("srl", "t2", "t2", 9 if has_rooms else 10)
    c.imm("andi", "t1", "t1", 31 if has_rooms else 15)
    c.imm("andi", "t2", "t2", 31 if has_rooms else 15)
    c.shift("sll", "t2", "t2", 5 if has_rooms else 4)
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
    # A full read replaces the renderer and preserves the shared return code.
    if load_full_bank:
        # These banks use different draw routines. Each carries identical
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
    if load_full_bank:
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
        for index, (_, _, tiles) in enumerate(room_banks(floor, recurring), 1)
        for x, z in tiles
    ) if has_rooms else ACADEMY_NPCS
    grid = (room_grid(points, 6 if has_rooms else 9, x_step=2 if has_rooms else 4,
                      z_step=2 if has_rooms else 4, level_one=floor == 1) if points else bytes(512))
    if recurring and not has_rooms:
        # Keep the stock Academy atlas at the actual common-creature and trap cells.
        grid = bytearray(grid)
        for x, z, owner in (
            (42, 43, 0), (43, 45, 0), (45, 45, 0), (4, 53, 0), (47, 56, 0),
            (35, 50, 0), (35, 53, 0), (40, 48, 0), (40, 50, 0), (40, 52, 0),
            (17, 53, 0), (18, 53, 0), (16, 54, 0), (18, 56, 0), (16, 55, 0),
            (43, 59, 0), (41, 61, 0), (15, 55, 0), (35, 56, 3), (8, 57, 4), (57, 56, 6),
        ):
            index = z // 4 * 16 + x // 4
            shift = 4 * (index & 1)
            grid[index // 2] = (grid[index // 2] & ~(15 << shift)) | owner << shift
        grid = bytes(grid)
    if floor == 7 or recurring and floor in (1, 2, 3, 4, 8):
        fallback_cells = {
            1: ((8, 43), (10, 43), (36, 28), (3, 38), (11, 38), (54, 38),
                (45, 52), (52, 52), (46, 55), (45, 56), (47, 56), (51, 58)),
            2: ((54, 55), (60, 55), (55, 60), (55, 61)),
            3: ((29, 21), (23, 28), (29, 28), (33, 28), (36, 31), (38, 31), (11, 33),
                (41, 23), (34, 24), (57, 24), (41, 29), (44, 29), (37, 32),
                (11, 7), (17, 7), (10, 10)),
            4: ((31, 44),),
            7: ((28, 57), (27, 55), (25, 55)),
            8: ((18, 12), (55, 12), (3, 13), (45, 23), (44, 34), (6, 38),
                (9, 51), (5, 58)),
        }
        grid = bytearray(grid)
        cells = fallback_cells[floor]
        if recurring and floor == 7:
            cells += ((21, 2), (22, 5), (19, 7), (20, 7), (18, 8),
                      (5, 29), (9, 28), (11, 28), (8, 30), (2, 34), (3, 35))
        for x, z in cells:
            index = z // 2 * 32 + x // 2
            grid[index // 2] &= ~(15 << (4 * (index & 1)))
        if floor == 8:
            index = 60 // 2 * 32 + 6 // 2
            shift = 4 * (index & 1)
            headless = next(i for i, (name, _, _) in enumerate(room_banks(8, True), 1) if name == "headless")
            grid[index // 2] = (grid[index // 2] & ~(15 << shift)) | headless << shift
        grid = bytes(grid)
    if recurring and floor in ROOM_CELL_OVERRIDES:
        grid = bytearray(grid)
        bank_ids = {name: index for index, (name, _, _) in enumerate(room_banks(floor, True), 1)}
        bank_ids[None] = 0
        for name, tiles in ROOM_CELL_OVERRIDES[floor].items():
            for x, z in tiles:
                index = z // 2 * 32 + x // 2
                shift = 4 * (index & 1)
                grid[index // 2] = (grid[index // 2] & ~(15 << shift)) | bank_ids[name] << shift
        grid = bytes(grid)
    return {
        POINTER: struct.pack("<I", SELECTOR),
        grid_at: grid,
        SELECTOR - PAYLOAD: c.out(), SWITCH - PAYLOAD: switch.out(),
        ACTIVE: struct.pack("<I", bank),
    }

if __name__ == "__main__":
    from creature_atlas import LEVEL_SIX_WIZARD_TYPES

    families = [ROOM_FAMILIES[bank] for bank in MIXED_COMBAT_BANKS | DEDICATED_ROOM_COMBAT_BANKS]
    families += [BANK_FAMILIES[bank] for bank in ACADEMY_COMBAT_BANKS]
    actors = {actor for bank in families for family in bank for actor in family}
    print("\n".join(map(str, sorted(actors.union(LEVEL_SIX_WIZARD_TYPES)))))

"""Emit the Japanese Rev 1 Lanugo rendering hooks."""

from mipswords import Code

IDLE_ACTION = 0x20
WALK_ACTION = 0x2c
GREEN_GOBLIN_TYPE = 70
LOWER_GOBLIN_TYPE = 78
GOBLIN_PALETTE_TYPES = (70, 76, 3)
ORDER_LOG_ENTRIES = 128


def require_palette_type(c, actor, scratch, fallback, palette_types, extra_type=None):
    base, first_variant, variant_count = palette_types
    if extra_type is not None:
        c.imm("ori", scratch, "zero", extra_type)
        c.branch("beq", actor, scratch, "palette_type")
        c.nop()
    c.imm("addiu", scratch, actor, -first_variant)
    c.imm("sltiu", scratch, scratch, variant_count)
    c.branch("bne", scratch, "zero", "palette_type")
    c.imm("ori", scratch, "zero", base)
    c.branch("bne", actor, scratch, fallback)
    c.nop()
    c.label("palette_type")


def registry_entry(c, actor, entry, scratch, registry):
    c.imm("addiu", entry, actor, -64)
    c.shift("sll", entry, entry, 2)
    c.address(scratch, registry)
    c.alu("addu", entry, entry, scratch)
    c.mem("lw", entry, 0, entry)
    c.nop()


def require_registered_action(c, actor, action, entry, scratch, registry, fallback):
    c.imm("addiu", scratch, actor, -64)
    c.imm("sltiu", scratch, scratch, 64)
    c.branch("beq", scratch, "zero", fallback)
    c.nop()
    registry_entry(c, actor, entry, scratch, registry)
    c.branch("beq", entry, "zero", fallback)
    c.imm("andi", scratch, entry, 0xffff)
    # Wizard entries have no directional-table override and support fixed poses.
    c.branch("beq", scratch, "zero", "registry_action")
    c.imm("ori", scratch, "zero", IDLE_ACTION)
    c.branch("beq", action, scratch, "registry_action")
    c.imm("ori", scratch, "zero", WALK_ACTION)
    c.branch("bne", action, scratch, fallback)
    c.nop()
    c.label("registry_action")


def require_fixed_pose_family(c, actor, action, scratch, extra_type, fallback, wizard_combat):
    # The second texture page has directional sprites but no fixed casting frames.
    c.imm("ori", scratch, "zero", extra_type)
    c.branch("bne", actor, scratch, "casting_family")
    if wizard_combat:
        c.nop()
        c.imm("sltiu", scratch, action, IDLE_ACTION)
        c.branch("bne", scratch, "zero", fallback)
    else:
        c.imm("ori", scratch, "zero", 0x0d)
        c.branch("beq", action, scratch, fallback)
    c.nop()
    c.label("casting_family")


def require_atlas_action(c, action, scratch, walk_ready, fallback):
    # The caller masked the native action and XORed it with IDLE_ACTION.
    c.branch("beq", action, "zero", "atlas_action")
    c.imm("xori", scratch, action, WALK_ACTION ^ IDLE_ACTION)
    c.branch("bne", scratch, "zero", fallback)
    c.nop()
    c.address(scratch, walk_ready)
    c.mem("lw", scratch, 0, scratch)
    c.nop()
    c.branch("beq", scratch, "zero", fallback)
    c.nop()
    c.label("atlas_action")


def atlas_action_index(c, table, action, result, scratch, fallback):
    c.address(result, table)
    c.alu("addu", result, result, action)
    c.mem("lbu", result, 0, result)
    c.imm("ori", scratch, "zero", 255)
    c.branch("beq", result, scratch, fallback)
    c.nop()


# Keep actor projection and hit testing when substituting a sprite.
def suppress(origin, order_table_register="v1", walk_ready=None, wide=False, lower_floor=False,
             palette_types=GOBLIN_PALETTE_TYPES, order_writer=None, action_map=None, extra_type=None, wizard_combat=False, registry=None):
    c=Code(origin)
    c.mem("lw","t8",0x74,"sp")
    c.address("t9",0x8002a5d8)
    c.branch("bne","t8","t9","normal")
    c.mem("lw","t8",0x158,"sp")
    c.nop()
    c.mem("lbu","t9",23,"t8")
    if walk_ready is None:
        c.mem("lbu","t8",26,"t8")
    else:
        c.mem("lhu","t8",0,"t8")
    c.imm("andi","t9","t9",0x3f)
    if action_map is None:
        c.imm("xori","t9","t9",IDLE_ACTION)
    if walk_ready is None:
        c.branch("bne","t9","zero","normal")
        c.imm("ori","t9","zero",10)
        c.nop()
        c.branch("bne","t8","t9","normal")
        c.nop()
    else:
        c.imm("andi", "t8", "t8", 0x1ff)
        if registry is not None:
            require_registered_action(c, "t8", "t9", "t8", "t7", registry, "normal")
        elif wide:
            require_palette_type(c, "t8", "t7", "normal", palette_types, extra_type)
        else:
            c.imm("xori", "t8", "t8", LOWER_GOBLIN_TYPE if lower_floor else GREEN_GOBLIN_TYPE)
            c.branch("bne", "t8", "zero", "normal")
            c.nop()
        if action_map is None:
            require_atlas_action(c, "t9", "t8", walk_ready, "normal")
        else:
            if extra_type is not None:
                require_fixed_pose_family(c, "t8", "t9", "t7", extra_type, "normal", wizard_combat)
            atlas_action_index(c, action_map, "t9", "t8", "t7", "normal")
    c.mem("sh","s3",0x18c,"sp")
    if order_writer is None:
        c.jump(0x8002b684)
        c.nop()
    else:
        c.jump(order_writer)
        c.alu("addu", "t8", order_table_register, "zero")
    c.label("normal")
    c.jump(0x8002b684)
    c.mem("sw","v0",0,order_table_register)
    return c.out()

# Idle view order measured in the DOS renderer's 32-sector direction table.
DOS_IDLE_DIRECTIONS = bytes((
    0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4,
    4, 4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 0, 0,
))


def draw(origin, metadata, direction_table, clut=0x401c, walk_ready=None, wide=False,
         shade_selector=None, overlay_offset=None, palette_types=GOBLIN_PALETTE_TYPES,
         order_log=None, combat=None, extra_atlas=None, wizard_combat=False, registry=None):
    c=Code(origin)
    shade_return = None
    extra_type = extra_atlas[0] if extra_atlas else None
    c.mem("lw","t0",0xe0,"sp")
    actor_type = 10 if walk_ready is None else GREEN_GOBLIN_TYPE
    if overlay_offset is not None:
        actor_type = LOWER_GOBLIN_TYPE
    c.imm("ori", "t1", "zero", actor_type)
    if walk_ready is None:
        c.mem("lbu","t2",26,"t0")
        c.nop()
    else:
        c.mem("lhu", "t2", 0, "t0")
        c.nop()
        c.imm("andi", "t2", "t2", 0x1ff)
    if registry is not None and combat is None:
        raise ValueError("The creature registry requires the action table.")
    if registry is None and wide and overlay_offset is None:
        require_palette_type(c, "t2", "t1", "finish", palette_types, extra_type)
    elif registry is None:
        c.branch("bne","t2","t1","finish")
    c.mem("lbu","t4",23,"t0")
    c.mem("lhu","t6",12,"t0")
    c.imm("andi","t4","t4",0x3f)
    if combat is None:
        c.imm("xori","t4","t4",IDLE_ACTION)
        if walk_ready is None:
            c.branch("bne","t4","zero","finish")
        else:
            require_atlas_action(c, "t4", "t7", walk_ready, "finish")
            c.alu("sltu", "t7", "zero", "t4")
            c.shift("sll", "t7", "t7", 9 if wide else 8)  # Walking metadata follows the idle table.
        # Group the seven native animation frames into four DOS phases.
        c.shift("srl","t6","t6",13)
        c.imm("andi","t6","t6",3)
    else:
        if registry is not None:
            require_registered_action(c, "t2", "t4", "t5", "t3", registry, "finish")
        elif extra_type is not None:
            require_fixed_pose_family(c, "t2", "t4", "t3", extra_type, "finish", wizard_combat)
        atlas_action_index(c, combat[0], "t4", "t7", "t3", "finish")
        c.shift("srl", "t6", "t6", 12)
    c.alu("subu","t1","a3","a1")
    c.branch("blez","t1","zero","finish")
    c.nop()
    c.imm("sltiu","t2","t1",256 if order_log is None else 512)
    c.branch("beq","t2","zero","finish")
    c.nop()
    if order_log is not None:
        rewind_native_order(c, *order_log)
    # DOS chooses the view from actor facing and camera yaw.
    c.mem("lhu", "t5", 2, "t0")
    c.imm("lui", "t4", "zero", 0x801d)
    c.mem("lhu", "t4", 0x53d4, "t4")
    c.imm("andi", "t5", "t5", 0x380)
    c.shift("srl", "t5", "t5", 5)  # Actor heading in 32nds of a turn.
    c.shift("srl", "t4", "t4", 11)
    c.alu("subu", "t2", "t5", "t4")
    c.imm("andi", "t2", "t2", 31)
    c.address("t0", direction_table)
    c.alu("addu", "t0", "t0", "t2")
    c.mem("lbu", "t2", 0, "t0")
    c.address("t0", metadata)
    if registry is not None:
        c.mem("lw", "t3", 0xe0, "sp")
        c.nop()
        c.mem("lhu", "t3", 0, "t3")
        c.nop()
        c.imm("andi", "t3", "t3", 0x1ff)
        registry_entry(c, "t3", "t5", "t4", registry)
        c.imm("andi", "t3", "t5", 0xffff)
        c.alu("addu", "t0", "t0", "t3")
    elif extra_atlas:
        c.mem("lw", "t3", 0xe0, "sp")
        c.imm("ori", "t4", "zero", extra_type)
        c.mem("lhu", "t3", 0, "t3")
        c.nop()
        c.imm("andi", "t3", "t3", 0x1ff)
        c.branch("bne", "t3", "t4", "atlas_selected")
        c.nop()
        c.address("t0", extra_atlas[1])
        c.label("atlas_selected")
    if combat is not None:
        select_combat_pose(c, *combat[1:], compact_base=metadata if registry is not None else None)
    else:
        c.shift("sll", "t2", "t2", 2)
        c.alu("addu", "t2", "t2", "t6")
        c.shift("sll", "t2", "t2", 4 if wide else 3)
        c.alu("addu", "t0", "t0", "t2")
        if walk_ready is not None:
            c.alu("addu", "t0", "t0", "t7")

    # Pass the original projected foot/center through the DOS hotspot.
    dimensions = 0 if wide else 2
    c.mem("lbu","t2",dimensions,"t0") # width
    c.mem("lbu","t3",dimensions + 1,"t0") # height
    c.mem("lbu","t4",dimensions + 2,"t0") # hotspot x
    c.mem("lbu","t5",dimensions + 3,"t0") # hotspot y
    c.muldiv("multu","t1","t4")
    c.nop()
    c.mflo("t4")
    c.muldiv("divu","t4","t3")
    c.alu("addu","t8","a0","a2")
    c.shift("sra","t8","t8",1)
    c.mflo("t4")
    c.alu("subu","t8","t8","t4") # left
    c.muldiv("multu","t1","t5")
    c.nop()
    c.mflo("t5")
    c.muldiv("divu","t5","t3")
    c.nop()
    c.mflo("t5")
    c.alu("subu","t9","a3","t5") # top
    c.muldiv("multu","t1","t2")
    c.nop()
    c.mflo("t2")
    c.muldiv("divu","t2","t3")
    if wide:
        c.mem("lhu", "t4", 4, "t0")
        c.mem("lhu", "t5", 6, "t0")
    else:
        c.mem("lhu","t4",0,"t0") # packed base uv
        c.mem("lbu","t5",2,"t0")
    c.mflo("t2")
    c.alu("addu","t2","t8","t2") # right
    c.alu("addu","t3","t9","t1") # bottom

    c.imm("lui","t6","zero",0x800d)
    c.mem("lw","t7",-0x6188,"t6") # packet alloc
    if overlay_offset is None:
        c.mem("lw","v0",-0x6168,"t6") # packet end
        c.imm("addiu","v1","t7",0x28)
    else:
        c.mem("lbu", "v0", overlay_offset + 12, "t0")
        c.imm("addiu", "v1", "t7", 0x28)
        c.branch("beq", "v0", "zero", "check_space")
        c.nop()
        c.imm("addiu", "v1", "v1", 0x28)
        c.label("check_space")
        c.mem("lw", "v0", -0x6168, "t6")
        c.nop()
    c.alu("sltu","v0","v0","v1")
    c.branch("bne","v0","zero","finish")
    c.nop()
    c.mem("sw","v1",-0x6188,"t6")
    c.mem("lw","v0",-0x6138,"t6")
    c.mem("lhu","v1",0x114,"sp")
    c.mem("lw","v0",0x70,"v0")
    c.shift("sll","v1","v1",2)
    c.imm("addiu","v0","v0",0x400)
    c.alu("addu","v0","v0","v1")
    c.mem("lw","v1",0,"v0")
    c.address("t6",0x00ffffff)
    c.alu("AND","v1","v1","t6")
    c.alu("AND","t6","t7","t6")
    c.imm("lui","t1","zero",0x0900)
    c.alu("OR","v1","v1","t1")
    c.mem("sw","v1",0,"t7")
    c.mem("sw","t6",0,"v0")
    # Opaque raw-texture quad preserves the RGB555 palette entries.
    c.imm("lui","v1","zero",0x2d00)
    c.mem("sw","v1",4,"t7")
    c.imm("andi","t8","t8",0xffff)
    c.imm("andi","t2","t2",0xffff)
    c.shift("sll","t9","t9",16)
    c.shift("sll","t3","t3",16)
    c.alu("OR","v1","t8","t9")
    c.mem("sw","v1",8,"t7")
    c.alu("OR","v1","t2","t9")
    c.mem("sw","v1",16,"t7")
    c.alu("OR","v1","t8","t3")
    c.mem("sw","v1",24,"t7")
    c.alu("OR","v1","t2","t3")
    c.mem("sw","v1",32,"t7")
    if overlay_offset is not None:
        layered_quad(c, overlay_offset)
    elif wide:
        # The 8-bit layout stores four UV corners so rotated frames render upright.
        if registry is not None:
            c.mem("lw", "v1", 0xe0, "sp")
            c.nop()
            c.mem("lhu", "v1", 0, "v1")
            c.nop()
            c.imm("andi", "v1", "v1", 0x1ff)
            registry_entry(c, "v1", "t6", "v1", registry)
            c.imm("lui", "v1", "zero", 0xffff)
            c.alu("AND", "t6", "t6", "v1")
        elif shade_selector is None:
            c.mem("lw", "v1", 0xe0, "sp")
            c.nop()
            c.mem("lhu", "v1", 0, "v1")
            c.imm("ori", "t6", "zero", palette_types[0])
            c.imm("andi", "v1", "v1", 0x1ff)
            c.branch("beq", "v1", "t6", "base_clut")
            c.imm("lui", "t6", "zero", clut)
            if extra_atlas:
                c.imm("ori", "t3", "zero", extra_type)
                c.branch("bne", "v1", "t3", "normal_clut")
                c.nop()
                c.branch("beq", "zero", "zero", "base_clut")
                c.imm("lui", "t6", "zero", extra_atlas[2])
                c.label("normal_clut")
            c.imm("addiu", "v1", "v1", 1 - palette_types[1])
            c.shift("sll", "v1", "v1", 22)  # Select the CLUT row above the first.
            c.alu("addu", "t6", "t6", "v1")
            c.label("base_clut")
        else:
            c.jump(shade_selector)
            c.nop()
            shade_return = origin + 4 * len(c.words)
        c.alu("OR", "v1", "t6", "t4")
        c.mem("sw", "v1", 12, "t7")
        c.mem("lbu", "v1", 12, "t0")
        c.mem("lhu", "t4", 8, "t0")
        c.shift("sll", "v1", "v1", 16)
        c.alu("OR", "v1", "v1", "t5")
        c.mem("sw", "v1", 20, "t7")
        c.mem("lhu", "t5", 10, "t0")
        c.mem("sw", "t4", 28, "t7")
        c.mem("sw", "t5", 36, "t7")
    else:
        c.imm("lui","v1","zero",clut)
        c.alu("OR","v1","v1","t4")
        c.mem("sw","v1",12,"t7")
        c.imm("addiu","t5","t5",-1)
        c.alu("addu","t5","t4","t5")
        if walk_ready is None:
            c.imm("lui","v1","zero",0x16)
        else:
            c.mem("lbu", "v1", 6, "t0")
            c.nop()
            c.shift("sll", "v1", "v1", 16)
        c.alu("OR","v1","v1","t5")
        c.mem("sw","v1",20,"t7")
        c.mem("lbu","v1",3,"t0")
        c.nop()
        c.imm("addiu","v1","v1",-1)
        c.shift("sll","v1","v1",8)
        c.alu("addu","t4","t4","v1")
        c.mem("sw","t4",28,"t7")
        c.alu("addu","t5","t5","v1")
        c.mem("sw","t5",36,"t7")
    c.label("finish")
    c.jump(0x800757c4)
    c.nop()
    return c.out(), shade_return


def select_combat_pose(c, phases, metadata, death, compact_base=None):
    # For fixed-view DOS actions, use the matching standing pose outside views 3–5.
    c.imm("sltiu", "t3", "t7", 2)
    c.branch("bne", "t3", "zero", "directional_pose")
    c.imm("ori", "t3", "zero", death)
    c.branch("beq", "t7", "t3", "combat_pose")
    c.imm("addiu", "t3", "t2", -3)
    c.imm("sltiu", "t3", "t3", 3)
    c.branch("bne", "t3", "zero", "combat_pose")
    c.nop()
    c.imm("ori", "t7", "zero", 0)
    c.label("directional_pose")
    c.shift("srl", "t6", "t6", 1)
    c.imm("andi", "t6", "t6", 3)
    if compact_base is None:
        c.shift("sll", "t7", "t7", 9)
        c.shift("sll", "t2", "t2", 2)
        c.alu("addu", "t2", "t2", "t6")
        c.shift("sll", "t2", "t2", 4)
        c.alu("addu", "t0", "t0", "t2")
    else:
        c.shift("sll", "t7", "t7", 5)
        c.shift("sll", "t2", "t2", 2)
        c.alu("addu", "t2", "t2", "t6")
        c.address("t3", compact_base)
        c.branch("beq", "t0", "t3", "linear_pose")
        c.nop()
        c.alu("addu", "t2", "t2", "t7")
        c.alu("addu", "t2", "t2", "t0")
        c.mem("lbu", "t2", 0, "t2")
        c.imm("addiu", "t0", "t0", 64)
        c.shift("sll", "t3", "t2", 1)
        c.shift("sll", "t2", "t2", 4)
        c.alu("subu", "t2", "t2", "t3")
        c.branch("beq", "zero", "zero", "pose_selected")
        c.alu("addu", "t0", "t0", "t2")
        c.label("linear_pose")
        c.shift("sll", "t7", "t7", 4)
        c.shift("sll", "t2", "t2", 4)
        c.alu("addu", "t0", "t0", "t2")
    c.branch("beq", "zero", "zero", "pose_selected")
    c.alu("addu", "t0", "t0", "t7")
    c.label("combat_pose")
    c.imm("addiu", "t7", "t7", -2)
    c.shift("sll", "t7", "t7", 4)
    c.alu("addu", "t7", "t7", "t6")
    c.address("t0", phases)
    c.alu("addu", "t0", "t0", "t7")
    c.mem("lbu", "t7", 0, "t0")
    c.address("t0", metadata)
    c.shift("sll", "t7", "t7", 4)
    c.alu("addu", "t0", "t0", "t7")
    c.label("pose_selected")


def write_layer_uv(c, metadata_offset, packet_offset):
    for uv, packet, parameter, parameter_offset in (
        (4, 12, "lhu", 14),
        (6, 20, "lbu", 12),
    ):
        c.mem("lhu", "t4", metadata_offset + uv, "t0")
        c.mem(parameter, "v1", metadata_offset + parameter_offset, "t0")
        c.nop()
        c.shift("sll", "v1", "v1", 16)
        c.alu("OR", "v1", "v1", "t4")
        c.mem("sw", "v1", packet_offset + packet, "t7")
    c.mem("lhu", "t4", metadata_offset + 8, "t0")
    c.mem("lhu", "t5", metadata_offset + 10, "t0")
    c.mem("sw", "t4", packet_offset + 28, "t7")
    c.mem("sw", "t5", packet_offset + 36, "t7")


def layered_quad(c, overlay_offset):
    write_layer_uv(c, 0, 0)
    c.mem("lbu", "v1", overlay_offset + 12, "t0")
    c.nop()
    c.branch("beq", "v1", "zero", "finish")
    c.nop()
    # Put the second quad after the first, with exactly the same screen vertices.
    c.mem("lw", "t1", 0, "t7")
    c.imm("addiu", "v1", "t7", 0x28)
    c.mem("sw", "t1", 0x28, "t7")
    c.address("t6", 0x00ffffff)
    c.alu("AND", "v1", "v1", "t6")
    c.imm("lui", "t1", "zero", 0x0900)
    c.alu("OR", "v1", "v1", "t1")
    c.mem("sw", "v1", 0, "t7")
    for word in (4, 8, 16, 24, 32):
        c.mem("lw", "v1", word, "t7")
        c.nop()
        c.mem("sw", "v1", word + 0x28, "t7")
    write_layer_uv(c, overlay_offset, 0x28)


def log_native_order(origin, count, buffer, *, unique_buckets=False):
    """Record the old bucket head before committing an ordinary native draw."""
    c = Code(origin)
    c.address("t9", count)
    c.mem("lw", "t7", 0, "t9")
    c.address("t6", buffer)
    if unique_buckets:
        # Save the head from the first write to each bucket. Repeated polygon
        # submissions to that bucket need no additional rewind entry.
        c.imm("sltiu", "t4", "t7", ORDER_LOG_ENTRIES + 1)
        c.branch("beq", "t4", "zero", "overflow")
        c.shift("sll", "t5", "t7", 3)
        c.alu("addu", "t5", "t5", "t6")
        c.label("find_bucket")
        c.branch("beq", "t6", "t5", "checked_buckets")
        c.nop()
        c.mem("lw", "t4", 0, "t6")
        c.imm("addiu", "t6", "t6", 8)
        c.branch("beq", "t4", "t8", "submit")
        c.nop()
        c.branch("beq", "zero", "zero", "find_bucket")
        c.nop()
        c.label("checked_buckets")
        c.imm("sltiu", "t4", "t7", ORDER_LOG_ENTRIES)
        c.branch("beq", "t4", "zero", "overflow")
        c.mem("lw", "t4", 0, "t8")
        c.nop()
    else:
        c.imm("sltiu", "t4", "t7", ORDER_LOG_ENTRIES)
        c.branch("beq", "t4", "zero", "overflow")
        c.shift("sll", "t5", "t7", 3)
        c.mem("lw", "t4", 0, "t8")
        c.alu("addu", "t6", "t6", "t5")
    c.mem("sw", "t8", 0, "t6")
    c.mem("sw", "t4", 4, "t6")
    c.imm("addiu", "t7", "t7", 1)
    c.branch("beq", "zero", "zero", "submit")
    c.nop()
    c.label("overflow")
    c.imm("ori", "t7", "zero", ORDER_LOG_ENTRIES + 1)
    c.label("submit")
    c.mem("sw", "t7", 0, "t9")
    c.jump(0x8002b684)
    c.mem("sw", "v0", 0, "t8")
    return c.out()


def rewind_native_order(c, count, buffer):
    # A failed projection or full packet arena must keep all native primitives.
    c.address("t4", count)
    c.mem("lw", "t8", 0, "t4")
    c.imm("lui", "t9", "zero", 0x800d)
    c.branch("beq", "t8", "zero", "finish")
    c.imm("sltiu", "t2", "t8", ORDER_LOG_ENTRIES + 1)
    c.branch("beq", "t2", "zero", "finish")
    c.mem("lw", "t4", -0x6188, "t9")
    c.mem("lw", "t5", -0x6168, "t9")
    c.imm("addiu", "t4", "t4", 0x28)
    c.alu("sltu", "t2", "t5", "t4")
    c.branch("bne", "t2", "zero", "finish")
    c.shift("sll", "t8", "t8", 3)
    # Restore newest first because a model may submit several polygons to one bucket.
    c.address("t9", buffer)
    c.alu("addu", "t8", "t8", "t9")
    c.label("rewind_bucket")
    c.imm("addiu", "t8", "t8", -8)
    c.mem("lw", "t4", 0, "t8")
    c.mem("lw", "t5", 4, "t8")
    c.branch("bne", "t8", "t9", "rewind_bucket")
    c.mem("sw", "t5", 0, "t4")

"""Emit the Japanese Rev 1 Lanugo rendering hooks."""

from mipswords import Code

IDLE_ACTION = 0x20
WALK_ACTION = 0x2c
GREEN_GOBLIN_TYPE = 70


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


# Keep actor projection and hit testing when substituting a sprite.
def suppress(origin, order_table_register="v1", walk_ready=None):
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
    c.imm("xori","t9","t9",IDLE_ACTION)
    if walk_ready is None:
        c.branch("bne","t9","zero","normal")
        c.imm("ori","t9","zero",10)
        c.nop()
        c.branch("bne","t8","t9","normal")
        c.nop()
    else:
        c.imm("andi", "t8", "t8", 0x1ff)
        c.imm("xori", "t8", "t8", GREEN_GOBLIN_TYPE)
        c.branch("bne", "t8", "zero", "normal")
        c.nop()
        require_atlas_action(c, "t9", "t8", walk_ready, "normal")
    c.mem("sh","s3",0x18c,"sp")
    c.jump(0x8002b684)
    c.nop()
    c.label("normal")
    c.jump(0x8002b684)
    c.mem("sw","v0",0,order_table_register)
    return c.out()

# Idle view order measured in the DOS renderer's 32-sector direction table.
DOS_IDLE_DIRECTIONS = bytes((
    0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4,
    4, 4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 0, 0,
))


def draw(origin, metadata, direction_table, clut=0x401c, walk_ready=None):
    c=Code(origin)
    c.mem("lw","t0",0xe0,"sp")
    c.imm("ori", "t1", "zero", 10 if walk_ready is None else GREEN_GOBLIN_TYPE)
    if walk_ready is None:
        c.mem("lbu","t2",26,"t0")
        c.nop()
    else:
        c.mem("lhu", "t2", 0, "t0")
        c.nop()
        c.imm("andi", "t2", "t2", 0x1ff)
    c.branch("bne","t2","t1","finish")
    c.mem("lbu","t4",23,"t0")
    c.mem("lhu","t6",12,"t0")
    c.imm("andi","t4","t4",0x3f)
    c.imm("xori","t4","t4",IDLE_ACTION)
    if walk_ready is None:
        c.branch("bne","t4","zero","finish")
    else:
        require_atlas_action(c, "t4", "t7", walk_ready, "finish")
        c.alu("sltu", "t7", "zero", "t4")
        c.shift("sll", "t7", "t7", 8)  # Walking metadata follows the 256-byte idle table.
    # Group the seven native animation frames into four DOS phases.
    c.shift("srl","t6","t6",13)
    c.imm("andi","t6","t6",3)
    c.alu("subu","t1","a3","a1")
    c.branch("blez","t1","zero","finish")
    c.nop()
    c.imm("sltiu","t2","t1",256)
    c.branch("beq","t2","zero","finish")
    c.nop()
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
    c.shift("sll", "t2", "t2", 2)
    c.alu("addu", "t2", "t2", "t6")
    c.shift("sll", "t2", "t2", 3)
    c.alu("addu", "t0", "t0", "t2")
    if walk_ready is not None:
        c.alu("addu", "t0", "t0", "t7")

    # Pass the original projected foot/center through the DOS hotspot.
    c.mem("lbu","t2",2,"t0") # width
    c.mem("lbu","t3",3,"t0") # height
    c.mem("lbu","t4",4,"t0") # hotspot x
    c.mem("lbu","t5",5,"t0") # hotspot y
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
    c.mem("lhu","t4",0,"t0") # packed base uv
    c.mem("lbu","t5",2,"t0")
    c.mflo("t2")
    c.alu("addu","t2","t8","t2") # right
    c.alu("addu","t3","t9","t1") # bottom

    c.imm("lui","t6","zero",0x800d)
    c.mem("lw","t7",-0x6188,"t6") # packet alloc
    c.mem("lw","v0",-0x6168,"t6") # packet end
    c.imm("addiu","v1","t7",0x28)
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
    return c.out()

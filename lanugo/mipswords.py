import struct

REG = dict(zip("zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra".split(),range(32)))

class Code:
    def __init__(self, origin):
        self.origin = origin
        self.words = []
        self.labels = {}
        self.branches = []

    def add(self, word):
        self.words.append(word)

    def label(self, name):
        self.labels[name] = len(self.words)

    def mem(self, mnemonic, rt, offset, rs):
        self.imm(mnemonic, rt, rs, offset)

    def imm(self, mnemonic, rt, rs, value):
        op = dict(addiu=9, sltiu=11, andi=12, ori=13, xori=14, lui=15,
                  lb=32, lh=33, lw=35, lbu=36, lhu=37, sb=40, sh=41, sw=43)[mnemonic]
        self.add(op<<26 | REG[rs]<<21 | REG[rt]<<16 | (value&65535))

    def alu(self, mnemonic, rd, rs, rt):
        funct = dict(addu=33, subu=35, AND=36, OR=37, XOR=38, slt=42, sltu=43)[mnemonic]
        self.add(REG[rs]<<21 | REG[rt]<<16 | REG[rd]<<11 | funct)

    def shift(self, mnemonic, rd, rt, count):
        funct = dict(sll=0, srl=2, sra=3)[mnemonic]
        self.add(REG[rt]<<16 | REG[rd]<<11 | count<<6 | funct)

    def muldiv(self, mnemonic, rs, rt):
        self.add(REG[rs]<<21 | REG[rt]<<16 | dict(mult=24, multu=25, div=26, divu=27)[mnemonic])

    def mflo(self, rd):
        self.add(REG[rd]<<11 | 18)

    def branch(self, mnemonic, rs, rt, label):
        op = dict(beq=4, bne=5, blez=6, bgtz=7)[mnemonic]
        self.branches.append((len(self.words), label))
        self.add(op<<26 | REG[rs]<<21 | REG[rt]<<16)

    def address(self, reg, address):
        self.imm("lui",reg,"zero",address>>16)
        self.imm("ori",reg,reg,address)

    def jump(self, address, link=False):
        self.add(((3 if link else 2)<<26) | ((address>>2)&0x3ffffff))

    def nop(self):
        self.add(0)

    def out(self):
        for index,label in self.branches:
            distance=self.labels[label]-index-1
            assert -32768<=distance<32768
            self.words[index]=(self.words[index]&0xffff0000)|(distance&0xffff)
        return struct.pack(f"<{len(self.words)}I",*self.words)

def ret(code, delay=None):
    code.add(REG["ra"]<<21 | 8)
    if delay is None:
        code.nop()
    else:
        delay()

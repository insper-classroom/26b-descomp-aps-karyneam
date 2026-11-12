"""Modelo funcional independente para conferir a CPU no cocotb (C+C++B+B+).

A entrada e a ROM .hex do firmware acumulativo. A cada passo, o modelo calcula
PC, resultado da ULA, registradores, RAM e HI/LO. Nao usa sinais internos do DUT.
Arquitetura deste projeto: little-endian, sem delay slot e sem excecoes.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1
ROM_PATH = Path(__file__).resolve().parents[1] / "programs" / "conceito_bplus_selftest.hex"

R_FUNCS = {
    0: "sll", 2: "srl", 3: "sra", 4: "sllv", 6: "srlv", 7: "srav",
    8: "jr", 9: "jalr", 16: "mfhi", 17: "mthi", 18: "mflo", 19: "mtlo",
    24: "mult", 25: "multu", 32: "add", 33: "addu", 34: "sub", 35: "subu",
    36: "and", 37: "or", 38: "xor", 39: "nor", 42: "slt", 43: "sltu",
}
OPCODES = {
    2: "j", 3: "jal", 4: "beq", 5: "bne", 6: "blez", 7: "bgtz",
    8: "addi", 9: "addiu", 10: "slti", 11: "sltiu", 12: "andi",
    13: "ori", 14: "xori", 15: "lui", 32: "lb", 33: "lh", 35: "lw",
    36: "lbu", 37: "lhu", 40: "sb", 41: "sh", 43: "sw",
}
EXPECTED = frozenset(R_FUNCS.values()) | frozenset(OPCODES.values()) | {"bltz", "bgez"}
assert len(EXPECTED) == 48
BRANCHES = frozenset(("beq", "bne", "bltz", "bgez", "blez", "bgtz"))


def signed(x, bits=32):
    x &= (1 << bits) - 1
    return x - (1 << bits) if x & (1 << (bits - 1)) else x


def decode(w):
    op = (w >> 26) & 63
    if op == 0:
        return R_FUNCS.get(w & 63, "INVALID_R")
    if op == 1:
        return {0: "bltz", 1: "bgez"}.get((w >> 16) & 31, "INVALID_REGIMM")
    return OPCODES.get(op, "INVALID_OP")


@dataclass(frozen=True)
class Step:
    pc: int
    instruction: int
    mnemonic: str
    alu: int
    next_pc: int
    signature: int
    branch_taken: Optional[bool]


class MipsReference:
    def __init__(self, program=None):
        if program is None:
            program = [int(line, 16) for line in ROM_PATH.read_text(encoding="utf-8").split()]
        self.program = list(program)
        self.pc = 0
        self.reg = [0] * 32
        self.ram = bytearray(256)
        self.hi = 0
        self.lo = 0
        self.signature = 0
        self.coverage = Counter()
        self.branches = defaultdict(lambda: Counter())

    def read(self, address, size, extend=False):
        assert address % size == 0 and 0 <= address and address + size <= len(self.ram), (
            f"Leitura fora/desalinhada: 0x{address:08X}, {size} bytes"
        )
        value = int.from_bytes(self.ram[address:address + size], 'little')
        return (signed(value, size * 8) if extend else value) & MASK32

    def write(self, address, size, value):
        assert address % size == 0 and 0 <= address and address + size <= len(self.ram), (
            f"Escrita fora/desalinhada: 0x{address:08X}, {size} bytes"
        )
        self.ram[address:address + size] = (value & ((1 << (size * 8)) - 1)).to_bytes(size, 'little')

    def step(self):
        old_pc = self.pc
        assert old_pc % 4 == 0 and 0 <= old_pc // 4 < len(self.program), f"PC fora da ROM: {old_pc:08X}"
        w = self.program[old_pc // 4]
        op, rs, rt = (w >> 26) & 63, (w >> 21) & 31, (w >> 16) & 31
        rd, shamt, fn = (w >> 11) & 31, (w >> 6) & 31, w & 63
        imm = w & 0xFFFF
        si = signed(imm, 16)
        a, b = self.reg[rs], self.reg[rt]
        next_pc = (old_pc + 4) & MASK32
        alu = 0
        dest = None
        branch_taken = None
        name = decode(w)
        assert name in EXPECTED, f"Instrucao nao suportada: {w:08X} PC={old_pc:08X}"

        if op == 0:
            if fn in (32, 33):
                alu = (a + b) & MASK32
                dest = (rd, alu)
            elif fn in (34, 35):
                alu = (a - b) & MASK32
                dest = (rd, alu)
            elif fn == 36:
                alu = a & b
                dest = (rd, alu)
            elif fn == 37:
                alu = a | b
                dest = (rd, alu)
            elif fn == 38:
                alu = a ^ b
                dest = (rd, alu)
            elif fn == 39:
                alu = (~(a | b)) & MASK32
                dest = (rd, alu)
            elif fn == 42:
                alu = int(signed(a) < signed(b))
                dest = (rd, alu)
            elif fn == 43:
                alu = int(a < b)
                dest = (rd, alu)
            elif fn in (0, 2, 3, 4, 6, 7):
                amt = (a & 31) if fn in (4, 6, 7) else shamt
                if fn in (0, 4):
                    alu = (b << amt) & MASK32
                elif fn in (2, 6):
                    alu = b >> amt
                else:
                    alu = (signed(b) >> amt) & MASK32
                dest = (rd, alu)
            elif fn == 16:
                alu = self.hi
                dest = (rd, alu)
            elif fn == 18:
                alu = self.lo
                dest = (rd, alu)
            elif fn == 17:
                self.hi = a
            elif fn == 19:
                self.lo = a
            elif fn in (24, 25):
                prod = (signed(a) * signed(b)) & MASK64 if fn == 24 else (a * b) & MASK64
                self.hi, self.lo = (prod >> 32) & MASK32, prod & MASK32
            elif fn == 8:
                next_pc = a
            elif fn == 9:
                dest = (rd, next_pc)
                next_pc = a
        elif op == 1:
            assert rt in (0, 1)
            branch_taken = signed(a) < 0 if rt == 0 else signed(a) >= 0
            if branch_taken:
                next_pc = (next_pc + (si << 2)) & MASK32
        elif op in (8, 9):
            alu = (a + si) & MASK32
            dest = (rt, alu)
        elif op == 10:
            alu = int(signed(a) < si)
            dest = (rt, alu)
        elif op == 11:
            alu = int(a < (si & MASK32))
            dest = (rt, alu)
        elif op == 12:
            alu = a & imm
            dest = (rt, alu)
        elif op == 13:
            alu = a | imm
            dest = (rt, alu)
        elif op == 14:
            alu = a ^ imm
            dest = (rt, alu)
        elif op == 15:
            alu = imm << 16
            dest = (rt, alu)
        elif op in (32, 33, 35, 36, 37, 40, 41, 43):
            alu = (a + si) & MASK32
            if op in (32, 33, 35, 36, 37):
                size = 4 if op == 35 else 2 if op in (33, 37) else 1
                dest = (rt, self.read(alu, size, op in (32, 33)))
            else:
                size = 4 if op == 43 else 2 if op == 41 else 1
                self.write(alu, size, b)
                if op == 43 and alu == 252:
                    self.signature = b
        elif op in (4, 5, 6, 7):
            if op == 4:
                branch_taken = a == b
            elif op == 5:
                branch_taken = a != b
            elif op == 6:
                assert rt == 0
                branch_taken = signed(a) <= 0
            else:
                assert rt == 0
                branch_taken = signed(a) > 0
            if branch_taken:
                next_pc = (next_pc + (si << 2)) & MASK32
        elif op in (2, 3):
            if op == 3:
                dest = (31, next_pc)
            next_pc = (next_pc & 0xF0000000) | ((w & 0x03FFFFFF) << 2)

        if dest is not None and dest[0] != 0:
            self.reg[dest[0]] = dest[1] & MASK32
        self.reg[0] = 0
        self.coverage[name] += 1
        if branch_taken is not None:
            self.branches[name]['taken' if branch_taken else 'not_taken'] += 1
        self.pc = next_pc
        return Step(old_pc, w, name, alu, next_pc, self.signature, branch_taken)

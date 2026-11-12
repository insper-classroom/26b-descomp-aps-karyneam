#!/usr/bin/env python3
"""Emulador de referencia independente da ROM acumulativa C+C+.
Modelo little-endian para RAM byte-addressable; NAO simula o VHDL/FPGA.
A verificacao e feita pelo programa real (desvios para fail), nao so por cobertura.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
words = [int(s, 16) for s in (ROOT / 'programs/conceito_cplus_selftest.hex').read_text().split()]
registers = [0] * 32
mem = bytearray(256)
mask = 0xffffffff
pc, steps = 0, 0
seen = set()
trace = []


def signed(x, width=32):
    x &= (1 << width) - 1
    return x - (1 << width) if (x >> (width - 1)) else x


def read(addr, width, is_signed=False):
    assert 0 <= addr and addr + width <= 256 and (addr % width == 0), (hex(addr), width)
    value = int.from_bytes(mem[addr:addr + width], 'little')
    return signed(value, width * 8) & mask if is_signed else value


def write(addr, width, value):
    assert 0 <= addr and addr + width <= 256 and (addr % width == 0), (hex(addr), width)
    mem[addr:addr + width] = (value & ((1 << (width * 8)) - 1)).to_bytes(width, 'little')


functs = {0: 'sll', 2: 'srl', 3: 'sra', 8: 'jr',
          32: 'add', 33: 'addu', 34: 'sub', 35: 'subu',
          36: 'and', 37: 'or', 38: 'xor', 39: 'nor', 42: 'slt', 43: 'sltu'}
opcodes = {2: 'j', 3: 'jal', 4: 'beq', 5: 'bne', 8: 'addi', 9: 'addiu',
           10: 'slti', 11: 'sltiu', 12: 'andi', 13: 'ori', 14: 'xori', 15: 'lui',
           32: 'lb', 33: 'lh', 35: 'lw', 36: 'lbu', 37: 'lhu', 40: 'sb', 41: 'sh', 43: 'sw'}

for steps in range(1, 600):
    assert pc % 4 == 0 and 0 <= pc // 4 < len(words), f'PC fora da ROM: {pc:08X}'
    word = words[pc // 4]
    op, rs, rt = (word >> 26) & 63, (word >> 21) & 31, (word >> 16) & 31
    rd, shamt, fn = (word >> 11) & 31, (word >> 6) & 31, word & 63
    imm = word & 65535
    si = signed(imm, 16)
    a, b = registers[rs], registers[rt]
    next_pc, dest = pc + 4, None
    if op == 0:
        name = functs.get(fn)
        assert name, f'funct nao implementada {fn}'
        if fn in (32, 33): dest = (rd, a + b)
        elif fn in (34, 35): dest = (rd, a - b)
        elif fn == 36: dest = (rd, a & b)
        elif fn == 37: dest = (rd, a | b)
        elif fn == 38: dest = (rd, a ^ b)
        elif fn == 39: dest = (rd, ~(a | b))
        elif fn == 42: dest = (rd, int(signed(a) < signed(b)))
        elif fn == 43: dest = (rd, int(a < b))
        elif fn == 0: dest = (rd, b << shamt)
        elif fn == 2: dest = (rd, b >> shamt)
        elif fn == 3: dest = (rd, signed(b) >> shamt)
        elif fn == 8: next_pc = a
    else:
        name = opcodes.get(op)
        assert name, f'opcode nao implementado {op}'
        if op in (8, 9): dest = (rt, a + si)
        elif op == 10: dest = (rt, int(signed(a) < si))
        elif op == 11: dest = (rt, int(a < (si & mask)))
        elif op == 12: dest = (rt, a & imm)
        elif op == 13: dest = (rt, a | imm)
        elif op == 14: dest = (rt, a ^ imm)
        elif op == 15: dest = (rt, imm << 16)
        elif op in (32, 33, 35, 36, 37, 40, 41, 43):
            addr = (a + si) & mask
            if op == 32: dest = (rt, read(addr, 1, True))
            elif op == 33: dest = (rt, read(addr, 2, True))
            elif op == 35: dest = (rt, read(addr, 4))
            elif op == 36: dest = (rt, read(addr, 1))
            elif op == 37: dest = (rt, read(addr, 2))
            elif op == 40: write(addr, 1, b)
            elif op == 41: write(addr, 2, b)
            elif op == 43: write(addr, 4, b)
        elif op == 4 and a == b: next_pc += si * 4
        elif op == 5 and a != b: next_pc += si * 4
        elif op in (2, 3):
            if op == 3: dest = (31, pc + 4)
            next_pc = ((pc + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2)
    if dest and dest[0] != 0:
        registers[dest[0]] = dest[1] & mask
    registers[0] = 0
    seen.add(name)
    trace.append((pc, name))
    pc = next_pc
    status = read(252, 4)
    if status in (1, 2):
        break
else:
    raise AssertionError('programa ultrapassou 600 instrucoes sem concluir')

expected_c = {'add', 'addu', 'addi', 'addiu', 'sub', 'subu', 'slt', 'sltu',
              'slti', 'sltiu', 'and', 'andi', 'or', 'ori', 'xor', 'xori',
              'nor', 'lui', 'sll', 'srl', 'sra', 'lw', 'sw', 'beq', 'bne',
              'j', 'jal', 'jr'}
expected_cplus = {'lb', 'lbu', 'lh', 'lhu', 'sb', 'sh'}
assert status == 1, f'FAIL do autoteste no PC={pc:08X}; ultima instrucao: {trace[-1]}'
assert seen == (expected_c | expected_cplus), f'Falta: {(expected_c | expected_cplus) - seen}'
assert read(64, 4) == 0x00ef0000, f'RAM[0x40] final inesperada: {read(64, 4):08X}'
print(f'PASS: conceitos C + C+; {steps} instrucoes executadas; {len(seen)}/34 instrucoes distintas')
print('PASS: signed/unsigned, byte lanes 0..3, halfword baixo/alto, escrita parcial e regressoes C')
print(f'Status RAM[0xFC]={status}; RAM[0x40]=0x{read(64, 4):08X}')

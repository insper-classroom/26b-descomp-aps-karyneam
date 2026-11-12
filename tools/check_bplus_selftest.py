#!/usr/bin/env python3
"""Emulador independente para o programa acumulativo C+C++B+B+.

Executa o MESMO arquivo .hex que vai para a ROM da FPGA, verifica as
comparacoes realizadas em Assembly e acompanha cobertura por instrucao.
NAO simula VHDL, nao substitui Quartus, FPGA nem cocotb.
"""
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
words = [int(line, 16) for line in (ROOT / 'programs/conceito_bplus_selftest.hex').read_text().split()]
registers = [0] * 32
mem = bytearray(256)
mask = (1 << 32) - 1
pc = 0
hi = 0
lo = 0
seen = set()
trace = []
branch = defaultdict(lambda: {'taken': 0, 'not_taken': 0})


def signed(x, width=32):
    x &= (1 << width) - 1
    return x - (1 << width) if x & (1 << (width - 1)) else x


def read(addr, width, is_signed=False):
    assert 0 <= addr and addr + width <= len(mem) and addr % width == 0, (hex(addr), width)
    v = int.from_bytes(mem[addr:addr + width], 'little')
    return (signed(v, width * 8) & mask) if is_signed else v


def write(addr, width, value):
    assert 0 <= addr and addr + width <= len(mem) and addr % width == 0, (hex(addr), width)
    mem[addr:addr + width] = (value & ((1 << (8 * width)) - 1)).to_bytes(width, 'little')


functs = {0: 'sll', 2: 'srl', 3: 'sra', 4: 'sllv', 6: 'srlv', 7: 'srav', 16: 'mfhi', 17: 'mthi', 18: 'mflo',
          19: 'mtlo', 24: 'mult', 25: 'multu',
          8: 'jr', 9: 'jalr', 32: 'add', 33: 'addu', 34: 'sub', 35: 'subu',
          36: 'and', 37: 'or', 38: 'xor', 39: 'nor', 42: 'slt', 43: 'sltu'}
opcodes = {2: 'j', 3: 'jal', 4: 'beq', 5: 'bne', 6: 'blez', 7: 'bgtz',
           8: 'addi', 9: 'addiu', 10: 'slti', 11: 'sltiu', 12: 'andi',
           13: 'ori', 14: 'xori', 15: 'lui', 32: 'lb', 33: 'lh',
           35: 'lw', 36: 'lbu', 37: 'lhu', 40: 'sb', 41: 'sh', 43: 'sw'}

for steps in range(1, 1500):
    assert (pc & 3) == 0 and 0 <= pc // 4 < len(words), f'PC fora da ROM: {pc:08X}'
    w = words[pc // 4]
    op, rs, rt = (w >> 26) & 63, (w >> 21) & 31, (w >> 16) & 31
    rd, shamt, fn = (w >> 11) & 31, (w >> 6) & 31, w & 63
    imm = w & 0xFFFF
    si = signed(imm, 16)
    a, b = registers[rs], registers[rt]
    next_pc, dest = (pc + 4) & mask, None
    if op == 0:
        name = functs.get(fn)
        assert name is not None, f'funct desconhecida {fn} em PC={pc:08X}'
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
        elif fn == 4: dest = (rd, b << (a & 31))
        elif fn == 6: dest = (rd, b >> (a & 31))
        elif fn == 7: dest = (rd, signed(b) >> (a & 31))
        elif fn == 16: dest = (rd, hi)
        elif fn == 17: hi = a
        elif fn == 18: dest = (rd, lo)
        elif fn == 19: lo = a
        elif fn == 24:
            product = (signed(a) * signed(b)) & ((1 << 64) - 1)
            hi, lo = (product >> 32) & mask, product & mask
        elif fn == 25:
            product = a * b
            hi, lo = (product >> 32) & mask, product & mask
        elif fn == 8: next_pc = a
        elif fn == 9:
            dest = (rd, next_pc)
            next_pc = a
    elif op == 1:
        assert rt in (0, 1), f'REGIMM invalido: rt={rt}'
        name = 'bltz' if rt == 0 else 'bgez'
        taken = signed(a) < 0 if rt == 0 else signed(a) >= 0
        branch[name]['taken' if taken else 'not_taken'] += 1
        if taken: next_pc = (next_pc + (si << 2)) & mask
    else:
        name = opcodes.get(op)
        assert name is not None, f'opcode desconhecido {op} em PC={pc:08X}'
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
        elif op in (4, 5, 6, 7):
            if op == 4: taken = a == b
            elif op == 5: taken = a != b
            elif op == 6:
                assert rt == 0
                taken = signed(a) <= 0
            else:
                assert rt == 0
                taken = signed(a) > 0
            branch[name]['taken' if taken else 'not_taken'] += 1
            if taken: next_pc = (next_pc + (si << 2)) & mask
        elif op in (2, 3):
            if op == 3: dest = (31, next_pc)
            next_pc = (next_pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
    if dest is not None and dest[0] != 0:
        registers[dest[0]] = dest[1] & mask
    registers[0] = 0
    seen.add(name)
    trace.append((pc, name))
    pc = next_pc
    status = read(252, 4)
    if status in (1, 2): break
else:
    raise AssertionError('programa ultrapassou 1500 instrucoes sem concluir')

expected_c = {'add', 'addu', 'addi', 'addiu', 'sub', 'subu', 'slt', 'sltu',
              'slti', 'sltiu', 'and', 'andi', 'or', 'ori', 'xor', 'xori',
              'nor', 'lui', 'sll', 'srl', 'sra', 'lw', 'sw', 'beq', 'bne',
              'j', 'jal', 'jr'}
expected_cplus = {'lb', 'lbu', 'lh', 'lhu', 'sb', 'sh'}
expected_b = {'sllv', 'srlv', 'srav', 'bltz', 'bgez', 'blez', 'bgtz', 'jalr'}
expected_bplus = {'mult', 'multu', 'mfhi', 'mflo', 'mthi', 'mtlo'}
assert status == 1, f'FAIL em pc={pc:08X}; ultima instrucao={trace[-1]}'
assert seen == (expected_c | expected_cplus | expected_b | expected_bplus), (
    f'Faltaram instrucoes: {sorted((expected_c | expected_cplus | expected_b | expected_bplus)-seen)}'
)
for name in ('bltz', 'bgez', 'blez', 'bgtz'):
    assert branch[name]['taken'] >= 1, f'{name} nao foi testado como tomado'
    assert branch[name]['not_taken'] >= 1, f'{name} nao foi testado como nao tomado'
assert read(64, 4) == 0x00EF0000, f'RAM[0x40]={read(64, 4):08X} inesperado'
assert registers[23] == (240 * 4), 'jalr rd, rs nao gravou PC+4 corretamente em $s7'
assert registers[31] == (248 * 4), 'jalr rs nao gravou PC+4 corretamente em $ra'
assert (hi, lo) == (0, 0), 'mult por zero nao limpou HI/LO'
assert registers[10] == 0, 'mflo final nao retornou zero'
print(f'PASS: C + C+ + B + B+; {steps} instrucoes executadas; {len(seen)}/48 mnemonicos executados')
print('PASS: branch tomado/nao tomado, shifts low5 com sinal, jalr com rd e $ra')
print(f'PASS: RAM[0xFC]={status}; RAM[0x40]=0x{read(64,4):08X}; '+
      f'jalr $s7={registers[23]:08X}, $ra={registers[31]:08X}')

print('PASS: mult/multu signed/unsigned, limites de 32 bits, zero, mfhi/mflo e mthi/mtlo')

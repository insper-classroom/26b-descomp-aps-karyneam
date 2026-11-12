#!/usr/bin/env python3
"""Valida o modelo de referencia sem cocotb (nao valida RTL)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'test'))
from mips_reference import MipsReference, EXPECTED, BRANCHES

cpu = MipsReference()
for steps in range(1, 851):
    result = cpu.step()
    assert result.signature != 2, f'FAIL em {result.pc:08X} ({result.mnemonic})'
    if result.signature == 1:
        break
else:
    raise AssertionError('Timeout de 850 instrucoes')

assert set(cpu.coverage) == EXPECTED, sorted(EXPECTED - set(cpu.coverage))
for b in BRANCHES:
    assert cpu.branches[b]['taken'] > 0, f'{b}: sem taken'
    assert cpu.branches[b]['not_taken'] > 0, f'{b}: sem not_taken'
assert cpu.read(64, 4) == 0x00EF0000
assert cpu.reg[23] == 960, cpu.reg[23]
assert cpu.reg[31] == 992, cpu.reg[31]
assert (cpu.hi, cpu.lo) == (0,0)
print(f'PASS modelo de referencia: {steps} instrucoes; {len(cpu.coverage)}/48 mnemonicos; assinatura={result.signature}')
print('PASS branches taken/not-taken, RAM e HI/LO finais')
print('IMPORTANTE: somente o modelo Python foi executado; rode cocotb para testar o VHDL.')

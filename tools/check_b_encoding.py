#!/usr/bin/env python3
"""Testes rapidos de encoding dos 8 mnemonicos B no montador."""
import assemble_b
base = assemble_b.base
labels = {'alvo': 14}


def check(line, i, result):
    got = base.assemble(line, i, labels)
    assert got == result, f'{line}: esperado={result:08X}, obtido={got:08X}'


check('sllv $t2, $t0, $t1', 0, base.r(9, 8, 10, 0, 4))
check('srlv $s0, $s1, $s2', 0, base.r(18, 17, 16, 0, 6))
check('srav $a0, $a1, $a2', 0, base.r(6, 5, 4, 0, 7))
check('bltz $t0, alvo', 3, base.i(1, 8, 0, 10))
check('bgez $t0, alvo', 3, base.i(1, 8, 1, 10))
check('blez $t0, alvo', 3, base.i(6, 8, 0, 10))
check('bgtz $t0, alvo', 3, base.i(7, 8, 0, 10))
check('jalr $s7, $t5', 0, base.r(13, 0, 23, 0, 9))
check('jalr $t5', 0, base.r(13, 0, 31, 0, 9))
check('ori $t5, $zero, alvo', 0, base.i(13, 0, 13, 56))
print('PASS: encodings das 8 instrucoes B, ambas as formas de jalr e endereco de rotulo')

#!/usr/bin/env python3
"""Confere opcodes/funct e campos dos seis formatos R do conceito B+."""
import assemble_bplus
base = assemble_bplus.base

def check(source, expected):
    result = base.assemble(source, 0, {})
    assert result == expected, f'{source}: esperado {expected:08X}, obtido {result:08X}'

check('mult $t0, $t1', base.r(8, 9, 0, 0, 24))
check('multu $s0, $s1', base.r(16, 17, 0, 0, 25))
check('mfhi $t2', base.r(0, 0, 10, 0, 16))
check('mflo $s2', base.r(0, 0, 18, 0, 18))
check('mthi $s3', base.r(19, 0, 0, 0, 17))
check('mtlo $a0', base.r(4, 0, 0, 0, 19))
# Confirmar sintaxe correta: operandos nao devem trocar rs,rt,rd.
for invalid in ('mult $t0', 'mfhi $t0, $t1', 'mthi $t0, $t1'):
    try:
        base.assemble(invalid, 0, {})
    except ValueError:
        pass
    else:
        raise AssertionError(f'Deveria rejeitar: {invalid}')
print('PASS: codificacao das 6 instrucoes B+ e verificacao dos operandos')

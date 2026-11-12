"""Programas MIPS curtos e independentes: um programa por instrucao da APS.

Cada programa testa casos de borda da instrucao indicada. A CPU calcula
os resultados e os compara a constantes no Assembly. Para PASS escreve 1 em
0xFC; para FAIL escreve 2. Suporte de setup (lui/ori/bne/sw...) e permitido.
Nenhum arquivo VHDL de producao e modificado.
"""

from typing import List

R3 = {
    'add': [(5, 3, 8), (-5, 2, -3)],
    'addu': [(0xFFFFFFFF, 2, 1), (0, 0, 0)],
    'sub': [(5, 8, -3), (-7, -8, 1)],
    'subu': [(0, 1, 0xFFFFFFFF), (0xFFFFFFFF, 0xFFFFFFFF, 0)],
    'slt': [(-1, 1, 1), (0x7FFFFFFF, -1, 0), (3, 3, 0)],
    'sltu': [(0xFFFFFFFF, 1, 0), (1, 0xFFFFFFFF, 1), (3, 3, 0)],
    'and': [(0xFF00FF00, 0x0F0F0F0F, 0x0F000F00), (0xFFFFFFFF, 0, 0)],
    'or': [(0xFF000000, 0x00F0F000, 0xFFF0F000), (0, 0, 0)],
    'xor': [(0xAAAAAAAA, 0x55555555, 0xFFFFFFFF), (0x12345678, 0x12345678, 0)],
    'nor': [(0, 0, 0xFFFFFFFF), (0xF0F0F0F0, 0x0F000000, 0x000F0F0F)],
}

I3 = {
    'addi': [(5, -7, -2), (-32768, 32767, -1)],
    'addiu': [(0xFFFFFFFF, 2, 1), (5, -7, -2)],
    'slti': [(-1, 1, 1), (4, -1, 0), (0, 0, 0)],
    'sltiu': [(1, -1, 1), (0xFFFFFFFF, 1, 0), (0, 0, 0)],
    'andi': [(0xFFFF00FF, 0x00F0, 0xF0), (0xFFFFFFFF, 0, 0)],
    'ori': [(0x12340000, 0xABCD, 0x1234ABCD), (0, 0x8000, 0x8000)],
    'xori': [(0xFFFF000F, 0xFFFF, 0xFFFFFFF0), (0, 0xFF00, 0xFF00)],
}

SHIFTS = {
    'sll': [(3, 2, 12), (0x80000001, 31, 0x80000000)],
    'srl': [(0x80000000, 31, 1), (0xFFFFFFFF, 1, 0x7FFFFFFF)],
    'sra': [(0x80000000, 31, 0xFFFFFFFF), (0xFFFFFFF8, 2, 0xFFFFFFFE)],
    'sllv': [(3, 2, 12), (0x80000001, 63, 0x80000000)],
    'srlv': [(0x80000000, 31, 1), (0xFFFFFFFF, 33, 0x7FFFFFFF)],
    'srav': [(0x80000000, 31, 0xFFFFFFFF), (0xFFFFFFF8, 34, 0xFFFFFFFE)],
}

ALL = sorted([
    'add','addu','addi','addiu','sub','subu','slt','sltu','slti','sltiu',
    'and','andi','or','ori','xor','xori','nor','lui',
    'sll','srl','sra','lw','sw','beq','bne','j','jal','jr',
    'lb','lh','lbu','lhu','sb','sh',
    'sllv','srlv','srav','bltz','bgez','blez','bgtz','jalr',
    'mult','multu','mfhi','mflo','mthi','mtlo',
])
assert len(ALL) == 48 and len(set(ALL)) == 48


def load(reg: str, val: int) -> List[str]:
    val &= 0xFFFFFFFF
    # LUI e ORI carregam qualquer palavra; evitamos pseudo-instrucoes.
    if val <= 0xFFFF:
        return [f'ori {reg}, $zero, 0x{val:04X}']
    return [f'lui {reg}, 0x{val >> 16:04X}',
            f'ori {reg}, {reg}, 0x{val & 0xFFFF:04X}']


def check(reg: str, val: int) -> List[str]:
    return load('$t3', val) + [f'bne {reg}, $t3, fail']


def case(mnemonic: str) -> List[str]:
    if mnemonic not in ALL:
        raise ValueError(f'Instrucao desconhecida: {mnemonic}')
    a: List[str] = []

    if mnemonic in R3:
        for x, y, value in R3[mnemonic]:
            a += load('$t0', x) + load('$t1', y)
            a += [f'{mnemonic} $t2, $t0, $t1'] + check('$t2', value)
    elif mnemonic in I3:
        for x, imm, value in I3[mnemonic]:
            a += load('$t0', x)
            a += [f'{mnemonic} $t2, $t0, {imm}'] + check('$t2', value)
    elif mnemonic == 'lui':
        for imm in (0x1234, 0x8000, 0):
            a += [f'lui $t2, 0x{imm:04X}'] + check('$t2', imm << 16)
    elif mnemonic in SHIFTS:
        for x, amount, val in SHIFTS[mnemonic]:
            a += load('$t1', x)
            if mnemonic.endswith('v'):
                a += load('$t0', amount)
                a += [f'{mnemonic} $t2, $t1, $t0']
            else:
                a += [f'{mnemonic} $t2, $t1, {amount}']
            a += check('$t2', val)
    elif mnemonic in ('lw', 'sw'):
        for address, value in [(32, 0xF012ABCD), (40, 0x13579BDF)]:
            a += load('$t0', value)
            a += [f'sw $t0, {address}($zero)', f'lw $t2, {address}($zero)']
            a += check('$t2', value)
    elif mnemonic in ('lb', 'lbu', 'lh', 'lhu'):
        a += load('$t0', 0x80FF7F01) + ['sw $t0, 32($zero)']
        table = {
            'lb': [(32,1),(33,127),(34,0xFFFFFFFF),(35,0xFFFFFF80)],
            'lbu': [(32,1),(33,127),(34,255),(35,128)],
            'lh': [(32,0x7F01),(34,0xFFFF80FF)],
            'lhu': [(32,0x7F01),(34,0x80FF)],
        }
        for address, value in table[mnemonic]:
            a += [f'{mnemonic} $t2, {address}($zero)'] + check('$t2', value)
        # Offset negativo para verificar endereco base + sinal.
        address, value = table[mnemonic][-1]
        a += load('$t4', address + 4)
        a += [f'{mnemonic} $t2, -4($t4)'] + check('$t2', value)
    elif mnemonic == 'sb':
        a += load('$t0', 0x80FF7F01) + ['sw $t0, 32($zero)']
        a += load('$t1', 0x12345678)
        a += ['sb $t1, 33($zero)', 'lw $t2, 32($zero)'] + check('$t2', 0x80FF7801)
        a += ['sb $t1, 35($zero)', 'lw $t2, 32($zero)'] + check('$t2', 0x78FF7801)
    elif mnemonic == 'sh':
        a += load('$t0', 0x80FF7F01) + ['sw $t0, 32($zero)']
        a += load('$t1', 0xABCD)
        a += ['sh $t1, 32($zero)', 'lw $t2, 32($zero)'] + check('$t2', 0x80FFABCD)
        a += ['sh $t1, 34($zero)', 'lw $t2, 32($zero)'] + check('$t2', 0xABCDABCD)
    elif mnemonic in ('beq', 'bne'):
        a += load('$t0', 4) + load('$t1', 4) + load('$t2', 5)
        taken_rs, taken_rt, false_rs, false_rt = (
            ('$t0', '$t1', '$t0', '$t2') if mnemonic == 'beq'
            else ('$t0', '$t2', '$t0', '$t1')
        )
        a += [f'{mnemonic} {taken_rs}, {taken_rt}, branch_taken',
              'j fail', 'branch_taken:',
              f'{mnemonic} {false_rs}, {false_rt}, fail']
    elif mnemonic in ('bltz','bgez','blez','bgtz'):
        true_value, false_value = {
            'bltz': (-1, 0), 'bgez': (0, -1),
            'blez': (0, 1), 'bgtz': (1, -1),
        }[mnemonic]
        a += load('$t0', true_value)
        a += [f'{mnemonic} $t0, branch_taken', 'j fail', 'branch_taken:']
        a += load('$t0', false_value)
        a += [f'{mnemonic} $t0, fail']
    elif mnemonic == 'j':
        a += ['j jump_ok', 'j fail', 'jump_ok:']
    elif mnemonic == 'jr':
        a += ['ori $t0, $zero, jr_dest', 'jr $t0', 'j fail', 'jr_dest:']
    elif mnemonic == 'jal':
        a += [
            'jal func_jal', 'return_jal:',
            'ori $t3, $zero, return_jal',
            'bne $ra, $t3, fail',
            'j after_jal',
            'func_jal:', 'ori $t2, $zero, 0x1234', 'jr $ra',
            'after_jal:',
        ] + check('$t2', 0x1234)
    elif mnemonic == 'jalr':
        a += [
            'ori $t0, $zero, jalr_dest',
            'jalr $s0, $t0', 'return_jalr:',
            'ori $t3, $zero, return_jalr',
            'bne $s0, $t3, fail',
            'j after_jalr',
            'jalr_dest:', 'ori $t2, $zero, 0x1234', 'jr $s0',
            'after_jalr:',
        ] + check('$t2', 0x1234)
        a += [
            'ori $t0, $zero, jalr_dest2',
            'jalr $t0', 'return_jalr2:',
            'ori $t3, $zero, return_jalr2',
            'bne $ra, $t3, fail',
            'j after_jalr2',
            'jalr_dest2:', 'ori $t2, $zero, 0x5678', 'jr $ra',
            'after_jalr2:',
        ] + check('$t2', 0x5678)
    elif mnemonic == 'mult':
        for x, y, hi, lo in [
            (-7, 9, 0xFFFFFFFF, 0xFFFFFFC1),
            (0x80000000, -1, 0, 0x80000000),
            (0x7FFFFFFF, 0x7FFFFFFF, 0x3FFFFFFF, 1),
            (0, -1, 0, 0),
        ]:
            a += load('$t0', x) + load('$t1', y)
            a += ['mult $t0, $t1', 'mfhi $t2'] + check('$t2', hi)
            a += ['mflo $t2'] + check('$t2', lo)
    elif mnemonic == 'multu':
        for x, y, hi, lo in [
            (0xFFFFFFFF, 2, 1, 0xFFFFFFFE),
            (0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFE, 1),
            (0x80000000, 0x80000000, 0x40000000, 0),
            (0xFFFFFFFF, 0, 0, 0),
        ]:
            a += load('$t0', x) + load('$t1', y)
            a += ['multu $t0, $t1', 'mfhi $t2'] + check('$t2', hi)
            a += ['mflo $t2'] + check('$t2', lo)
    elif mnemonic in ('mfhi','mflo'):
        move = 'mthi' if mnemonic == 'mfhi' else 'mtlo'
        for value in (0x12345678, 0xFFFFFFFF, 0):
            a += load('$t0', value)
            a += [f'{move} $t0', f'{mnemonic} $t2'] + check('$t2', value)
    elif mnemonic == 'mthi':
        a += load('$t1', 0x55AA00FF) + ['mtlo $t1']
        for val in (0x12345678, -1):
            a += load('$t0', val) + ['mthi $t0', 'mfhi $t2'] + check('$t2', val)
        a += ['mflo $t2'] + check('$t2', 0x55AA00FF)
    elif mnemonic == 'mtlo':
        a += load('$t1', 0x55AA00FF) + ['mthi $t1']
        for val in (0x12345678, -1):
            a += load('$t0', val) + ['mtlo $t0', 'mflo $t2'] + check('$t2', val)
        a += ['mfhi $t2'] + check('$t2', 0x55AA00FF)
    else:
        raise AssertionError(f'Sem gerador: {mnemonic}')

    a += [
        'ori $t7, $zero, 1',
        'sw $t7, 252($zero)',
        'pass_loop:', 'j pass_loop',
        'fail:',
        'ori $t7, $zero, 2',
        'sw $t7, 252($zero)',
        'fail_loop:', 'j fail_loop',
    ]
    return a

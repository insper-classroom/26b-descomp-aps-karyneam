"""48 testes cocotb identificados por instrucao do MIPS (C+C++B+B+).

Cada teste reinicia a CPU, executa o programa real em ROM e compara, ciclo
por ciclo, a instrucao, PC, resultado da ULA e assinatura com um modelo
funcional independente que acompanha registradores, HI/LO e RAM byte a byte.

Os testes NAO dependem de acesso aos registradores internos do simulador.
Execucao: make -C test TOPLEVEL=mips_word_toplevel MODULE=test_mips_instructions
"""
from collections import Counter
from pathlib import Path
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mips_reference import MipsReference, EXPECTED, BRANCHES

MAX_STEPS = 850


async def run_reference_test(dut, focus):
    ref = MipsReference()
    counts = Counter()
    dut.enable.value = 0
    dut.reset.value = 1
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    await Timer(12, units='ns')
    assert int(dut.debug_pc.value) == 0, 'PC nao zerou no reset'
    assert int(dut.debug_signature.value) == 0, 'Assinatura nao zerou no reset'
    dut.reset.value = 0
    dut.enable.value = 1

    for cycle in range(MAX_STEPS):
        # Dá tempo para o sinal combinacional da ROM/ULA estabilizar.
        await Timer(1, units='ns')
        pc = ref.pc
        assert int(dut.debug_pc.value) == pc, (
            f'{focus}: PC na entrada do ciclo {cycle} esperado={pc:08X} '
            f'obtido={int(dut.debug_pc.value):08X}'
        )
        expected_word = ref.program[pc // 4]
        assert int(dut.debug_instruction.value) == expected_word, (
            f'{focus}: ROM no PC={pc:08X} esperado={expected_word:08X} '
            f'obtido={int(dut.debug_instruction.value):08X}'
        )
        result = ref.step()
        assert int(dut.debug_alu_result.value) == result.alu, (
            f'{focus}: ULA em {result.mnemonic}, PC={pc:08X}: '
            f'esperado=0x{result.alu:08X} obtido=0x{int(dut.debug_alu_result.value):08X}'
        )
        counts[result.mnemonic] += 1
        await RisingEdge(dut.clk)
        await Timer(1, units='ns')
        assert int(dut.debug_pc.value) == result.next_pc, (
            f'{focus}: PC apos {result.mnemonic} em {pc:08X}: '
            f'esperado={result.next_pc:08X} obtido={int(dut.debug_pc.value):08X}'
        )
        assert int(dut.debug_signature.value) == result.signature, (
            f'{focus}: assinatura divergente apos {result.mnemonic} em {pc:08X}: '
            f'esperado={result.signature} obtido={int(dut.debug_signature.value)}'
        )
        assert result.signature != 2, f'{focus}: autoteste alcançou FAIL apos {result.mnemonic}'
        if result.signature == 1:
            break
    else:
        assert False, f'{focus}: programa excedeu {MAX_STEPS} instrucoes sem terminar'

    # O teste com foco em uma instrucao so pode passar se ELA foi executada
    # e todo o programa, incluindo as verificacoes de resultados, passou.
    assert counts[focus] > 0, f'{focus}: a instrucao nao foi executada'
    assert set(counts) == EXPECTED, f'{focus}: faltaram {sorted(EXPECTED - set(counts))}'
    if focus in BRANCHES:
        assert ref.branches[focus]['taken'] > 0, f'{focus}: faltou branch tomado'
        assert ref.branches[focus]['not_taken'] > 0, f'{focus}: faltou branch nao tomado'
    if focus in ('mult', 'multu', 'mfhi', 'mflo', 'mthi', 'mtlo'):
        assert ref.hi == 0 and ref.lo == 0, f'{focus}: HI/LO final inesperado'
    if focus in ('lw', 'sw', 'lb', 'lbu', 'lh', 'lhu', 'sb', 'sh'):
        assert ref.read(64, 4) == 0x00EF0000, f'{focus}: resultado acumulado na RAM incorreto'
    dut._log.info('PASS test_%s: %d ocorrencias, %d passos, 48/48 mnemônicos',
                  focus, counts[focus], cycle+1)


def _make_test(mnemonic):
    async def test_one_instruction(dut):
        await run_reference_test(dut, mnemonic)
    test_one_instruction.__name__ = f'test_{mnemonic}'
    test_one_instruction.__qualname__ = f'test_{mnemonic}'
    return cocotb.test()(test_one_instruction)


# Registra 48 casos distintos no runner do cocotb: test_add, test_addi, etc.
for _instruction in sorted(EXPECTED):
    globals()[f'test_{_instruction}'] = _make_test(_instruction)

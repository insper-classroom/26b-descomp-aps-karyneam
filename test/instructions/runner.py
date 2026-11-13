"""Driver comum das 48 simulacoes cocotb, cada uma com ROM propria."""
from pathlib import Path
import sys
from collections import Counter

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mips_reference import MipsReference, BRANCHES
from instructions.cases import ALL

ROM = Path(__file__).resolve().parents[1] / 'generated' / 'case.hex'


async def run_case(dut, mnemonic):
    assert mnemonic in ALL
    words = [int(line, 16) for line in ROM.read_text(encoding='utf-8').split()]
    ref = MipsReference(program=words)
    visited = Counter()
    # A CPU agora tem entradas MMIO e de selecao de banco. Nos testes
    # individuais, sempre utilizar banco 0 da ROM temporaria.
    dut.rom_bank.value = 0
    dut.io_read_data.value = 0
    dut.enable.value = 0
    dut.reset.value = 1
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    await Timer(12, units='ns')
    assert int(dut.debug_pc.value) == 0, 'Reset nao zerou PC'
    assert int(dut.debug_signature.value) == 0, 'Reset nao zerou assinatura'
    dut.reset.value = 0
    dut.enable.value = 1

    max_steps = len(words) + 10
    for cycle in range(max_steps):
        await Timer(1, units='ns')
        pc = ref.pc
        assert int(dut.debug_pc.value) == pc, (
            f'{mnemonic}: ciclo {cycle}, PC esperado={pc:08X}, '
            f'RTL={int(dut.debug_pc.value):08X}')
        expected_word = ref.program[pc // 4]
        assert int(dut.debug_instruction.value) == expected_word, (
            f'{mnemonic}: ROM PC={pc:08X} esperada={expected_word:08X}, '
            f'RTL={int(dut.debug_instruction.value):08X}')
        step = ref.step()
        assert int(dut.debug_alu_result.value) == step.alu, (
            f'{mnemonic}: ALU em {step.mnemonic} PC={pc:08X}, '
            f'esperado={step.alu:08X}, RTL={int(dut.debug_alu_result.value):08X}')
        visited[step.mnemonic] += 1

        # Confere também que enable=0 nao avanca PC nem altera HI/LO em MULTU.
        if step.mnemonic == 'multu' and mnemonic == 'multu' and visited['multu'] == 1:
            dut.enable.value = 0
            for _ in range(2):
                await RisingEdge(dut.clk)
                await Timer(1, units='ns')
                assert int(dut.debug_pc.value) == pc, 'PC mudou com enable=0'
                assert int(dut.debug_signature.value) == 0
            dut.enable.value = 1
        await RisingEdge(dut.clk)
        await Timer(1, units='ns')
        assert int(dut.debug_pc.value) == step.next_pc, (
            f'{mnemonic}: PC apos {step.mnemonic} no endereco {pc:08X}; '
            f'esperado={step.next_pc:08X}; RTL={int(dut.debug_pc.value):08X}')
        assert int(dut.debug_signature.value) == step.signature, (
            f'{mnemonic}: assinatura diferente no ciclo {cycle}; '
            f'esperado={step.signature}, RTL={int(dut.debug_signature.value)}')
        assert step.signature != 2, f'{mnemonic}: programa foi para FAIL em {pc:08X}'
        if step.signature == 1:
            break
    else:
        assert False, f'{mnemonic}: programa nao concluiu em {max_steps} ciclos'

    assert visited[mnemonic] > 0, f'{mnemonic}: instrução alvo nao executada'
    if mnemonic in BRANCHES:
        assert ref.branches[mnemonic]['taken'] >= 1, f'{mnemonic}: sem branch tomado'
        assert ref.branches[mnemonic]['not_taken'] >= 1, f'{mnemonic}: sem branch nao tomado'
    dut._log.info('PASS %s: %d ocorrencias, %d ciclos, ROM exclusiva',
                  mnemonic.upper(), visited[mnemonic], cycle + 1)

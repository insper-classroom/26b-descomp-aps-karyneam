"""Teste integrado acumulativo cocotb: C (28) + C+ (6) + B (8) + B+ (6).

Este teste roda o programa MIPS na CPU VHDL e so aceita PASS quando
as verificacoes dentro do proprio Assembly terminam com status 1.
Testes individuais de cada instrucao ficam para a etapa final da APS.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

FUNCT = {0: 'sll', 2: 'srl', 3: 'sra', 4: 'sllv', 6: 'srlv',
         7: 'srav', 16: 'mfhi', 17: 'mthi', 18: 'mflo', 19: 'mtlo',
         24: 'mult', 25: 'multu', 8: 'jr', 9: 'jalr', 32: 'add', 33: 'addu',
         34: 'sub', 35: 'subu', 36: 'and', 37: 'or', 38: 'xor',
         39: 'nor', 42: 'slt', 43: 'sltu'}
OP = {2: 'j', 3: 'jal', 4: 'beq', 5: 'bne', 6: 'blez',
      7: 'bgtz', 8: 'addi', 9: 'addiu', 10: 'slti',
      11: 'sltiu', 12: 'andi', 13: 'ori', 14: 'xori',
      15: 'lui', 32: 'lb', 33: 'lh', 35: 'lw',
      36: 'lbu', 37: 'lhu', 40: 'sb', 41: 'sh', 43: 'sw'}
EXPECTED = set(FUNCT.values()) | set(OP.values()) | {'bltz', 'bgez'}


def decode(word):
    op = (word >> 26) & 63
    if op == 0:
        return FUNCT.get(word & 63, 'unknown R')
    if op == 1:
        return {0: 'bltz', 1: 'bgez'}.get((word >> 16) & 31, 'unknown REGIMM')
    return OP.get(op, 'unknown opcode')


@cocotb.test()
async def programa_c_cplus_b_bplus(dut):
    dut.reset.value = 1
    dut.enable.value = 0
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())
    await Timer(12, units='ns')
    dut.reset.value = 0
    await Timer(1, units='ns')
    assert int(dut.debug_pc.value) == 0
    assert int(dut.debug_signature.value) == 0

    dut.enable.value = 1
    await Timer(1, units='ns')
    visited = set()
    stalled_mult = False
    for cycle in range(850):
        pc_before = int(dut.debug_pc.value)
        instr = int(dut.debug_instruction.value)
        name = decode(instr)
        assert not name.startswith('unknown'), (f'Instrucao invalida {instr:08X} no PC={pc_before:08X}')
        visited.add(name)
        # A instrucao multu deve ficar parada enquanto enable=0.
        # As verificacoes de HI/LO feitas em Assembly precisam continuar passando.
        if name == 'multu' and not stalled_mult:
            stalled_mult = True
            dut.enable.value = 0
            for _ in range(3):
                await RisingEdge(dut.clk)
                await Timer(1, units='ns')
                assert int(dut.debug_pc.value) == pc_before, 'PC mudou com enable=0'
                assert int(dut.debug_signature.value) == 0
            dut.enable.value = 1
            await Timer(1, units='ns')
        await RisingEdge(dut.clk)
        await Timer(1, units='ns')
        signature = int(dut.debug_signature.value)
        assert signature != 2, (f'FAIL no programa C+C++B+B+ apos {cycle+1} passos; '
                                f'PC anterior={pc_before:08X}, instrucao={name}')
        if signature == 1:
            break
    else:
        assert False, 'Programa nao concluiu em 850 ciclos'

    assert visited == EXPECTED, f'Faltaram instrucoes: {sorted(EXPECTED - visited)}'
    assert len(visited) == 48
    assert stalled_mult, "multu nao foi testado com pausa"
    dut._log.info('PASS: %d ciclos, %d instrucoes distintas (C+C++B+B+)', cycle+1, len(visited))

    # Clock-enable parado nao pode mudar PC nem assinatura.
    dut.enable.value = 0
    await Timer(1, units='ns')
    stopped_pc = int(dut.debug_pc.value)
    for _ in range(3):
        await RisingEdge(dut.clk)
        await Timer(1, units='ns')
        assert int(dut.debug_pc.value) == stopped_pc
        assert int(dut.debug_signature.value) == 1

    dut.reset.value = 1
    await Timer(2, units='ns')
    assert int(dut.debug_pc.value) == 0
    assert int(dut.debug_signature.value) == 0

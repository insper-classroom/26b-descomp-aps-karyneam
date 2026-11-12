"""Teste cocotb independente da instrucao J."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_j(dut):
    await run_case(dut, 'j')

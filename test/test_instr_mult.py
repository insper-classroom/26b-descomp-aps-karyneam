"""Teste cocotb independente da instrucao MULT."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_mult(dut):
    await run_case(dut, 'mult')

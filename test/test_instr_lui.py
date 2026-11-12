"""Teste cocotb independente da instrucao LUI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_lui(dut):
    await run_case(dut, 'lui')

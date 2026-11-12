"""Teste cocotb independente da instrucao LH."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_lh(dut):
    await run_case(dut, 'lh')

"""Teste cocotb independente da instrucao ANDI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_andi(dut):
    await run_case(dut, 'andi')

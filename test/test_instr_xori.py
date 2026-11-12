"""Teste cocotb independente da instrucao XORI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_xori(dut):
    await run_case(dut, 'xori')

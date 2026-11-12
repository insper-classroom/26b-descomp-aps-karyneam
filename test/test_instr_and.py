"""Teste cocotb independente da instrucao AND."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_and(dut):
    await run_case(dut, 'and')

"""Teste cocotb independente da instrucao OR."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_or(dut):
    await run_case(dut, 'or')

"""Teste cocotb independente da instrucao SW."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sw(dut):
    await run_case(dut, 'sw')

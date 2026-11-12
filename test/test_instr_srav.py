"""Teste cocotb independente da instrucao SRAV."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_srav(dut):
    await run_case(dut, 'srav')

"""Teste cocotb independente da instrucao MFLO."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_mflo(dut):
    await run_case(dut, 'mflo')

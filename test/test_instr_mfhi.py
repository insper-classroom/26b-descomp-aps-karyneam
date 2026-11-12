"""Teste cocotb independente da instrucao MFHI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_mfhi(dut):
    await run_case(dut, 'mfhi')

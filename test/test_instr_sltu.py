"""Teste cocotb independente da instrucao SLTU."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sltu(dut):
    await run_case(dut, 'sltu')

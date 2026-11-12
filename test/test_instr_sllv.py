"""Teste cocotb independente da instrucao SLLV."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sllv(dut):
    await run_case(dut, 'sllv')

"""Teste cocotb independente da instrucao SRLV."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_srlv(dut):
    await run_case(dut, 'srlv')

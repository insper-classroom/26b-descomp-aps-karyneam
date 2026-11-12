"""Teste cocotb independente da instrucao LW."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_lw(dut):
    await run_case(dut, 'lw')

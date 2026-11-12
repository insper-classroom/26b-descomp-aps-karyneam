"""Teste cocotb independente da instrucao SLTI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_slti(dut):
    await run_case(dut, 'slti')

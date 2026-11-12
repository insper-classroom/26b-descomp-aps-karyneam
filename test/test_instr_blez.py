"""Teste cocotb independente da instrucao BLEZ."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_blez(dut):
    await run_case(dut, 'blez')

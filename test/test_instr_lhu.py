"""Teste cocotb independente da instrucao LHU."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_lhu(dut):
    await run_case(dut, 'lhu')

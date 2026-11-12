"""Teste cocotb independente da instrucao LB."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_lb(dut):
    await run_case(dut, 'lb')

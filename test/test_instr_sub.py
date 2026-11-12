"""Teste cocotb independente da instrucao SUB."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sub(dut):
    await run_case(dut, 'sub')

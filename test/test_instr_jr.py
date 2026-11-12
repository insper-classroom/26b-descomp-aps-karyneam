"""Teste cocotb independente da instrucao JR."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_jr(dut):
    await run_case(dut, 'jr')

"""Teste cocotb independente da instrucao ADD."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_add(dut):
    await run_case(dut, 'add')

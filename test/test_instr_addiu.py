"""Teste cocotb independente da instrucao ADDIU."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_addiu(dut):
    await run_case(dut, 'addiu')

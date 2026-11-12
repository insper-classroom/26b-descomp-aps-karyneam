"""Teste cocotb independente da instrucao ADDI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_addi(dut):
    await run_case(dut, 'addi')

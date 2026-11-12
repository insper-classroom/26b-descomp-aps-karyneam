"""Teste cocotb independente da instrucao SLTIU."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sltiu(dut):
    await run_case(dut, 'sltiu')

"""Teste cocotb independente da instrucao ADDU."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_addu(dut):
    await run_case(dut, 'addu')

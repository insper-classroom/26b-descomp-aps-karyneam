"""Teste cocotb independente da instrucao SUBU."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_subu(dut):
    await run_case(dut, 'subu')

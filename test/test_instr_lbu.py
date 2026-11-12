"""Teste cocotb independente da instrucao LBU."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_lbu(dut):
    await run_case(dut, 'lbu')

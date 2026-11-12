"""Teste cocotb independente da instrucao BLTZ."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_bltz(dut):
    await run_case(dut, 'bltz')

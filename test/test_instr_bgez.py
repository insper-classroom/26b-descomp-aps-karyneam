"""Teste cocotb independente da instrucao BGEZ."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_bgez(dut):
    await run_case(dut, 'bgez')

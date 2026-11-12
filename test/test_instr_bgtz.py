"""Teste cocotb independente da instrucao BGTZ."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_bgtz(dut):
    await run_case(dut, 'bgtz')

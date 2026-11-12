"""Teste cocotb independente da instrucao ORI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_ori(dut):
    await run_case(dut, 'ori')

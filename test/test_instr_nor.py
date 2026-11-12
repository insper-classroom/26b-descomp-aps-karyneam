"""Teste cocotb independente da instrucao NOR."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_nor(dut):
    await run_case(dut, 'nor')

"""Teste cocotb independente da instrucao MTLO."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_mtlo(dut):
    await run_case(dut, 'mtlo')

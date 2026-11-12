"""Teste cocotb independente da instrucao SLT."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_slt(dut):
    await run_case(dut, 'slt')

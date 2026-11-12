"""Teste cocotb independente da instrucao BNE."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_bne(dut):
    await run_case(dut, 'bne')

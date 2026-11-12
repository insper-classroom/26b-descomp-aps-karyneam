"""Teste cocotb independente da instrucao JALR."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_jalr(dut):
    await run_case(dut, 'jalr')

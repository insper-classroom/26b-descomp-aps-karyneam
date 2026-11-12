"""Teste cocotb independente da instrucao SRA."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sra(dut):
    await run_case(dut, 'sra')

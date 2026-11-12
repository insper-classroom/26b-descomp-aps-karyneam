"""Teste cocotb independente da instrucao SB."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sb(dut):
    await run_case(dut, 'sb')

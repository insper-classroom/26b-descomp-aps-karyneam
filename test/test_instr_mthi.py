"""Teste cocotb independente da instrucao MTHI."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_mthi(dut):
    await run_case(dut, 'mthi')

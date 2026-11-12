"""Teste cocotb independente da instrucao SRL."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_srl(dut):
    await run_case(dut, 'srl')

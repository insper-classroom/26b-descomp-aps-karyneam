"""Teste cocotb independente da instrucao BEQ."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_beq(dut):
    await run_case(dut, 'beq')

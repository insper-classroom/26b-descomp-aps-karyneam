"""Teste cocotb independente da instrucao SLL."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sll(dut):
    await run_case(dut, 'sll')

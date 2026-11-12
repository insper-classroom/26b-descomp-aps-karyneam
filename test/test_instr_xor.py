"""Teste cocotb independente da instrucao XOR."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_xor(dut):
    await run_case(dut, 'xor')

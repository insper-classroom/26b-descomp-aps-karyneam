"""Teste cocotb independente da instrucao SH."""
import cocotb
from instructions.runner import run_case


@cocotb.test()
async def verificar_sh(dut):
    await run_case(dut, 'sh')

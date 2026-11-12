"""Verifica os bytes da ROM gerada pelo autoteste acumulativo C+C++B+B+."""
from pathlib import Path
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_mips_rom(dut):
    root = Path(__file__).resolve().parents[1]
    expected = [int(line, 16) for line in
                (root / 'programs/conceito_bplus_selftest.hex').read_text().splitlines()]
    for address in range(2 ** len(dut.addr)):
        dut.addr.value = address
        await Timer(1, units='ns')
        value = int(dut.data.value)
        check = expected[address] if address < len(expected) else 0
        assert value == check, (f'ROM[{address}] esperado={check:08X} '
                                f'valor={value:08X}')

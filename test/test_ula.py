import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_ula_soma(dut):
    # Testa operacao de Soma (control = 010)

    dut.A.value = 2
    dut.B.value = 3
    dut.control.value = 0b010

    await Timer(10, unit="ns")

    res = int(dut.result.value)

    dut._log.info(
        f"Soma: A=2, B=3 -> Result={res}, "
        f"Zero={int(dut.flag_zero.value)}"
    )

    assert res == 5, f"Erro: esperado 5, obtido {res}"
    assert int(dut.flag_zero.value) == 0, \
        "Flag zero deveria ser 0"


@cocotb.test()
async def test_ula_zero_flag(dut):
    # Testa se a flag Zero ativa quando o resultado de 32 bits eh zero

    dut.A.value = 0
    dut.B.value = 0
    dut.control.value = 0b010  # 0 + 0

    await Timer(10, unit="ns")

    res = int(dut.result.value)

    dut._log.info(
        f"Zero Flag Test: Result={res}, "
        f"Zero={int(dut.flag_zero.value)}"
    )

    assert res == 0, f"Resultado deveria ser 0, obtido {res}"
    assert int(dut.flag_zero.value) == 1, \
        "Flag zero deveria ser 1"


@cocotb.test()
async def test_ula_sub(dut):
    # Testa operacao de Subtracao (control = 011)

    dut.A.value = 10
    dut.B.value = 3
    dut.control.value = 0b011

    await Timer(10, unit="ns")

    res = int(dut.result.value)

    dut._log.info(f"Subtracao: 10 - 3 = {res}")

    assert res == 7, f"Erro: esperado 7, obtido {res}"


@cocotb.test()
async def test_ula_and(dut):
    # Testa operacao AND (control = 100)

    dut.A.value = 0b1100
    dut.B.value = 0b1010
    dut.control.value = 0b100

    await Timer(10, unit="ns")

    res = int(dut.result.value)

    dut._log.info(f"AND: 1100 AND 1010 = {res}")

    assert res == 0b1000, \
        f"Erro no AND: esperado 8, obtido {res}"


@cocotb.test()
async def test_ula_or(dut):
    # Testa operacao OR (control = 101)

    dut.A.value = 0b1100
    dut.B.value = 0b1010
    dut.control.value = 0b101

    await Timer(10, unit="ns")

    res = int(dut.result.value)

    dut._log.info(f"OR: 1100 OR 1010 = {res}")

    assert res == 0b1110, \
        f"Erro no OR: esperado 14, obtido {res}"


@cocotb.test()
async def test_ula_not(dut):
    # Testa operacao NOT A (control = 110)

    dut.A.value = 0x00000000
    dut.B.value = 0
    dut.control.value = 0b110

    await Timer(10, unit="ns")

    res = int(dut.result.value)

    dut._log.info(f"NOT: NOT 0x00000000 = 0x{res:08X}")

    assert res == 0xFFFFFFFF, \
        f"Erro no NOT: esperado 0xFFFFFFFF, obtido 0x{res:08X}"


@cocotb.test()
async def test_ula_xor(dut):
    # Testa operacao XOR (control = 111)

    dut.A.value = 0b1100
    dut.B.value = 0b1010
    dut.control.value = 0b111

    await Timer(10, unit="ns")

    res = int(dut.result.value)

    dut._log.info(f"XOR: 1100 XOR 1010 = {res}")

    assert res == 0b0110, \
        f"Erro no XOR: esperado 6, obtido {res}"


@cocotb.test()
async def test_ula_negative_flag(dut):
    # Testa flag negativa usando 0 - 1 = -1

    dut.A.value = 0
    dut.B.value = 1
    dut.control.value = 0b011

    await Timer(10, unit="ns")

    res = int(dut.result.value)
    neg = int(dut.flag_neg.value)

    dut._log.info(
        f"Negative Flag Test: Result=0x{res:08X}, Neg={neg}"
    )

    assert res == 0xFFFFFFFF, \
        f"Esperado 0xFFFFFFFF (-1), obtido 0x{res:08X}"

    assert neg == 1, \
        "Flag negativa deveria ser 1"


@cocotb.test()
async def test_ula_overflow(dut):
    # 0x7FFFFFFF + 1 causa overflow signed de 32 bits

    dut.A.value = 0x7FFFFFFF
    dut.B.value = 1
    dut.control.value = 0b010

    await Timer(10, unit="ns")

    res = int(dut.result.value)
    ovf = int(dut.flag_overflow.value)

    dut._log.info(
        f"Overflow Test: Result=0x{res:08X}, Overflow={ovf}"
    )

    assert res == 0x80000000, \
        f"Esperado 0x80000000, obtido 0x{res:08X}"

    assert ovf == 1, \
        "Flag overflow deveria ser 1"
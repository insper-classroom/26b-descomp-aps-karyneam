import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset_reg_file(dut):
    #Reseta o banco de registradores.
    dut.rst.value = 1
    dut.W_en.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.rst.value = 0


async def write_register(dut, addr, data):
    #Escreve data no registrador addr.
    dut.W_addr.value = addr
    dut.W_data.value = data
    dut.W_en.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.W_en.value = 0


@cocotb.test()
async def test_reg_file_reset(dut):
    #Testa se o reset coloca os registradores em zero.

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.A_addr.value = 5
    dut.B_addr.value = 10

    await reset_reg_file(dut)

    await Timer(1, unit="ns")

    assert int(dut.A_data.value) == 0
    assert int(dut.B_data.value) == 0

    dut._log.info("RESET OK: registradores possuem valor 0")


@cocotb.test()
async def test_reg_file_write_read(dut):
    #Testa escrita e leitura de um registrador.

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_reg_file(dut)

    # Escreve 42 no registrador $5
    await write_register(dut, 5, 42)

    # Lê $5 pela porta A
    dut.A_addr.value = 5

    await Timer(1, unit="ns")

    result = int(dut.A_data.value)

    dut._log.info(f"R5 = {result}")

    assert result == 42, f"Esperado R5=42, obtido {result}"


@cocotb.test()
async def test_reg_file_dual_read(dut):
    #Testa as duas portas de leitura simultaneamente.

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_reg_file(dut)

    # R5 = 100
    await write_register(dut, 5, 100)

    # R10 = 200
    await write_register(dut, 10, 200)

    # Lê os dois ao mesmo tempo
    dut.A_addr.value = 5
    dut.B_addr.value = 10

    await Timer(1, unit="ns")

    a = int(dut.A_data.value)
    b = int(dut.B_data.value)

    dut._log.info(f"A_data (R5)={a}, B_data (R10)={b}")

    assert a == 100, f"Esperado A_data=100, obtido {a}"
    assert b == 200, f"Esperado B_data=200, obtido {b}"


@cocotb.test()
async def test_reg_file_write_enable(dut):
    #Testa se W_en=0 impede a escrita.

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_reg_file(dut)

    # Primeiro R7 = 55
    await write_register(dut, 7, 55)

    # Tenta escrever 99 com W_en = 0
    dut.W_addr.value = 7
    dut.W_data.value = 99
    dut.W_en.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.A_addr.value = 7

    await Timer(1, unit="ns")

    result = int(dut.A_data.value)

    dut._log.info(f"W_en=0: R7={result}")

    assert result == 55, (
        f"W_en=0 deveria impedir escrita. "
        f"Esperado 55, obtido {result}"
    )


@cocotb.test()
async def test_reg_file_r0(dut):
    #Testa se o registrador $0 permanece sempre zero.

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_reg_file(dut)

    # Tenta escrever em $0
    await write_register(dut, 0, 12345)

    # Lê $0 pelas duas portas
    dut.A_addr.value = 0
    dut.B_addr.value = 0

    await Timer(1, unit="ns")

    a = int(dut.A_data.value)
    b = int(dut.B_data.value)

    dut._log.info(f"R0: A_data={a}, B_data={b}")

    assert a == 0, f"R0 deve ser sempre 0, mas A_data={a}"
    assert b == 0, f"R0 deve ser sempre 0, mas B_data={b}"


@cocotb.test()
async def test_reg_file_overwrite(dut):
    #Testa sobrescrita de um registrador.

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_reg_file(dut)

    # Primeira escrita
    await write_register(dut, 15, 100)

    # Sobrescreve R15
    await write_register(dut, 15, 999)

    dut.A_addr.value = 15

    await Timer(1, unit="ns")

    result = int(dut.A_data.value)

    dut._log.info(f"R15 apos sobrescrita = {result}")

    assert result == 999, f"Esperado R15=999, obtido {result}"
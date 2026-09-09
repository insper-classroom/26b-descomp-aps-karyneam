import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_ula_soma(dut):
    #Testa operacao de Soma (control = 0000)
    dut.A.value = 2
    dut.B.value = 3
    dut.control.value = 0b0000
    
    await Timer(10, unit="ns")
    
    res = int(dut.result.value)
    dut._log.info(f"Soma: A=2, B=3 -> Result={res}, Zero={int(dut.flag_zero.value)}")
    assert res == 5, f"Erro: esperado 5, obtido {res}"
    assert int(dut.flag_zero.value) == 0, "Flag zero deveria ser 0"


@cocotb.test()
async def test_ula_zero_flag(dut):
    #Testa se a flag de Zero ativa quando os 3 bits finais sao 0
    dut.A.value = 0
    dut.B.value = 0
    dut.control.value = 0b0000
    
    await Timer(10, unit="ns")
    
    res = int(dut.result.value)
    dut._log.info(f"Zero Flag Test: Result={res}, Zero={int(dut.flag_zero.value)}")
    assert res == 0, f"Resultado deveria ser 0, obtido {res}"
    assert int(dut.flag_zero.value) == 1, "Flag zero deveria ser 1"


@cocotb.test()
async def test_ula_and(dut):
    #Testa operacao AND logico (control = 0010)
    dut.A.value = 0b1100
    dut.B.value = 0b1010
    dut.control.value = 0b0010  
    
    await Timer(10, unit="ns")

    res = int(dut.result.value)
    dut._log.info(f"AND: Result={res}")
    assert res == 8, f"Erro no AND: esperado 8, obtido {res}"


@cocotb.test()
async def test_ula_xor(dut):
    #Testa operacao XOR logico (control = 0100)
    dut.A.value = 0b1100
    dut.B.value = 0b1010
    dut.control.value = 0b0100  
    
    await Timer(10, unit="ns")
    
    res = int(dut.result.value)
    dut._log.info(f"XOR: Result={res}")
    assert res == 6, f"Erro no XOR: esperado 6, obtido {res}"
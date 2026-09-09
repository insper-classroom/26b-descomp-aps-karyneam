import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_ula_soma(dut):
    #Testa operacao de Soma (control = 0)
    dut.A.value = 15
    dut.B.value = 25
    dut.control.value = 0b0000  
    
    await Timer(2, units="ns")
    
    dut._log.info(f"Soma: A={dut.A.value}, B={dut.B.value} -> Result={dut.result.value.to_unsigned()}")
    assert dut.result.value.to_unsigned() == 40, f"Erro: esperado 40, obtido {dut.result.value.to_unsigned()}"
    assert dut.flag_zero.value == 0, "Flag zero deveria ser 0"


@cocotb.test()
async def test_ula_zero_flag(dut):
    #Testa se a flag de Zero ativa corretamente
    dut.A.value = 0
    dut.B.value = 0
    dut.control.value = 0b0000
    
    await Timer(2, units="ns")
    
    dut._log.info(f"Zero Flag Test: Result={dut.result.value.to_unsigned()}, Zero={dut.flag_zero.value}")
    assert dut.result.value.to_unsigned() == 0, "Resultado deveria ser 0"
    assert dut.flag_zero.value == 1, "Flag zero deveria ser 1"


@cocotb.test()
async def test_ula_and(dut):
    #Testa operacao AND logico (control = 4)
    dut.A.value = 0b1100
    dut.B.value = 0b1010
    dut.control.value = 0b0100  # bits 2..0 = 100
    
    await Timer(2, units="ns")
    
    dut._log.info(f"AND: Result={dut.result.value.to_unsigned()}")
    assert dut.result.value.to_unsigned() == 8, f"Erro no AND: esperado 8, obtido {dut.result.value.to_unsigned()}"


@cocotb.test()
async def test_ula_xor(dut):
    #Testa operacao XOR logico (control = 7)
    dut.A.value = 0b1100
    dut.B.value = 0b1010
    dut.control.value = 0b0111  # bits 2..0 = 111
    
    await Timer(2, units="ns")
    
    dut._log.info(f"XOR: Result={dut.result.value.to_unsigned()}")
    assert dut.result.value.to_unsigned() == 6, f"Erro no XOR: esperado 6, obtido {dut.result.value.to_unsigned()}"
"""Testes cocotb das quatro lanes independentes da RAM C+.
Obs.: escrita eh por palavra indexada em addr[7:2]; os bits baixos
selecionam byte/halfword no PROCESSADOR, nao dentro da RAM.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, FallingEdge


@cocotb.test()
async def teste_rmw_e_little_endian(dut):
    dut.reset.value = 1
    dut.byte_we.value = 0
    dut.addr.value = 0x40
    dut.data_in.value = 0
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await Timer(3, units="ns")
    assert int(dut.data_out.value) == 0
    dut.reset.value = 0

    async def write(word, enables, address=0x40):
        # Alterar sinais depois da borda de descida evita corridas no simulador.
        await FallingEdge(dut.clk)
        dut.addr.value = address
        dut.data_in.value = word
        dut.byte_we.value = enables
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        dut.byte_we.value = 0
        return int(dut.data_out.value)

    assert await write(0x80FF7F01, 0b1111) == 0x80FF7F01
    # byte 1: low 8 bits de data_in precisa estar posicionado pelo MIPS.
    assert await write(0x0000A500, 0b0010) == 0x80FFA501
    assert await write(0, 0b0001) == 0x80FFA500
    assert await write(0x00A50000, 0b0100) == 0x80A5A500
    assert await write(0xA5000000, 0b1000) == 0xA5A5A500
    assert await write(0x0000BEEF, 0b0011) == 0xA5A5BEEF
    assert await write(0xBEEF0000, 0b1100) == 0xBEEFBEEF
    # Nenhuma escrita deve ocorrer quando byte_we=0000.
    assert await write(0xFFFFFFFF, 0b0000) == 0xBEEFBEEF
    # Outro indice de palavra nao pode ter sido modificado.
    dut.addr.value = 0x44
    await Timer(1, units="ns")
    assert int(dut.data_out.value) == 0
    assert await write(0x12345678, 0b1111, 0x44) == 0x12345678
    dut.addr.value = 0x40
    await Timer(1, units="ns")
    assert int(dut.data_out.value) == 0xBEEFBEEF

    # RESET limpa as quatro lanes.
    dut.reset.value = 1
    await Timer(2, units="ns")
    assert int(dut.data_out.value) == 0
    dut.addr.value = 0x44
    await Timer(1, units="ns")
    assert int(dut.data_out.value) == 0

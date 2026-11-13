"""Verifica os nove programas da ROM de producao, banco por banco.

O processador recebe o banco pelos switches SW4..SW1; cada banco
ocupa 512 palavras de 32 bits na ROM. Comparar somente com o autoteste B+
no endereco absoluto inteiro deixou de ser valido apos integrar as demos.
"""
from pathlib import Path

import cocotb
from cocotb.triggers import Timer

BANK_WORDS = 512
FILES = (
    'conceito_bplus_selftest.hex',
    'demo_01_soma_1_a_10.hex',
    'demo_02_fatorial_5.hex',
    'demo_03_logica_e_shifts.hex',
    'demo_04_bytes_halfwords.hex',
    'demo_05_fibonacci_8.hex',
    'demo_06_subrotinas.hex',
    'demo_07_comparacoes_branches.hex',
    'demo_08_jogo_da_velha.hex',
)


@cocotb.test()
async def verificar_todos_os_bancos_da_rom(dut):
    root = Path(__file__).resolve().parents[1]
    programs = root / 'programs'
    capacity = 2 ** len(dut.addr)
    assert capacity >= len(FILES) * BANK_WORDS, (
        f'ROM com {capacity} palavras, esperado ao menos {len(FILES) * BANK_WORDS}'
    )

    expected = [0] * capacity
    for bank, filename in enumerate(FILES):
        words = [int(word, 16) for word in (programs / filename).read_text(
            encoding='utf-8').split()]
        assert 0 < len(words) <= BANK_WORDS, f'Banco {bank}: tamanho invalido'
        first = bank * BANK_WORDS
        expected[first:first + len(words)] = words

    for addr, word in enumerate(expected):
        dut.addr.value = addr
        await Timer(1, units='ns')
        got = int(dut.data.value)
        assert got == word, (
            f'ROM banco={addr // BANK_WORDS} palavra={addr % BANK_WORDS}: '
            f'esperado=0x{word:08X}, recebido=0x{got:08X}'
        )
    dut._log.info('PASS: nove bancos de ROM, %d enderecos conferidos', capacity)

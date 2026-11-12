#!/usr/bin/env python3
"""Cria ROM VHDL e HEX temporarios para UM teste de instrucao.

Uso: python tools/build_instruction_test.py <mnemonico>
Gera arquivos apenas em test/generated/. Nao altera src/ nem programas
usados no Quartus ou nos autotestes integrados anteriores.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'test'))
sys.path.insert(0, str(ROOT / 'tools'))
from instructions.cases import ALL, case
import assemble_bplus

BASE = assemble_bplus.base
OUT = ROOT / 'test' / 'generated'


def assemble_program(mnemonic):
    lines = case(mnemonic)
    labels = {}
    code = []
    for i, source in enumerate(lines, 1):
        source = source.split('#', 1)[0].strip()
        while ':' in source:
            label, source = source.split(':', 1)
            label = label.strip()
            if not re.fullmatch(r'[A-Za-z_]\w*', label) or label in labels:
                raise ValueError(f'rotulo invalido/duplicado: {label}')
            labels[label] = len(code)
            source = source.strip()
        if source:
            code.append((i, source))
    if len(code) > 1024:
        raise ValueError('ROM excedeu 1024 palavras')
    words = []
    for pc, (lineno, source) in enumerate(code):
        try:
            words.append(BASE.assemble(source, pc, labels))
        except Exception as exc:
            raise ValueError(f'{mnemonic}: linha {lineno}: {source}: {exc}') from exc
    return code, words


def generate(mnemonic):
    if mnemonic not in ALL:
        raise ValueError(f'Instrucao invalida: {mnemonic}. Validas: {", ".join(ALL)}')
    code, words = assemble_program(mnemonic)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'case.hex').write_text(''.join(f'{w:08X}\n' for w in words), encoding='utf-8')
    body = '\n'.join(f'        tmp({idx}) := x"{word:08X}"; -- {line}'
                     for idx, ((_, line), word) in enumerate(zip(code, words)))
    vhdl = f'''library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ROM TEMPORARIA somente para cocotb: teste individual {mnemonic}
entity mips_rom is
    generic (dataWidth : natural := 32; addrWidth : natural := 10);
    port (addr : in std_logic_vector(addrWidth-1 downto 0);
          data : out std_logic_vector(dataWidth-1 downto 0));
end entity;
architecture bhv of mips_rom is
    type blocoMemoria is array(0 to 2**addrWidth-1) of
        std_logic_vector(dataWidth-1 downto 0);
    function initMemory return blocoMemoria is
        variable tmp : blocoMemoria := (others => (others => '0'));
    begin
{body}
        return tmp;
    end function;
    signal memROM : blocoMemoria := initMemory;
begin
    data <= memROM(to_integer(unsigned(addr)));
end architecture;
'''
    (OUT / 'mips_rom.vhd').write_text(vhdl, encoding='utf-8')
    (OUT / 'case.asm').write_text('\n'.join(line for _, line in code) + '\n', encoding='utf-8')
    print(f'Teste {mnemonic}: ROM com {len(words)} instrucoes; PASS=1 / FAIL=2')
    return words


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python tools/build_instruction_test.py <mnemonico>')
    generate(sys.argv[1])


if __name__ == '__main__':
    main()

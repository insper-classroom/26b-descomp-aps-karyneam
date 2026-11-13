#!/usr/bin/env python3
"""Gera os 8 bancos da ROM do MESMO quartus/top_level.qpf.
Banco 0 = autoteste existente B+; bancos 1..8 = demonstracoes e jogo da velha.
Nao altera os montadores/testes legados.
"""
from pathlib import Path
import re
from assemble_bplus import base

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'src/mips_rom.vhd'
BANK_WORDS = 512
PROGRAMS = [
    ('00_autoteste_bplus', ROOT / 'programs/conceito_bplus_selftest.hex'),
    ('01_soma_1_a_10', ROOT / 'programs/demo_01_soma_1_a_10.asm'),
    ('02_fatorial_5', ROOT / 'programs/demo_02_fatorial_5.asm'),
    ('03_logica_e_shifts', ROOT / 'programs/demo_03_logica_e_shifts.asm'),
    ('04_bytes_halfwords', ROOT / 'programs/demo_04_bytes_halfwords.asm'),
    ('05_fibonacci_8', ROOT / 'programs/demo_05_fibonacci_8.asm'),
    ('06_subrotinas', ROOT / 'programs/demo_06_subrotinas.asm'),
    ('07_comparacoes_branches', ROOT / 'programs/demo_07_comparacoes_branches.asm'),
    ('08_jogo_da_velha', ROOT / 'programs/demo_08_jogo_da_velha.asm'),
]


def assemble_source(path):
    labels = {}
    code = []
    for lineno, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.split('#',1)[0].strip()
        if not line: continue
        while ':' in line:
            label, line = line.split(':',1)
            label = label.strip()
            if not re.fullmatch(r'[A-Za-z_]\w*', label) or label in labels:
                raise ValueError(f'{path}:{lineno}: rotulo invalido {label!r}')
            labels[label]=len(code)
            line=line.strip()
        if line:code.append((lineno,line))
    words=[]
    for index,(line_no, line) in enumerate(code):
        try: words.append(base.assemble(line,index,labels))
        except Exception as exc: raise ValueError(f'{path}:{line_no}: {line}: {exc}') from exc
    return words


def generate():
    entries = []
    for bank,(name,path) in enumerate(PROGRAMS):
        if path.suffix == '.hex':
            words = [int(x,16) for x in path.read_text(encoding='utf-8').split()]
        else:
            words = assemble_source(path)
            path.with_suffix('.hex').write_text(''.join(f'{w:08X}\n' for w in words),encoding='utf-8')
        if not 1 <= len(words) <= BANK_WORDS:
            raise ValueError(f'{name}: {len(words)} palavras, max {BANK_WORDS}')
        entries.append((bank,name,words))
        print(f'{bank}: {name}: {len(words)} palavras')
    body = '\n'.join(f'        tmp({bank*BANK_WORDS+i}) := x"{word:08X}"; -- {name}[{i}]'
                     for bank,name,words in entries
                     for i,word in enumerate(words) if word)
    ROM.write_text(f'''library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ROM UNICA para quartus/top_level.qpf, selecao por SW(4 downto 1).
-- Cada banco possui 512 palavras; PC logico de cada programa comeca em zero.
-- Arquivo gerado por: python tools/build_demo_rom.py
entity mips_rom is
    generic (dataWidth : natural := 32; addrWidth : natural := 13);
    port (
        addr : in std_logic_vector(addrWidth-1 downto 0);
        data : out std_logic_vector(dataWidth-1 downto 0)
    );
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
''',encoding='utf-8')
    return entries

if __name__ == '__main__':generate()

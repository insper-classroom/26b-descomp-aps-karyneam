#!/usr/bin/env python3
"""Confere ROM unica + programas e seus resultados em modelo de referencia Python.
Este verificador NAO substitui a simulacao do VHDL no cocotb/Quartus.
"""
from pathlib import Path
import sys,re
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'test'))
from mips_reference import MipsReference
from build_demo_rom import PROGRAMS,BANK_WORDS
RESULTADOS = [1,55,120,165,4660,21,42,7]
rom = (ROOT/'src/mips_rom.vhd').read_text(encoding='utf-8')
mapa={int(i):int(w,16) for i,w in re.findall(r'tmp\((\d+)\)\s*:=\s*x"([0-9A-Fa-f]{8})"',rom)}
expected={}
for bank,(name,path) in enumerate(PROGRAMS[:8]):
    path = path if path.suffix=='.hex' else path.with_suffix('.hex')
    words=[int(w,16) for w in path.read_text(encoding='utf-8').split()]
    expected.update({bank*BANK_WORDS+i:w for i,w in enumerate(words) if w})
    cpu=MipsReference(program=words)
    for step_n in range(950):
        step=cpu.step()
        if cpu.signature:break
    else:raise AssertionError(f'{name}: travou sem resultado')
    assert cpu.signature==RESULTADOS[bank],f'{name}: assinatura {cpu.signature}, esperado {RESULTADOS[bank]}'
    if bank>0:
        assert cpu.read(0,4)==RESULTADOS[bank],f'{name}: RAM[0] incorreta'
    print(f'PASS banco {bank} {name}: {step_n+1} instrucoes, resultado decimal={RESULTADOS[bank]}, HEX={RESULTADOS[bank]:06X}')
assert all(mapa.get(k)==v for k,v in expected.items()), 'ROM VHDL nao corresponde aos programas .hex'
print('PASS: os 8 bancos da ROM combinada correspondem aos HEX e aos resultados previstos.')

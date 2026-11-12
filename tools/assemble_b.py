#!/usr/bin/env python3
"""Monta autoteste cumulativo C+C++B (42 instrucoes) e ROM para Quartus."""
from pathlib import Path
import assemble_cplus
base = assemble_cplus.base
ROOT = Path(__file__).resolve().parents[1]
base.ASM = ROOT / 'programs/conceito_b_selftest.asm'
base.HEX = ROOT / 'programs/conceito_b_selftest.hex'
base.VHDL = ROOT / 'src/mips_rom.vhd'
base.FUNCT.update({'sllv':4, 'srlv':6, 'srav':7, 'jalr':9})
base.OPCODES.update({'bltz':1, 'bgez':1, 'blez':6, 'bgtz':7})
if __name__ == '__main__':
    base.main()

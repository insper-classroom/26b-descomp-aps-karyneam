#!/usr/bin/env python3
"""Monta autoteste cumulativo C+C++B+B+ (48 mnemonicos)."""
from pathlib import Path
import assemble_b
base = assemble_b.base
ROOT = Path(__file__).resolve().parents[1]
base.ASM = ROOT / 'programs/conceito_bplus_selftest.asm'
base.HEX = ROOT / 'programs/conceito_bplus_selftest.hex'
base.VHDL = ROOT / 'src/mips_rom.vhd'
base.FUNCT.update({'mult':24, 'multu':25, 'mfhi':16, 'mthi':17,
                   'mflo':18, 'mtlo':19})
if __name__ == '__main__':
    base.main()

#!/usr/bin/env python3
"""Montador C+; reutiliza o montador C sem alterar o teste de regressao C.
Gera a ROM C+C+ e arquivo .hex correspondente. Execute ao alterar .asm.
"""
from pathlib import Path
import assemble_c as base

ROOT = Path(__file__).resolve().parents[1]
base.ASM = ROOT / 'programs/conceito_cplus_selftest.asm'
base.HEX = ROOT / 'programs/conceito_cplus_selftest.hex'
base.VHDL = ROOT / 'src/mips_rom.vhd'
base.OPCODES.update({'lb':32, 'lh':33, 'lbu':36, 'lhu':37,
                     'sb':40, 'sh':41})

if __name__ == '__main__':
    base.main()

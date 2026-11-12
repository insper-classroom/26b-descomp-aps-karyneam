#!/usr/bin/env python3
"""Montador pequeno, restrito às instruções REAIS da rubrica C.
Uso: python tools/assemble_c.py
Gera src/mips_rom.vhd e programs/conceito_c_selftest.hex.
Branch = relativo à proxima instrucao; jump = endereco absoluto de byte / 4.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ASM = ROOT / 'programs/conceito_c_selftest.asm'
VHDL = ROOT / 'src/mips_rom.vhd'
HEX = ROOT / 'programs/conceito_c_selftest.hex'
REGS = {**{f'${i}': i for i in range(32)},
    **{f'${name}': i for i, name in enumerate([
       'zero','at','v0','v1','a0','a1','a2','a3',
       't0','t1','t2','t3','t4','t5','t6','t7',
       's0','s1','s2','s3','s4','s5','s6','s7',
       't8','t9','k0','k1','gp','sp','fp','ra'])}}
FUNCT = {'sll':0, 'srl':2, 'sra':3, 'jr':8,
         'add':32,'addu':33,'sub':34,'subu':35,
         'and':36,'or':37,'xor':38,'nor':39,'slt':42,'sltu':43}
OPCODES = {'j':2,'jal':3,'beq':4,'bne':5,'addi':8,'addiu':9,
           'slti':10,'sltiu':11,'andi':12,'ori':13,'xori':14,'lui':15,
           'lw':35,'sw':43}

def reg(token):
    try: return REGS[token.lower()]
    except KeyError: raise ValueError('registrador invalido: '+token)

def imm(token, labels=None):
    # O endereco (em BYTES) de um rotulo cabe em 16 bits nesta ROM de 1024 words.
    # Util para carregar o destino de JR/JALR com ORI, sem pseudo-instrucoes.
    if labels is not None and token in labels:
        return 4 * labels[token]
    return int(token, 0)

def signed16(value):
    if not (-32768 <= value <= 32767): raise ValueError('imediato signed fora de 16 bits: '+str(value))
    return value & 0xFFFF

def unsigned16(value):
    if not (0 <= value <= 65535): raise ValueError('imediato unsigned fora de 16 bits: '+str(value))
    return value

def r(rs,rt,rd,sh,fn):return rs<<21 | rt<<16 | rd<<11 | sh<<6 | fn

def i(op,rs,rt,im):return op<<26 | rs<<21 | rt<<16 | (im&0xFFFF)

def assemble(line,idx,labels):
    t = [p for p in re.split(r'[\s,()]+',line.strip()) if p]
    mnemonic,*a=t
    if mnemonic == 'nop':return 0
    if mnemonic in FUNCT:
        fn=FUNCT[mnemonic]
        if mnemonic in ('sll','srl','sra'):
            rd,rt,amt=reg(a[0]),reg(a[1]),imm(a[2])
            if not 0<=amt<=31: raise ValueError('shamt 0..31')
            return r(0,rt,rd,amt,fn)
        if mnemonic=='jr': return r(reg(a[0]),0,0,0,fn)
        if mnemonic in ('mult', 'multu'):
            if len(a) != 2: raise ValueError(f'{mnemonic} espera rs, rt')
            return r(reg(a[0]), reg(a[1]), 0, 0, fn)
        if mnemonic in ('mthi', 'mtlo'):
            if len(a) != 1: raise ValueError(f'{mnemonic} espera rs')
            return r(reg(a[0]), 0, 0, 0, fn)
        if mnemonic in ('mfhi', 'mflo'):
            if len(a) != 1: raise ValueError(f'{mnemonic} espera rd')
            return r(0, 0, reg(a[0]), 0, fn)
        if mnemonic=='jalr':
            if len(a) == 1: # jalr rs equivale a jalr $ra, rs
                dest, source = 31, reg(a[0])
            elif len(a) == 2:
                dest, source = reg(a[0]), reg(a[1])
            else: raise ValueError('jalr espera rs ou rd, rs')
            return r(source,0,dest,0,fn)
        if mnemonic in ('sllv','srlv','srav'):
            rd,rt,rs = map(reg,a)
            return r(rs,rt,rd,0,fn)
        rd,rs,rt=map(reg,a)
        return r(rs,rt,rd,0,fn)
    op=OPCODES[mnemonic]
    if mnemonic in ('j','jal'):
        addr=labels[a[0]] if a[0] in labels else imm(a[0])//4
        if not 0<=addr<2**26: raise ValueError('alvo de jump fora do alcance')
        return op<<26 | addr
    if mnemonic in ('beq','bne'):
        rs,rt=reg(a[0]),reg(a[1]); target=labels[a[2]]
        return i(op,rs,rt,signed16(target-idx-1))
    if mnemonic in ('bltz','bgez','blez','bgtz'):
        rs=reg(a[0]); target=labels[a[1]]
        # bltz/bgez compartilham opcode 1: o campo rt diferencia os dois.
        rt=1 if mnemonic=='bgez' else 0
        return i(op,rs,rt,signed16(target-idx-1))
    if mnemonic in ('lw','sw','lb','lbu','lh','lhu','sb','sh'):
        rt,offset,rs=reg(a[0]),signed16(imm(a[1])),reg(a[2])
        return i(op,rs,rt,offset)
    if mnemonic=='lui':return i(op,0,reg(a[0]),unsigned16(imm(a[1])))
    rt,rs=reg(a[0]),reg(a[1]); value=imm(a[2],labels)
    if mnemonic in ('andi','ori','xori'): value=unsigned16(value)
    else: value=signed16(value)
    return i(op,rs,rt,value)

def main():
    labels={}; code=[]
    for n,line in enumerate(ASM.read_text(encoding='utf-8').splitlines(),1):
        line=line.split('#',1)[0].strip()
        if not line:continue
        while ':' in line:
            label,line=line.split(':',1)
            label=label.strip()
            if not re.fullmatch(r'[A-Za-z_]\w*',label) or label in labels:
                raise ValueError(f'rotulo invalido/duplicado linha {n}: {label}')
            labels[label]=len(code)
            line=line.strip()
        if line:code.append((n,line))
    if len(code)>1024:raise ValueError('ROM suporta ate 1024 palavras')
    words=[]
    for idx,(lineno,line) in enumerate(code):
        try:words.append(assemble(line,idx,labels))
        except Exception as exc:raise ValueError(f'linha {lineno}: {line}: {exc}') from exc
    HEX.write_text(''.join(f'{word:08X}\n' for word in words),encoding='utf-8')
    body='\n'.join(f'      tmp({idx}) := x"{word:08X}"; -- {line}'
                   for idx, ((_,line),word) in enumerate(zip(code,words)))
    vhdl=f'''library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- Gerado automaticamente de programs/{ASM.name} pelo montador do projeto
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
    VHDL.write_text(vhdl,encoding='utf-8')
    print(f'Geradas {len(words)} instrucoes; labels: '+str(labels))

if __name__=='__main__':main()

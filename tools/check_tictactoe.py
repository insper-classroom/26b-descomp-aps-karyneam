#!/usr/bin/env python3
"""Emulador independente para o programa Assembly do jogo da velha.
Nao substitui o Quartus nem a simulacao VHDL/FPGA.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ROM = [int(s,16) for s in (ROOT/'programs/demo_08_jogo_da_velha.hex').read_text().split()]
MASK = 0xffffffff

def ss(x):
    x &= MASK
    return x if x < 2**31 else x-2**32

class CPU:
    def __init__(self):
        self.reg=[0]*32
        self.pc=0
        self.memory={}
        self.io={0x104:0,0x108:0,0x10c:0}
        self.keys=0
        self.steps=0
        self.error=None

    def step(self):
        idx=self.pc//4
        if idx<0 or idx>=len(ROM):raise RuntimeError(f'PC fora ROM {self.pc:08x}')
        w=ROM[idx]
        op=w>>26; rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;sh=(w>>6)&31;fn=w&63
        u=w&0xffff; imm=u if u<0x8000 else u-0x10000
        rv=self.reg; nxt=self.pc+4
        if op==0:
            if fn in (33,35):
                rv[rd]=(rv[rs]+rv[rt] if fn==33 else rv[rs]-rv[rt])&MASK
            elif fn==0:rv[rd]=(rv[rt]<<sh)&MASK
            elif fn==4:rv[rd]=(rv[rt]<<(rv[rs]&31))&MASK
            elif fn==37:rv[rd]=rv[rs]|rv[rt]
            else: raise RuntimeError(f'R funct {fn} em PC={self.pc}')
        elif op in (8,9):rv[rt]=(rv[rs]+imm)&MASK
        elif op==12:rv[rt]=rv[rs]&u
        elif op==35:
            addr=(rv[rs]+imm)&MASK
            rv[rt]=self.keys if addr==0x100 else self.io.get(addr,0) if addr>=0x100 else self.memory.get(addr,0)
        elif op==43:
            addr=(rv[rs]+imm)&MASK
            if addr>=0x100:self.io[addr]=rv[rt]
            else:self.memory[addr]=rv[rt]
        elif op==4:
            if rv[rs]==rv[rt]:nxt+=imm*4
        elif op==5:
            if rv[rs]!=rv[rt]:nxt+=imm*4
        elif op==1:
            if rt==1 and ss(rv[rs])>=0:nxt+=imm*4
            elif rt==0 and ss(rv[rs])<0:nxt+=imm*4
            elif rt not in (0,1):raise RuntimeError('REGIMM invalido')
        elif op==7:
            if ss(rv[rs])>0:nxt+=imm*4
        elif op==2:nxt=(w&0x3ffffff)*4
        else:raise RuntimeError(f'opcode {op} em PC={self.pc}')
        self.pc=nxt
        rv[0]=0
        self.steps+=1

    def run(self,n=1500):
        for _ in range(n):self.step()
    def press(self,key):
        self.keys=key
        self.run(250)
        self.keys=0
        self.run(250)
    def goto(self,target):
        current=self.io[0x108]
        while current!=target:
            self.press(2) # proxima
            current=(current+1)%9
            assert self.io[0x108]==current,(current,self.io)
    def play(self,target):
        self.goto(target)
        self.press(4) # confirmar
    def board(self):
        return [self.memory.get(0x40+4*i,0) for i in range(9)]

def scenario(sequence, expected_status, expected_board):
    cpu=CPU();cpu.run(250)
    assert cpu.io[0x10c]==1 and cpu.board()==[0]*9
    for p in sequence:cpu.play(p)
    assert cpu.io[0x10c]==expected_status,(sequence,cpu.io)
    assert cpu.board()==expected_board,(sequence,cpu.board(),expected_board)
    for i,v in enumerate(expected_board):
        assert (cpu.io[0x104]>>(2*i))&3==v
    print('PASS',sequence,'status',expected_status,'tabuleiro',expected_board,'steps',cpu.steps)

if __name__=='__main__':
    scenario([0,3,1,4,2],3,[1,1,1,2,2,0,0,0,0])
    scenario([0,3,1,4,8,5],4,[1,1,0,2,2,2,0,0,1])
    scenario([0,1,2,4,3,5,7,6,8],5,[1,2,1,1,2,2,2,1,1])
    cpu=CPU();cpu.run(250);cpu.play(0);state=cpu.io[0x104]; cpu.play(0)
    assert cpu.io[0x104]==state and cpu.io[0x10c]==2
    cpu.goto(8);cpu.press(2);assert cpu.io[0x108]==0
    cpu.press(1);assert cpu.io[0x108]==8
    print('PASS casa ocupada e circulacao do cursor')

#!/usr/bin/env python3
"""Emulador independente, para verificar a sequencia de ROM e os checks do autoteste.
NAO substitui compilacao/simulacao do VHDL nem o teste na FPGA.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
words=[int(x,16) for x in (ROOT/'programs/conceito_c_selftest.hex').read_text().split()]
regs=[0]*32;mem=[0]*64;pc=0;seen=set(); steps=0;log=[]
mask=0xFFFFFFFF
signed=lambda x: x-0x100000000 if x & 0x80000000 else x
while steps<400:
    assert pc%4==0 and 0<=pc//4<len(words),f'PC saiu da ROM: {pc:08X}'
    w=words[pc//4];op=(w>>26)&63;rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;sh=(w>>6)&31;fn=w&63;imm=w&65535
    si=imm-65536 if imm&0x8000 else imm
    nxt=pc+4;wr=None
    a=regs[rs];b=regs[rt];name=''
    if op==0:
        fns={0:'sll',2:'srl',3:'sra',8:'jr',32:'add',33:'addu',34:'sub',35:'subu',36:'and',37:'or',38:'xor',39:'nor',42:'slt',43:'sltu'}
        name=fns.get(fn,'unknown')
        if fn in (32,33):wr=(rd,(a+b)&mask)
        if fn in (34,35):wr=(rd,(a-b)&mask)
        if fn==36:wr=(rd,a&b)
        if fn==37:wr=(rd,a|b)
        if fn==38:wr=(rd,a^b)
        if fn==39:wr=(rd,~(a|b)&mask)
        if fn==42:wr=(rd,int(signed(a)<signed(b)))
        if fn==43:wr=(rd,int(a<b))
        if fn==0:wr=(rd,(b<<sh)&mask)
        if fn==2:wr=(rd,b>>sh)
        if fn==3:wr=(rd,signed(b)>>sh&mask)
        if fn==8:nxt=a
    else:
        ops={2:'j',3:'jal',4:'beq',5:'bne',8:'addi',9:'addiu',10:'slti',11:'sltiu',12:'andi',13:'ori',14:'xori',15:'lui',35:'lw',43:'sw'}
        name=ops.get(op,'unknown')
        if op in (8,9):wr=(rt,(a+si)&mask)
        if op==10:wr=(rt,int(signed(a)<si))
        if op==11:wr=(rt,int(a<(si&mask)))
        if op==12:wr=(rt,a&imm)
        if op==13:wr=(rt,a|imm)
        if op==14:wr=(rt,a^imm)
        if op==15:wr=(rt,imm<<16)
        if op in (35,43):
            addr=(a+si)&mask
            assert addr%4==0 and addr<256,(hex(addr),name)
            if op==35:wr=(rt,mem[addr//4])
            else:mem[addr//4]=b
        if op==4 and a==b:nxt=pc+4+si*4
        if op==5 and a!=b:nxt=pc+4+si*4
        if op in (2,3):
            if op==3:wr=(31,pc+4)
            nxt=((pc+4)&0xF0000000)|((w&0x3FFFFFF)<<2)
    assert name!='unknown',f'unrecognized op at {pc}: {w:08x}'
    if wr and wr[0]!=0:regs[wr[0]]=wr[1]&mask
    regs[0]=0
    seen.add(name);log.append((pc,name))
    steps+=1;pc=nxt
    if mem[63] in (1,2):break
else:raise AssertionError('nao concluiu o autoteste')
expected={'add','addu','addi','addiu','sub','subu','slt','sltu','slti','sltiu','and','andi','or','ori','xor','xori','nor','lui','sll','srl','sra','lw','sw','beq','bne','j','jal','jr'}
assert mem[63]==1, f'FAIL em {log[-1]} (status={mem[63]})'
assert seen==expected, f'Cobertura incompleta: {sorted(expected-seen)} / extras: {sorted(seen-expected)}'
print(f'PASS: {steps} instrucoes executadas; {len(seen)} instrucoes distintas verificadas; RAM[0xFC]={mem[63]}')
print('Cobertura: '+', '.join(sorted(seen)))

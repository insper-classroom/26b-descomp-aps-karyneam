# APS A/A+ - Jogo da velha para LT24 (dois jogadores, 3 botoes)
# MMIO: 0x100=teclas (KEY1 bit0, KEY2 bit1, KEY3 bit2; 1=pressionado)
#       0x104=tabuleiro compactado, 2 bits/casa (0 vazio, 1 X, 2 O)
#       0x108=cursor 0..8, 0x10C=estado (1=X,2=O,3=X venceu,4=O venceu,5=empate)
# RAM: 0x40..0x60 = nove palavras do tabuleiro.
# Nao ha branch delay slots neste processador.
start:
    addiu $s0, $zero, 64       # base da RAM das casas
    addiu $s1, $zero, 1        # X comeca
    addiu $s2, $zero, 0        # cursor
    addiu $s3, $zero, 0        # 18 bits compactados para LCD
    addiu $s4, $zero, 0        # numero de jogadas
    addiu $s6, $zero, 256      # base MMIO
    addiu $s7, $zero, 0        # casas do X (mascara 9 bits)
    addiu $t8, $zero, 0        # casas do O (mascara 9 bits)
    sw $s3, 4($s6)
    sw $s2, 8($s6)
    sw $s1, 12($s6)
    addiu $t0, $zero, 9
    addu $t1, $s0, $zero
limpar:
    sw $zero, 0($t1)
    addiu $t1, $t1, 4
    addiu $t0, $t0, -1
    bgtz $t0, limpar

aguardar:
    lw $t0, 0($s6)
    andi $t1, $t0, 1           # KEY1: anterior
    bne $t1, $zero, anterior
    andi $t1, $t0, 2           # KEY2: proxima
    bne $t1, $zero, proxima
    andi $t1, $t0, 4           # KEY3: confirmar
    bne $t1, $zero, confirmar
    j aguardar

anterior:
    addiu $s2, $s2, -1
    bgez $s2, cursor_atualizado
    addiu $s2, $zero, 8
    j cursor_atualizado
proxima:
    addiu $s2, $s2, 1
    addiu $t0, $zero, 9
    bne $s2, $t0, cursor_atualizado
    addiu $s2, $zero, 0
cursor_atualizado:
    sw $s2, 8($s6)
    j aguardar_soltar

confirmar:
    sll $t1, $s2, 2
    addu $t1, $t1, $s0         # &tabuleiro[cursor]
    lw $t2, 0($t1)
    bne $t2, $zero, aguardar_soltar
    sw $s1, 0($t1)            # a jogada acontece no MIPS!
    sll $t3, $s2, 1
    sllv $t4, $s1, $t3
    or $s3, $s3, $t4           # compacta estado para o LCD
    sw $s3, 4($s6)
    addiu $s4, $s4, 1

    addiu $t3, $zero, 1
    sllv $t3, $t3, $s2         # mascara da casa 0..8
    addiu $t0, $zero, 1
    bne $s1, $t0, jogou_o
    or $s7, $s7, $t3
    addu $t9, $s7, $zero
    j conferir_vitoria
jogou_o:
    or $t8, $t8, $t3
    addu $t9, $t8, $zero

# 8 trincas: linhas, colunas e diagonais
conferir_vitoria:
    andi $t4, $t9, 7
    addiu $t5, $zero, 7
    beq $t4, $t5, ganhou
    andi $t4, $t9, 56
    addiu $t5, $zero, 56
    beq $t4, $t5, ganhou
    andi $t4, $t9, 448
    addiu $t5, $zero, 448
    beq $t4, $t5, ganhou
    andi $t4, $t9, 73
    addiu $t5, $zero, 73
    beq $t4, $t5, ganhou
    andi $t4, $t9, 146
    addiu $t5, $zero, 146
    beq $t4, $t5, ganhou
    andi $t4, $t9, 292
    addiu $t5, $zero, 292
    beq $t4, $t5, ganhou
    andi $t4, $t9, 273
    addiu $t5, $zero, 273
    beq $t4, $t5, ganhou
    andi $t4, $t9, 84
    addiu $t5, $zero, 84
    beq $t4, $t5, ganhou
    addiu $t0, $zero, 9
    beq $s4, $t0, empate

    addiu $t0, $zero, 3
    subu $s1, $t0, $s1         # alterna X e O
    sw $s1, 12($s6)
    j aguardar_soltar

ganhou:
    addiu $t0, $zero, 2
    addu $t0, $t0, $s1         # status 3=X venceu; 4=O venceu
    sw $t0, 12($s6)
    j fim
empate:
    addiu $t0, $zero, 5
    sw $t0, 12($s6)
    j fim

aguardar_soltar:
    lw $t0, 0($s6)
    bne $t0, $zero, aguardar_soltar
    j aguardar
fim:
    j fim                      # KEY0 reinicia a partida

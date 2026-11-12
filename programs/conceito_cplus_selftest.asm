# Programa de autoteste do conceito C: instrucoes MIPS executadas na FPGA.
# LEDR9=PASS quando SW $t7, 252($zero) grava 1; LEDR8=FAIL se grava 2.
# Sem branch delay slot (conforme CPU didatica implementada).

start:
    addi  $t0, $zero, 5
    addiu $t1, $zero, 3
    addiu $t3, $zero, 8
    add   $t2, $t0, $t1
    bne   $t2, $t3, fail
    addu  $t2, $t0, $t1
    bne   $t2, $t3, fail
    addiu $t3, $zero, 2
    sub   $t2, $t0, $t1
    bne   $t2, $t3, fail
    subu  $t2, $t0, $t1
    bne   $t2, $t3, fail

    addi  $t2, $t0, -7          # -2
    addiu $t3, $zero, -2
    bne   $t2, $t3, fail
    addiu $t2, $t0, -7         # -2 (addiu sem trap)
    bne   $t2, $t3, fail
    slt   $t2, $t1, $t0         # 3 < 5
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail
    sltu  $t2, $t1, $t0
    bne   $t2, $t3, fail
    slti  $t2, $t1, 4
    bne   $t2, $t3, fail
    sltiu $t2, $t1, 4
    bne   $t2, $t3, fail
    addiu $t4, $zero, -1
    slt   $t2, $t4, $t1         # -1 < 3 signed
    bne   $t2, $t3, fail
    sltu  $t2, $t4, $t1         # 0xFFFFFFFF < 3 unsigned = falso
    bne   $t2, $zero, fail
    sltiu $t2, $t1, -1         # 3 < 0xFFFFFFFF unsigned
    bne   $t2, $t3, fail

    and   $t2, $t0, $t1         # 5 & 3 = 1
    bne   $t2, $t3, fail
    andi  $t2, $t0, 3
    bne   $t2, $t3, fail
    or    $t2, $t0, $t1         # 5 | 3 = 7
    addiu $t3, $zero, 7
    bne   $t2, $t3, fail
    ori   $t2, $t0, 2          # 5 | 2 = 7
    bne   $t2, $t3, fail
    xor   $t2, $t0, $t1         # 5 ^ 3 = 6
    addiu $t3, $zero, 6
    bne   $t2, $t3, fail
    xori  $t2, $t0, 3
    bne   $t2, $t3, fail
    nor   $t2, $t0, $t1         # ~(5|3) = -8
    addiu $t3, $zero, -8
    bne   $t2, $t3, fail
    lui   $t2, 0x1234
    ori   $t3, $zero, 0x1234
    sll   $t3, $t3, 16
    bne   $t2, $t3, fail

    sll   $t2, $t1, 2          # 3 << 2 = 12
    addiu $t3, $zero, 12
    bne   $t2, $t3, fail
    lui   $t4, 0x8000
    srl   $t2, $t4, 31         # 0x80000000 >> 31 = 1
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail
    sra   $t2, $t4, 31         # -2147483648 >> 31 = -1
    addiu $t3, $zero, -1
    bne   $t2, $t3, fail

    sw    $t0, 0($zero)        # RAM[0] = 5
    lw    $t2, 0($zero)
    bne   $t2, $t0, fail
    sw    $t1, 4($zero)        # RAM[4] = 3
    lw    $t2, 4($zero)
    bne   $t2, $t1, fail
    beq   $t0, $t0, beq_ok
    j     fail
beq_ok:
    beq   $t0, $t1, fail       # nao pode desviar
    bne   $t0, $t1, bne_ok
    j     fail
bne_ok:
    bne   $t0, $t0, fail       # nao pode desviar
    j     jump_ok
    j     fail
jump_ok:
    jal   subroutine          # testa jal e link $ra = PC+4
    addiu $t3, $zero, 9
    bne   $t2, $t3, fail
    j     pass

subroutine:
    addiu $t2, $zero, 9
    jr    $ra
    j     fail

pass:
    # Inicio da extensao C+: so chegamos aqui se TODO o conceito C passou.
    # Little-endian: SW 0x80FF7F01 em 0x40 deixa bytes 01 7F FF 80.
    lui   $s0, 0x80FF
    ori   $s0, $s0, 0x7F01
    sw    $s0, 64($zero)

    lb    $t2, 64($zero)        # byte0 = 0x01, positivo
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail
    lb    $t2, 65($zero)        # byte1 = 0x7F, positivo
    addiu $t3, $zero, 127
    bne   $t2, $t3, fail
    lb    $t2, 66($zero)        # byte2 = 0xFF => -1
    addiu $t3, $zero, -1
    bne   $t2, $t3, fail
    lb    $t2, 67($zero)        # byte3 = 0x80 => -128
    addiu $t3, $zero, -128
    bne   $t2, $t3, fail

    lbu   $t2, 66($zero)       # 0xFF => 255
    ori   $t3, $zero, 255
    bne   $t2, $t3, fail
    lbu   $t2, 67($zero)       # 0x80 => 128
    ori   $t3, $zero, 128
    bne   $t2, $t3, fail

    lh    $t2, 64($zero)        # 0x7F01 => 32513
    ori   $t3, $zero, 0x7F01
    bne   $t2, $t3, fail
    lh    $t2, 66($zero)        # 0x80FF => 0xFFFF80FF
    lui   $t3, 0xFFFF
    ori   $t3, $t3, 0x80FF
    bne   $t2, $t3, fail
    lhu   $t2, 66($zero)       # 0x80FF => 0x000080FF
    ori   $t3, $zero, 0x80FF
    bne   $t2, $t3, fail
    lhu   $t2, 64($zero)       # 0x7F01
    ori   $t3, $zero, 0x7F01
    bne   $t2, $t3, fail

    addiu $s4, $zero, 68       # base+imediato negativo
    lbu   $t2, -3($s4)         # 68-3 => byte1 (0x7F)
    addiu $t3, $zero, 127
    bne   $t2, $t3, fail

    ori   $s1, $zero, 0x12A5   # sb grava APENAS 0xA5
    sb    $s1, 65($zero)       # lane1 => 0x80FFA501
    lw    $t2, 64($zero)
    lui   $t3, 0x80FF
    ori   $t3, $t3, 0xA501
    bne   $t2, $t3, fail
    sb    $zero, 64($zero)     # lane0 => 0x80FFA500
    lw    $t2, 64($zero)
    lui   $t3, 0x80FF
    ori   $t3, $t3, 0xA500
    bne   $t2, $t3, fail
    sb    $s1, 66($zero)       # lane2 => 0x80A5A500
    lw    $t2, 64($zero)
    lui   $t3, 0x80A5
    ori   $t3, $t3, 0xA500
    bne   $t2, $t3, fail
    sb    $s1, 67($zero)       # lane3 => 0xA5A5A500
    lw    $t2, 64($zero)
    lui   $t3, 0xA5A5
    ori   $t3, $t3, 0xA500
    bne   $t2, $t3, fail

    ori   $s2, $zero, 0xBEEF
    sh    $s2, 64($zero)       # half baixo => 0xA5A5BEEF
    lw    $t2, 64($zero)
    lui   $t3, 0xA5A5
    ori   $t3, $t3, 0xBEEF
    bne   $t2, $t3, fail
    sh    $s2, 66($zero)       # half alto => 0xBEEFBEEF
    lw    $t2, 64($zero)
    lui   $t3, 0xBEEF
    ori   $t3, $t3, 0xBEEF
    bne   $t2, $t3, fail
    lh    $t2, 66($zero)       # signed 0xBEEF => 0xFFFFBEEF
    lui   $t3, 0xFFFF
    ori   $t3, $t3, 0xBEEF
    bne   $t2, $t3, fail
    lhu   $t2, 66($zero)       # unsigned 0xBEEF => 0x0000BEEF
    ori   $t3, $zero, 0xBEEF
    bne   $t2, $t3, fail

    sb    $zero, -1($s4)      # 0x43 = lane3, => 0x00EFBEEF
    lw    $t2, 64($zero)
    lui   $t3, 0x00EF
    ori   $t3, $t3, 0xBEEF
    bne   $t2, $t3, fail
    sh    $zero, -4($s4)      # 0x40 = half baixo, => 0x00EF0000
    lw    $t2, 64($zero)
    lui   $t3, 0x00EF
    bne   $t2, $t3, fail
    lb    $t2, -1($s4)        # byte alto zerado por sb
    bne   $t2, $zero, fail
    lhu   $t2, -4($s4)       # half baixo zerado por sh
    bne   $t2, $zero, fail

    # Passou nas 28 instrucoes C + 6 instrucoes C+.
    addiu $t7, $zero, 1
    sw    $t7, 252($zero)
pass_loop:
    j     pass_loop

fail:
    addiu $t7, $zero, 2
    sw    $t7, 252($zero)
fail_loop:
    j     fail_loop

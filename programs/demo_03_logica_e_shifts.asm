# Operacoes logicas e shifts: resultado 0xA5 = 165
# C: ori, xor, andi, sll, srl; B: sllv, srlv, srav
    ori   $t0, $zero, 0xF0
    ori   $t1, $zero, 0x0F
    xor   $t2, $t0, $t1
    andi  $t2, $t2, 0x00A5
    addiu $t3, $zero, 1
    sllv  $t4, $t2, $t3
    srlv  $s0, $t4, $t3
    addiu $t5, $zero, -16
    srav  $t6, $t5, $t3
    addiu $t7, $zero, -8
    bne   $t6, $t7, fail
    and   $t8, $t0, $t1
    bne   $t8, $zero, fail
    or    $t9, $t0, $t1
    addiu $t8, $zero, 255
    bne   $t9, $t8, fail
    ori   $t8, $zero, 0xA5
    bne   $s0, $t8, fail
    sw    $s0, 0($zero)
    sw    $s0, 252($zero)
fim:
    j fim
fail:
    lui   $t7, 0x00FF
    ori   $t7, $t7, 0xFFFF
    sw    $t7, 252($zero)
trava:
    j trava

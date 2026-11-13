# C+: load/store de byte e halfword, sinal e preservacao
# Resultado esperado 0x1234 = 4660
    lui   $t0, 0x80FF
    ori   $t0, $t0, 0x7E01
    sw    $t0, 8($zero)
    lb    $t1, 11($zero)
    addiu $t7, $zero, -128
    bne   $t1, $t7, fail
    lbu   $t2, 10($zero)
    addiu $t7, $zero, 255
    bne   $t2, $t7, fail
    lh    $t3, 10($zero)
    lui   $t7, 0xFFFF
    ori   $t7, $t7, 0x80FF
    bne   $t3, $t7, fail
    lhu   $t4, 10($zero)
    ori   $t7, $zero, 0x80FF
    bne   $t4, $t7, fail
    sb    $zero, 9($zero)
    ori   $t5, $zero, 0x1234
    sh    $t5, 10($zero)
    lw    $t6, 8($zero)
    lui   $t7, 0x1234
    ori   $t7, $t7, 0x0001
    bne   $t6, $t7, fail
    lbu   $t6, 8($zero)
    addiu $t7, $zero, 1
    bne   $t6, $t7, fail
    lhu   $s0, 10($zero)
    ori   $t7, $zero, 0x1234
    bne   $s0, $t7, fail
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

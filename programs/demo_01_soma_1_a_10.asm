# Soma 1 + ... + 10 = 55
# C: add, addiu, bne, lw, sw
    addiu $t0, $zero, 1
    addiu $t1, $zero, 0
    addiu $t2, $zero, 11
loop:
    add   $t1, $t1, $t0
    addiu $t0, $t0, 1
    bne   $t0, $t2, loop
    sw    $t1, 0($zero)
    lw    $s0, 0($zero)
    addiu $t3, $zero, 55
    bne   $s0, $t3, fail
    sw    $s0, 252($zero)
fim:
    j fim
fail:
    lui   $t7, 0x00FF
    ori   $t7, $t7, 0xFFFF
    sw    $t7, 252($zero)
trava:
    j trava

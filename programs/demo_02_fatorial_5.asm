# Fatorial de 5 = 120
# B+: mult, mflo, mfhi; B: bgtz
    addiu $t0, $zero, 1
    addiu $t1, $zero, 5
loop:
    mult  $t0, $t1
    mflo  $t0
    mfhi  $t2
    bne   $t2, $zero, fail
    addiu $t1, $t1, -1
    bgtz  $t1, loop
    sw    $t0, 0($zero)
    addiu $t3, $zero, 120
    bne   $t0, $t3, fail
    sw    $t0, 252($zero)
fim:
    j fim
fail:
    lui   $t7, 0x00FF
    ori   $t7, $t7, 0xFFFF
    sw    $t7, 252($zero)
trava:
    j trava

# Fibonacci: F(8) = 21 (F(0)=0, F(1)=1)
# C: addu, addiu, sw, lw; B: bgtz
    addiu $t0, $zero, 0
    addiu $t1, $zero, 1
    addiu $t2, $zero, 8
loop:
    addu  $t3, $t0, $t1
    addu  $t0, $t1, $zero
    addu  $t1, $t3, $zero
    addiu $t2, $t2, -1
    bgtz  $t2, loop
    sw    $t0, 0($zero)
    lw    $s0, 0($zero)
    addiu $t7, $zero, 21
    bne   $s0, $t7, fail
    sw    $s0, 252($zero)
fim:
    j fim
fail:
    lui   $t7, 0x00FF
    ori   $t7, $t7, 0xFFFF
    sw    $t7, 252($zero)
trava:
    j trava

# Comparacoes signed/unsigned + quatro branches adicionais
# Resultado calculado: 7
    addiu $t0, $zero, -1
    addiu $t1, $zero, 1
    slt   $t2, $t0, $t1
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail
    sltu  $t2, $t0, $t1
    bne   $t2, $zero, fail
    slti  $t2, $t0, 0
    bne   $t2, $t3, fail
    sltiu $t2, $t0, 0
    bne   $t2, $zero, fail
    bltz  $t0, negativo
    j fail
negativo:
    bgez  $t1, positivo
    j fail
positivo:
    blez  $t0, nao_positivo
    j fail
nao_positivo:
    bgtz  $t1, ok
    j fail
ok:
    addiu $s0, $zero, 3
    sll   $s0, $s0, 1
    addiu $s0, $s0, 1
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

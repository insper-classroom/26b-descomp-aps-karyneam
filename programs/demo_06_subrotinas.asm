# Produto 6 * 7 = 42 usando jal/jr, jalr e multu/mflo
# Sem branch delay slots, como definido neste processador
    addiu $a0, $zero, 6
    addiu $a1, $zero, 7
    jal   multiplica
    ori   $t6, $zero, verifica
    jalr  $s5, $t6
    sw    $v0, 0($zero)
    addiu $t7, $zero, 42
    bne   $v0, $t7, fail
    sw    $v0, 252($zero)
fim:
    j fim
multiplica:
    multu $a0, $a1
    mflo  $v0
    jr    $ra
verifica:
    addu  $v0, $v0, $zero
    jr    $s5
fail:
    lui   $t7, 0x00FF
    ori   $t7, $t7, 0xFFFF
    sw    $t7, 252($zero)
trava:
    j trava

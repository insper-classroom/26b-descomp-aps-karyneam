# Programa acumulativo de autoteste C + C+ + B + B+ na FPGA.
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

    # ==== CONCEITO B: shifts variaveis, branches extras e jalr. ====
    # Falha em qualquer teste (C, C+ ou B) salta para 'fail'.
    # sllv: rs fornece quantidade; somente 5 bits baixos sao usados.
    addiu $t0, $zero, 3
    addiu $t1, $zero, 2
    sllv  $t2, $t0, $t1        # 3 << 2 = 12
    addiu $t3, $zero, 12
    bne   $t2, $t3, fail
    addiu $t1, $zero, 34      # 34 & 31 = 2
    sllv  $t2, $t0, $t1
    bne   $t2, $t3, fail
    sllv  $t2, $t0, $zero     # deslocamento 0
    bne   $t2, $t0, fail
    addiu $t0, $zero, 1
    addiu $t1, $zero, 31
    sllv  $t2, $t0, $t1       # bit 31 = 1
    lui   $t3, 0x8000
    bne   $t2, $t3, fail

    # srlv: logico (insere zeros); tambem mascara rs[4:0].
    addiu $t1, $zero, 63      # mascara -> 31
    srlv  $t2, $t3, $t1       # 0x80000000 >> 31 = 1
    addiu $t4, $zero, 1
    bne   $t2, $t4, fail
    srlv  $t2, $t3, $zero
    bne   $t2, $t3, fail
    addiu $t1, $zero, 4
    srlv  $t2, $t3, $t1       # 0x08000000
    lui   $t4, 0x0800
    bne   $t2, $t4, fail

    # srav: aritmetico (repete bit de sinal).
    addiu $t3, $zero, -16
    addiu $t1, $zero, 2
    srav  $t2, $t3, $t1       # -16 >> 2 = -4
    addiu $t4, $zero, -4
    bne   $t2, $t4, fail
    addiu $t1, $zero, 63      # 63 & 31 = 31
    srav  $t2, $t3, $t1       # -16 >> 31 = -1
    addiu $t4, $zero, -1
    bne   $t2, $t4, fail
    srav  $t2, $t3, $zero
    bne   $t2, $t3, fail
    addiu $t3, $zero, 16
    addiu $t1, $zero, 2
    srav  $t2, $t3, $t1       # +16 >> 2 = 4
    addiu $t4, $zero, 4
    bne   $t2, $t4, fail

    # Valores base para os branches assinados.
    addiu $t0, $zero, -1
    addiu $t1, $zero, 0
    addiu $t2, $zero, 1

    bltz  $t0, bltz_negative_ok # -1: tomado
    j     fail
bltz_negative_ok:
    bltz  $t1, fail          # zero: nao tomado
    bltz  $t2, fail          # positivo: nao tomado
    bgez  $t0, fail          # -1: nao tomado
    bgez  $t1, bgez_zero_ok  # zero: tomado
    j     fail
bgez_zero_ok:
    bgez  $t2, bgez_positive_ok  # positivo: tomado
    j     fail
bgez_positive_ok:
    blez  $t0, blez_negative_ok  # negativo: tomado
    j     fail
blez_negative_ok:
    blez  $t1, blez_zero_ok  # zero: tomado
    j     fail
blez_zero_ok:
    blez  $t2, fail          # positivo: nao tomado
    bgtz  $t0, fail          # negativo: nao tomado
    bgtz  $t1, fail          # zero: nao tomado
    bgtz  $t2, bgtz_positive_ok # positivo: tomado
    j     fail
bgtz_positive_ok:
    # JALR: salto para endereco em rs, PC+4 no rd informado.
    # Primeiro testa destino diferente de $ra, sem alterar $ra.
    ori   $ra, $zero, 0x55AA
    ori   $t5, $zero, jalr_sub_s7   # endereco simbolico em bytes
    jalr  $s7, $t5
jalr_return_s7:
    ori   $t3, $zero, jalr_return_s7
    bne   $s7, $t3, fail
    ori   $t3, $zero, 0x55AA
    bne   $ra, $t3, fail
    addiu $t3, $zero, 42
    bne   $t2, $t3, fail

    # Testa sintaxe 'jalr rs': destino implicito $ra.
    ori   $t5, $zero, jalr_sub_ra
    jalr  $t5
jalr_return_ra:
    ori   $t3, $zero, jalr_return_ra
    bne   $ra, $t3, fail
    addiu $t3, $zero, 99
    bne   $t2, $t3, fail
    j     pass_b

jalr_sub_s7:
    addiu $t2, $zero, 42
    jr    $s7
    j     fail                # nao deve executar
jalr_sub_ra:
    addiu $t2, $zero, 99
    jr    $ra
    j     fail                # nao deve executar

pass_b:
    # ===== CONCEITO B+: registradores HI/LO e multiplicacao 64 bits =====
    # Antes de qualquer escrita, HI e LO precisam estar zerados pelo reset.
    mfhi  $t2
    bne   $t2, $zero, fail
    mflo  $t2
    bne   $t2, $zero, fail

    # mult +7 * +9 = 63 (HI=0, LO=63).
    addiu $t0, $zero, 7
    addiu $t1, $zero, 9
    mult  $t0, $t1
    mfhi  $t2
    bne   $t2, $zero, fail
    mflo  $t2
    addiu $t3, $zero, 63
    bne   $t2, $t3, fail

    # mult -7 * +9 = -63 = 0xFFFFFFFFFFFFFFC1.
    addiu $t0, $zero, -7
    mult  $t0, $t1
    mfhi  $t2
    addiu $t3, $zero, -1
    bne   $t2, $t3, fail
    mflo  $t2
    addiu $t3, $zero, -63
    bne   $t2, $t3, fail

    # mult -1 * -1 = +1.
    addiu $t0, $zero, -1
    mult  $t0, $t0
    mfhi  $t2
    bne   $t2, $zero, fail
    mflo  $t2
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail

    # mult (-2^31)*2 = -2^32: HI=0xFFFFFFFF; LO=0.
    lui   $t0, 0x8000
    addiu $t1, $zero, 2
    mult  $t0, $t1
    mfhi  $t2
    addiu $t3, $zero, -1
    bne   $t2, $t3, fail
    mflo  $t2
    bne   $t2, $zero, fail

    # mult (-2^31)*(-2^31) = 0x4000000000000000.
    mult  $t0, $t0
    mfhi  $t2
    lui   $t3, 0x4000
    bne   $t2, $t3, fail
    mflo  $t2
    bne   $t2, $zero, fail

    # mult (2^31-1)^2 = 0x3FFFFFFF00000001.
    lui   $t0, 0x7FFF
    ori   $t0, $t0, 0xFFFF
    mult  $t0, $t0
    mfhi  $t2
    lui   $t3, 0x3FFF
    ori   $t3, $t3, 0xFFFF
    bne   $t2, $t3, fail
    mflo  $t2
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail

    # multu 0xFFFFFFFF * 2 = 0x00000001FFFFFFFE.
    addiu $t0, $zero, -1
    addiu $t1, $zero, 2
    multu $t0, $t1
    mfhi  $t2
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail
    mflo  $t2
    addiu $t3, $zero, -2
    bne   $t2, $t3, fail

    # multu 0xFFFFFFFF^2 = 0xFFFFFFFE00000001.
    multu $t0, $t0
    mfhi  $t2
    addiu $t3, $zero, -2
    bne   $t2, $t3, fail
    mflo  $t2
    addiu $t3, $zero, 1
    bne   $t2, $t3, fail

    # multu 0x80000000^2 = 0x4000000000000000.
    lui   $t0, 0x8000
    multu $t0, $t0
    mfhi  $t2
    lui   $t3, 0x4000
    bne   $t2, $t3, fail
    mflo  $t2
    bne   $t2, $zero, fail

    # Qualquer operando zero zera as duas metades.
    multu $t0, $zero
    mfhi  $t2
    bne   $t2, $zero, fail
    mflo  $t2
    bne   $t2, $zero, fail

    # mthi altera apenas HI; mtlo altera apenas LO.
    lui   $t0, 0x1234
    ori   $t0, $t0, 0x5678
    mthi  $t0
    mfhi  $t2
    bne   $t2, $t0, fail
    mflo  $t2
    bne   $t2, $zero, fail

    lui   $t1, 0xFEDC
    ori   $t1, $t1, 0xBA98
    mtlo  $t1
    mflo  $t2
    bne   $t2, $t1, fail
    mfhi  $t2
    bne   $t2, $t0, fail

    # Cada multiplicacao deve sobrescrever HI E LO apos mthi/mtlo.
    addiu $t0, $zero, 6
    addiu $t1, $zero, 7
    mult  $t0, $t1
    mfhi  $t2
    bne   $t2, $zero, fail
    mflo  $t2
    addiu $t3, $zero, 42
    bne   $t2, $t3, fail

    # mthi preserva LO; mtlo preserva HI mesmo com valores negativos.
    addiu $t0, $zero, -1
    mthi  $t0
    mflo  $t2
    bne   $t2, $t3, fail
    mfhi  $t2
    bne   $t2, $t0, fail
    addiu $t1, $zero, -8
    mtlo  $t1
    mfhi  $t2
    bne   $t2, $t0, fail
    mflo  $t2
    bne   $t2, $t1, fail

    # Verifica HI=0 e LO=0 apos mult de zero (signed) tambem.
    mult  $t1, $zero
    mfhi  $t2
    bne   $t2, $zero, fail
    mflo  $t2
    bne   $t2, $zero, fail

    # 0xFC grava 1 somente se TODAS as verificacoes C, C+ e B passaram.
    addiu $t7, $zero, 1
    sw    $t7, 252($zero)
pass_loop:
    j     pass_loop

fail:
    addiu $t7, $zero, 2
    sw    $t7, 252($zero)
fail_loop:
    j     fail_loop

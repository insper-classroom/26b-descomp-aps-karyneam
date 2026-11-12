library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- CPU MIPS single-cycle, conceitos C + C+ + B + B+ (little-endian).
-- Sem branch delay slots e sem excecoes; acessos halfword devem estar alinhados.
-- 'enable' realiza um passo de instrucao sem criar um clock derivado.
entity mips_word_toplevel is
    port (
        clk               : in  std_logic;
        reset             : in  std_logic;
        enable            : in  std_logic;
        debug_pc          : out std_logic_vector(31 downto 0);
        debug_instruction : out std_logic_vector(31 downto 0);
        debug_alu_result  : out std_logic_vector(31 downto 0);
        debug_signature   : out std_logic_vector(31 downto 0)
    );
end entity;

architecture rtl of mips_word_toplevel is
    signal pc             : std_logic_vector(31 downto 0) := (others => '0');
    signal next_pc        : std_logic_vector(31 downto 0);
    signal instruction    : std_logic_vector(31 downto 0);
    signal reg_a, reg_b   : std_logic_vector(31 downto 0);
    signal alu_result     : std_logic_vector(31 downto 0);
    signal ram_data       : std_logic_vector(31 downto 0);
    signal write_data     : std_logic_vector(31 downto 0);
    signal write_addr     : std_logic_vector(4 downto 0);
    signal reg_write      : std_logic;
    signal byte_write     : std_logic_vector(3 downto 0);
    signal mem_data_in    : std_logic_vector(31 downto 0);
    signal reg_write_step : std_logic;
    signal byte_write_step : std_logic_vector(3 downto 0);
    signal signature      : std_logic_vector(31 downto 0) := (others => '0');
    -- B+: registradores especiais HI/LO; cada um armazena 32 bits.
    signal hi_reg, lo_reg : std_logic_vector(31 downto 0) := (others => '0');
    signal hi_next, lo_next : std_logic_vector(31 downto 0);
    signal hi_write, lo_write : std_logic;
begin
    debug_pc          <= pc;
    debug_instruction <= instruction;
    debug_alu_result  <= alu_result;
    debug_signature   <= signature;

    rom_inst : entity work.mips_rom
        port map (
            addr => pc(11 downto 2),
            data => instruction
        );

    reg_write_step <= reg_write and enable;
    byte_write_step <= byte_write when enable = '1' else "0000";

    regs_inst : entity work.reg_file
        port map (
            clk => clk, rst => reset,
            A_addr => instruction(25 downto 21),
            B_addr => instruction(20 downto 16),
            W_addr => write_addr, W_data => write_data,
            W_en => reg_write_step,
            A_data => reg_a, B_data => reg_b
        );

    -- RAM com 4 lanes de byte: preserva lw/sw de C e adiciona C+.
    ram_inst : entity work.mips_ram_bytes
        generic map (memoryAddrWidth => 6)
        port map (
            clk => clk, reset => reset,
            addr => alu_result, data_in => mem_data_in,
            data_out => ram_data, byte_we => byte_write_step
        );

    -- PC e assinatura de teste: o programa escreve 1 (sucesso) ou
    -- 2 (falha) na palavra de endereco 0x000000FC.
    process(clk, reset)
    begin
        if reset = '1' then
            pc <= (others => '0');
            signature <= (others => '0');
            hi_reg <= (others => '0');
            lo_reg <= (others => '0');
        elsif rising_edge(clk) then
            if enable = '1' then
                pc <= next_pc;
                if hi_write = '1' then hi_reg <= hi_next; end if;
                if lo_write = '1' then lo_reg <= lo_next; end if;
                if byte_write = "1111" and alu_result = x"000000FC" then
                    signature <= reg_b;
                end if;
            end if;
        end if;
    end process;

    process(all)
        variable op           : std_logic_vector(5 downto 0);
        variable fn           : std_logic_vector(5 downto 0);
        variable imm_signed   : std_logic_vector(31 downto 0);
        variable imm_unsigned : std_logic_vector(31 downto 0);
        variable plus_four    : std_logic_vector(31 downto 0);
        variable branch_dest  : std_logic_vector(31 downto 0);
        variable shamt        : natural range 0 to 31;
        variable v_alu        : std_logic_vector(31 downto 0);
        variable v_write      : std_logic_vector(31 downto 0);
        variable v_dest       : std_logic_vector(4 downto 0);
        variable v_pc         : std_logic_vector(31 downto 0);
        variable v_regwrite   : std_logic;
        variable v_bytewrite  : std_logic_vector(3 downto 0);
        variable v_memdata    : std_logic_vector(31 downto 0);
        variable selected_byte : std_logic_vector(7 downto 0);
        variable selected_half : std_logic_vector(15 downto 0);
        variable byte_shift   : natural range 0 to 24;
        variable multiplicand  : signed(32 downto 0);
        variable multiplier    : signed(32 downto 0);
        variable product_66    : signed(65 downto 0);
        variable v_hi_next, v_lo_next : std_logic_vector(31 downto 0);
        variable v_hi_write, v_lo_write : std_logic;
    begin
        op := instruction(31 downto 26);
        fn := instruction(5 downto 0);
        shamt := to_integer(unsigned(instruction(10 downto 6)));
        imm_signed   := std_logic_vector(resize(signed(instruction(15 downto 0)), 32));
        imm_unsigned := x"0000" & instruction(15 downto 0);
        plus_four := std_logic_vector(unsigned(pc) + 4);
        branch_dest := std_logic_vector(unsigned(plus_four) +
                       unsigned(shift_left(signed(imm_signed), 2)));

        -- Valores seguros: instrucoes nao reconhecidas nao mudam estado.
        v_alu := (others => '0');
        v_write := (others => '0');
        v_dest := instruction(20 downto 16);
        v_pc := plus_four;
        v_regwrite := '0';
        v_bytewrite := "0000";
        v_memdata := reg_b;
        selected_byte := (others => '0');
        selected_half := (others => '0');
        byte_shift := 0;
        multiplicand := (others => '0');
        multiplier := (others => '0');
        product_66 := (others => '0');
        v_hi_next := hi_reg;
        v_lo_next := lo_reg;
        v_hi_write := '0';
        v_lo_write := '0';

        case op is
            when "000000" =>  -- Tipo R
                v_dest := instruction(15 downto 11);
                case fn is
                    when "100000" | "100001" => -- add / addu
                        v_alu := std_logic_vector(unsigned(reg_a) + unsigned(reg_b));
                        v_regwrite := '1';
                    when "100010" | "100011" => -- sub / subu
                        v_alu := std_logic_vector(unsigned(reg_a) - unsigned(reg_b));
                        v_regwrite := '1';
                    when "101010" => -- slt (signed)
                        if signed(reg_a) < signed(reg_b) then v_alu(0) := '1'; end if;
                        v_regwrite := '1';
                    when "101011" => -- sltu (unsigned)
                        if unsigned(reg_a) < unsigned(reg_b) then v_alu(0) := '1'; end if;
                        v_regwrite := '1';
                    when "100100" => -- and
                        v_alu := reg_a and reg_b;
                        v_regwrite := '1';
                    when "100101" => -- or
                        v_alu := reg_a or reg_b;
                        v_regwrite := '1';
                    when "100110" => -- xor
                        v_alu := reg_a xor reg_b;
                        v_regwrite := '1';
                    when "100111" => -- nor
                        v_alu := not (reg_a or reg_b);
                        v_regwrite := '1';
                    when "000000" => -- sll
                        v_alu := std_logic_vector(shift_left(unsigned(reg_b), shamt));
                        v_regwrite := '1';
                    when "000010" => -- srl
                        v_alu := std_logic_vector(shift_right(unsigned(reg_b), shamt));
                        v_regwrite := '1';
                    when "000011" => -- sra
                        v_alu := std_logic_vector(shift_right(signed(reg_b), shamt));
                        v_regwrite := '1';
                    when "000100" => -- sllv: deslocamento usa apenas rs[4:0]
                        v_alu := std_logic_vector(shift_left(unsigned(reg_b),
                                 to_integer(unsigned(reg_a(4 downto 0)))));
                        v_regwrite := '1';
                    when "000110" => -- srlv
                        v_alu := std_logic_vector(shift_right(unsigned(reg_b),
                                 to_integer(unsigned(reg_a(4 downto 0)))));
                        v_regwrite := '1';
                    when "000111" => -- srav: preserva o bit de sinal
                        v_alu := std_logic_vector(shift_right(signed(reg_b),
                                 to_integer(unsigned(reg_a(4 downto 0)))));
                        v_regwrite := '1';
                    when "011000" | "011001" => -- mult/multu: 32x32 -> HI:LO de 64 bits
                        -- Um unico multiplicador assinado de 33x33: em multu,
                        -- prefixar zero evita interpretar valores unsigned como negativos.
                        if fn = "011000" then
                            multiplicand := resize(signed(reg_a), 33);
                            multiplier := resize(signed(reg_b), 33);
                        else
                            multiplicand := signed('0' & reg_a);
                            multiplier := signed('0' & reg_b);
                        end if;
                        product_66 := multiplicand * multiplier;
                        v_hi_next := std_logic_vector(product_66(63 downto 32));
                        v_lo_next := std_logic_vector(product_66(31 downto 0));
                        v_hi_write := '1';
                        v_lo_write := '1';
                    when "010000" => -- mfhi rd
                        v_alu := hi_reg;
                        v_regwrite := '1';
                    when "010010" => -- mflo rd
                        v_alu := lo_reg;
                        v_regwrite := '1';
                    when "010001" => -- mthi rs: nao modifica LO
                        v_hi_next := reg_a;
                        v_hi_write := '1';
                    when "010011" => -- mtlo rs: nao modifica HI
                        v_lo_next := reg_a;
                        v_lo_write := '1';
                    when "001000" => -- jr
                        v_pc := reg_a;
                    when "001001" => -- jalr rd, rs: link no rd, alvo no rs
                        v_pc := reg_a;
                        v_write := plus_four;
                        v_regwrite := '1';
                    when others => null;
                end case;

            when "001000" | "001001" => -- addi / addiu
                v_alu := std_logic_vector(unsigned(reg_a) + unsigned(imm_signed));
                v_regwrite := '1';
            when "001010" => -- slti (signed)
                if signed(reg_a) < signed(imm_signed) then v_alu(0) := '1'; end if;
                v_regwrite := '1';
            when "001011" => -- sltiu: o imediato e estendido com sinal
                if unsigned(reg_a) < unsigned(imm_signed) then v_alu(0) := '1'; end if;
                v_regwrite := '1';
            when "001100" => -- andi
                v_alu := reg_a and imm_unsigned;
                v_regwrite := '1';
            when "001101" => -- ori
                v_alu := reg_a or imm_unsigned;
                v_regwrite := '1';
            when "001110" => -- xori
                v_alu := reg_a xor imm_unsigned;
                v_regwrite := '1';
            when "001111" => -- lui
                v_alu := instruction(15 downto 0) & x"0000";
                v_regwrite := '1';

            when "100011" => -- lw: palavra completa (C)
                v_alu := std_logic_vector(unsigned(reg_a) + unsigned(imm_signed));
                v_regwrite := '1';
                v_write := ram_data;

            when "100000" | "100100" => -- lb / lbu (C+)
                v_alu := std_logic_vector(unsigned(reg_a) + unsigned(imm_signed));
                case v_alu(1 downto 0) is
                    when "00" => selected_byte := ram_data(7 downto 0);
                    when "01" => selected_byte := ram_data(15 downto 8);
                    when "10" => selected_byte := ram_data(23 downto 16);
                    when others => selected_byte := ram_data(31 downto 24);
                end case;
                if op = "100000" then
                    v_write := std_logic_vector(resize(signed(selected_byte), 32));
                else
                    v_write := x"000000" & selected_byte;
                end if;
                v_regwrite := '1';

            when "100001" | "100101" => -- lh / lhu (C+)
                v_alu := std_logic_vector(unsigned(reg_a) + unsigned(imm_signed));
                if v_alu(0) = '0' then -- apenas halfwords alinhadas
                    if v_alu(1) = '0' then
                        selected_half := ram_data(15 downto 0);
                    else
                        selected_half := ram_data(31 downto 16);
                    end if;
                    if op = "100001" then
                        v_write := std_logic_vector(resize(signed(selected_half), 32));
                    else
                        v_write := x"0000" & selected_half;
                    end if;
                    v_regwrite := '1';
                end if;

            when "101011" => -- sw (C): quatro lanes
                v_alu := std_logic_vector(unsigned(reg_a) + unsigned(imm_signed));
                v_bytewrite := "1111";
                v_memdata := reg_b;

            when "101000" => -- sb (C+): so o byte baixo do rt
                v_alu := std_logic_vector(unsigned(reg_a) + unsigned(imm_signed));
                byte_shift := to_integer(unsigned(v_alu(1 downto 0))) * 8;
                v_bytewrite := std_logic_vector(shift_left(to_unsigned(1, 4),
                                      to_integer(unsigned(v_alu(1 downto 0)))));
                v_memdata := std_logic_vector(shift_left(unsigned(reg_b), byte_shift));

            when "101001" => -- sh (C+): so os 16 bits baixos do rt
                v_alu := std_logic_vector(unsigned(reg_a) + unsigned(imm_signed));
                if v_alu(0) = '0' then
                    byte_shift := to_integer(unsigned(v_alu(1 downto 0))) * 8;
                    if v_alu(1) = '0' then
                        v_bytewrite := "0011";
                    else
                        v_bytewrite := "1100";
                    end if;
                    v_memdata := std_logic_vector(shift_left(unsigned(reg_b), byte_shift));
                end if;

            when "000001" => -- REGIMM: bltz (rt=0), bgez (rt=1)
                case instruction(20 downto 16) is
                    when "00000" => -- bltz
                        if signed(reg_a) < to_signed(0, 32) then
                            v_pc := branch_dest;
                        end if;
                    when "00001" => -- bgez (inclui o zero)
                        if signed(reg_a) >= to_signed(0, 32) then
                            v_pc := branch_dest;
                        end if;
                    when others => null;
                end case;
            when "000110" => -- blez: zero ou negativo
                if instruction(20 downto 16) = "00000" and
                   signed(reg_a) <= to_signed(0, 32) then
                    v_pc := branch_dest;
                end if;
            when "000111" => -- bgtz: estritamente positivo
                if instruction(20 downto 16) = "00000" and
                   signed(reg_a) > to_signed(0, 32) then
                    v_pc := branch_dest;
                end if;
            when "000100" => -- beq
                if reg_a = reg_b then v_pc := branch_dest; end if;
            when "000101" => -- bne
                if reg_a /= reg_b then v_pc := branch_dest; end if;
            when "000010" => -- j
                v_pc := plus_four(31 downto 28) & instruction(25 downto 0) & "00";
            when "000011" => -- jal
                v_pc := plus_four(31 downto 28) & instruction(25 downto 0) & "00";
                v_dest := "11111"; -- $ra = $31
                v_write := plus_four;
                v_regwrite := '1';
            when others => null;
        end case;

        -- Por padrao o writeback vem da ULA; loads, jal e jalr sobrescrevem.
        if op /= "100011" and op /= "100000" and op /= "100100" and
           op /= "100001" and op /= "100101" and op /= "000011" and
           not (op = "000000" and fn = "001001") then
            v_write := v_alu;
        end if;

        alu_result <= v_alu;
        write_data <= v_write;
        write_addr <= v_dest;
        reg_write <= v_regwrite;
        byte_write <= v_bytewrite;
        mem_data_in <= v_memdata;
        next_pc <= v_pc;
        hi_next <= v_hi_next;
        lo_next <= v_lo_next;
        hi_write <= v_hi_write;
        lo_write <= v_lo_write;
    end process;
end architecture;

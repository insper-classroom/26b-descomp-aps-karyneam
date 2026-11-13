library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- Wrapper FPGA Cyclone V: CLOCK_50, KEY[0:1], SW[3:0], LEDR, HEX[0:5].
-- SW(3 downto 1) escolhe o programa (0=autoteste, 1..7=demos).
-- SW(0) = 1: execucao automatica a ~100 instrucoes/s.
-- SW(0) = 0: uma instrucao por pressionamento de KEY(1).
-- KEY(0): reset (ativo em nivel baixo).
entity TOP_LEVEL is
    port (
        CLOCK_50 : in  std_logic;
        KEY      : in  std_logic_vector(3 downto 0);
        SW       : in  std_logic_vector(9 downto 0);
        LEDR     : out std_logic_vector(9 downto 0);
        HEX0     : out std_logic_vector(6 downto 0);
        HEX1     : out std_logic_vector(6 downto 0);
        HEX2     : out std_logic_vector(6 downto 0);
        HEX3     : out std_logic_vector(6 downto 0);
        HEX4     : out std_logic_vector(6 downto 0);
        HEX5     : out std_logic_vector(6 downto 0);
        GPIO_0   : inout std_logic_vector(35 downto 0)
    );
end entity;

architecture rtl of TOP_LEVEL is
    constant AUTO_DIV   : natural := 100_000;   -- 50 MHz / 500000 = 100 Hz
    constant DEBOUNCE   : natural := 1_000_000; -- ~20ms a 50 MHz
    signal reset        : std_logic;
    signal pc, instr, alu, signature : std_logic_vector(31 downto 0);
    signal auto_count   : natural range 0 to AUTO_DIV-1 := 0;
    signal stable_count : natural range 0 to DEBOUNCE := 0;
    signal key_meta     : std_logic := '1';
    signal key_sync     : std_logic := '1';
    signal key_stable   : std_logic := '1';
    signal key_previous : std_logic := '1';
    signal manual_pulse : std_logic := '0';
    signal run_enable   : std_logic;
    signal show_value   : std_logic_vector(23 downto 0);
    signal io_addr, io_wdata, io_rdata : std_logic_vector(31 downto 0);
    signal io_we : std_logic;
    signal lcd_board : std_logic_vector(17 downto 0) := (others => '0');
    signal lcd_cursor : std_logic_vector(3 downto 0) := (others => '0');
    signal lcd_state : std_logic_vector(2 downto 0) := (others => '0');
    signal lcd_ready : std_logic;
    signal lcd_data : std_logic_vector(15 downto 0);
    signal lcd_wr_n, lcd_rd_n, lcd_cs_n, lcd_rs, lcd_reset_n, lcd_on : std_logic;
    signal key_game_meta, key_game_sync : std_logic_vector(1 downto 0) := (others => '1');
    signal game_selected : std_logic;

    function hex7(n : std_logic_vector(3 downto 0)) return std_logic_vector is
    begin
        case n is
            when x"0" => return "1000000";
            when x"1" => return "1111001";
            when x"2" => return "0100100";
            when x"3" => return "0110000";
            when x"4" => return "0011001";
            when x"5" => return "0010010";
            when x"6" => return "0000010";
            when x"7" => return "1111000";
            when x"8" => return "0000000";
            when x"9" => return "0011000";
            when x"A" => return "0001000";
            when x"B" => return "0000011";
            when x"C" => return "1000110";
            when x"D" => return "0100001";
            when x"E" => return "0000110";
            when others => return "0001110"; -- F
        end case;
    end function;
begin
    reset <= not KEY(0);
    game_selected <= '1' when SW(4 downto 1) = "1000" else '0';
    run_enable <= '1' when (SW(0) = '1' and auto_count = AUTO_DIV-1) else
                  manual_pulse when SW(0) = '0' else '0';

    process(CLOCK_50, reset)
    begin
        if reset = '1' then
            auto_count <= 0;
            key_meta <= '1';
            key_sync <= '1';
            key_stable <= '1';
            key_previous <= '1';
            stable_count <= 0;
            manual_pulse <= '0';
            key_game_meta <= (others => '1');
            key_game_sync <= (others => '1');
        elsif rising_edge(CLOCK_50) then
            -- Divisor de clock em forma de clock enable.
            if auto_count = AUTO_DIV-1 then auto_count <= 0;
            else auto_count <= auto_count + 1;
            end if;

            -- Entradas da interface: botoes nativos ja debounced na DE0-CV.
            key_game_meta <= KEY(2 downto 1); -- KEY1: proxima casa; KEY2: confirma; KEY3 sem funcao
            key_game_sync <= key_game_meta;
            -- Dois flip-flops de sincronizacao, seguidos por debounce.
            key_meta <= KEY(1);
            key_sync <= key_meta;
            manual_pulse <= '0';
            key_previous <= key_stable;
            if key_sync = key_stable then
                stable_count <= 0;
            elsif stable_count = DEBOUNCE then
                key_stable <= key_sync;
                stable_count <= 0;
            else
                stable_count <= stable_count + 1;
            end if;
            if key_previous = '1' and key_stable = '0' then
                manual_pulse <= '1';
            end if;
        end if;
    end process;

    cpu : entity work.mips_word_toplevel
        port map (
            clk => CLOCK_50, reset => reset, enable => run_enable,
            rom_bank => SW(4 downto 1),
            io_read_data => io_rdata,
            io_addr => io_addr,
            io_write_data => io_wdata,
            io_write_strobe => io_we,
            debug_pc => pc, debug_instruction => instr,
            debug_alu_result => alu, debug_signature => signature
        );

    -- MMIO 0x100: KEY1 bit0 (proxima) e KEY2 bit1 (confirma).
    io_rdata <= (31 downto 2 => '0') & (not key_game_sync)
                 when io_addr = x"00000100" else (others => '0');
    process(CLOCK_50, reset)
    begin
        if reset = '1' then
            lcd_board <= (others => '0');
            lcd_cursor <= (others => '0');
            lcd_state <= (others => '0');
        elsif rising_edge(CLOCK_50) then
            if io_we = '1' then
                case io_addr is
                    when x"00000104" => lcd_board <= io_wdata(17 downto 0);
                    when x"00000108" => lcd_cursor <= io_wdata(3 downto 0);
                    when x"0000010C" => lcd_state <= io_wdata(2 downto 0);
                    when others => null;
                end case;
            end if;
        end if;
    end process;

    lcd : entity work.lt24_game_display
        port map (
            clk => CLOCK_50, rst => reset,
            board => lcd_board, cursor => lcd_cursor, game_state => lcd_state,
            lcd_data => lcd_data, lcd_wr_n => lcd_wr_n, lcd_rd_n => lcd_rd_n,
            lcd_cs_n => lcd_cs_n, lcd_rs => lcd_rs,
            lcd_reset_n => lcd_reset_n, lcd_on => lcd_on, ready => lcd_ready
        );
    -- GPIO_0: LT24 encaixado no conector GPIO_0 da DE0-CV.
    -- Pinagem fisica 2x20: pino 1=GPIO_0[0], 2=[1], ...
    process(all)
        variable p : std_logic_vector(35 downto 0);
    begin
        p := (others => 'Z');
        p(3) := '0';  -- ADC_DIN sem uso (touch desabilitado)
        p(4) := '0';  -- ADC_DCLK sem uso
        p(5) := lcd_data(3);
        p(6) := lcd_data(2);
        p(7) := lcd_data(1);
        p(8) := lcd_data(0);
        p(10) := lcd_rd_n;
        p(11) := lcd_wr_n;
        p(12) := lcd_rs;
        for i in 4 to 15 loop
            p(i+9) := lcd_data(i);
        end loop;
        p(25) := lcd_cs_n;
        p(33) := lcd_reset_n;
        p(34) := '1'; -- ADC_CS_N: touch desabilitado
        p(35) := lcd_on;
        GPIO_0 <= p;
    end process;

    -- Banco 0: autoteste acumulativo (1=PASS, 2=FAIL).
    -- Bancos 1..7: resultado CALCULADO pelo MIPS gravado em RAM[0xFC].
    -- Falha nos demos escreve 0x00FFFFFF (display FFFFFF).
    LEDR(9) <= lcd_ready when game_selected = '1' else
                '1' when (SW(4 downto 1) = "0000" and signature = x"00000001") or
                          (SW(4 downto 1) /= "0000" and signature /= x"00000000" and
                           signature /= x"00FFFFFF") else '0';
    LEDR(8) <= '1' when game_selected = '1' and unsigned(lcd_state) >= 3 else
                '1' when (SW(4 downto 1) = "0000" and signature = x"00000002") or
                          (SW(4 downto 1) /= "0000" and signature = x"00FFFFFF") else '0';
    LEDR(7) <= '0' when game_selected = '1' else
                '1' when signature = x"00000000" else '0';
    LEDR(6 downto 0) <= pc(8 downto 2);

    -- Banco 0 exibe o PC (word address). Bancos 1..7 exibem o
    -- resultado em HEXADECIMAL, nao em BCD decimal.
    show_value <= (23 downto 8 => '0') & lcd_state & '0' & lcd_cursor
                  when game_selected = '1' else
                  pc(25 downto 2) when SW(4 downto 1) = "0000" else
                  signature(23 downto 0);
    HEX0 <= hex7(show_value(3 downto 0));
    HEX1 <= hex7(show_value(7 downto 4));
    HEX2 <= hex7(show_value(11 downto 8));
    HEX3 <= hex7(show_value(15 downto 12));
    HEX4 <= hex7(show_value(19 downto 16));
    HEX5 <= hex7(show_value(23 downto 20));
end architecture;

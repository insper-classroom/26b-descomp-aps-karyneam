library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- Wrapper FPGA Cyclone V: CLOCK_50, KEY[0:1], SW[0], LEDR, HEX[0:5].
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
        HEX5     : out std_logic_vector(6 downto 0)
    );
end entity;

architecture rtl of TOP_LEVEL is
    constant AUTO_DIV   : natural := 500_000;   -- 50 MHz / 500000 = 100 Hz
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
    signal word_pc      : std_logic_vector(23 downto 0);

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
        elsif rising_edge(CLOCK_50) then
            -- Divisor de clock em forma de clock enable.
            if auto_count = AUTO_DIV-1 then auto_count <= 0;
            else auto_count <= auto_count + 1;
            end if;

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
            debug_pc => pc, debug_instruction => instr,
            debug_alu_result => alu, debug_signature => signature
        );

    -- Auto-teste: assinatura 1 => passou, 2 => falhou, 0 => executando.
    LEDR(9) <= '1' when signature = x"00000001" else '0';
    LEDR(8) <= '1' when signature = x"00000002" else '0';
    LEDR(7) <= '1' when signature = x"00000000" else '0';
    LEDR(6 downto 0) <= pc(8 downto 2);

    -- Os HEX exibem o indice da instrucao (PC / 4), em hexadecimal.
    word_pc <= pc(25 downto 2);
    HEX0 <= hex7(word_pc(3 downto 0));
    HEX1 <= hex7(word_pc(7 downto 4));
    HEX2 <= hex7(word_pc(11 downto 8));
    HEX3 <= hex7(word_pc(15 downto 12));
    HEX4 <= hex7(word_pc(19 downto 16));
    HEX5 <= hex7(word_pc(23 downto 20));
end architecture;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity toplevel_mips is
    port (
        SW   : in  std_logic_vector(9 downto 0);
        KEY  : in  std_logic_vector(3 downto 0);
        LEDR : out std_logic_vector(9 downto 0);
        HEX0 : out std_logic_vector(6 downto 0)
    );
end entity toplevel_mips;


architecture rtl of toplevel_mips is

    component arith_machine is
    port(
        instr        : in  std_logic_vector(31 downto 0);

        rd_src       : in  std_logic;
        wr_enable    : in  std_logic;
        ula_src2     : in  std_logic_vector(1 downto 0);
        ula_op       : in  std_logic_vector(2 downto 0);

        clk           : in  std_logic;
        reset         : in  std_logic;

        overflow      : out std_logic;
        zero          : out std_logic;
        negative      : out std_logic;
        ula_out       : out std_logic_vector(31 downto 0)
    );
    end component;

    signal instr_s     : std_logic_vector(31 downto 0);

    signal rd_src_s    : std_logic;
    signal wr_enable_s : std_logic;
    signal ula_src2_s  : std_logic_vector(1 downto 0);
    signal ula_op_s    : std_logic_vector(2 downto 0);

    signal ula_out_s   : std_logic_vector(31 downto 0);

    signal overflow_s  : std_logic;
    signal zero_s      : std_logic;
    signal negative_s  : std_logic;

    signal cnt          : unsigned(3 downto 0) := (others => '0');



    function hex_to_7seg(
        hex_in : std_logic_vector(3 downto 0)
    ) return std_logic_vector is
    begin

        case hex_in is

            when "0000" => return "1000000"; -- 0
            when "0001" => return "1111001"; -- 1
            when "0010" => return "0100100"; -- 2
            when "0011" => return "0110000"; -- 3
            when "0100" => return "0011001"; -- 4
            when "0101" => return "0010010"; -- 5
            when "0110" => return "0000010"; -- 6
            when "0111" => return "1111000"; -- 7
            when "1000" => return "0000000"; -- 8
            when "1001" => return "0011000"; -- 9

            when others => return "1111111";

        end case;

    end function;


begin
    -- Contador

    process(KEY(0), SW(0))
    begin

        if SW(0) = '1' then

            cnt <= (others => '0');

        elsif rising_edge(KEY(0)) then

            if cnt = 7 then
                cnt <= (others => '0');
            else
                cnt <= cnt + 1;
            end if;

        end if;

    end process;


    process(cnt)
    begin


        instr_s     <= (others => '0');

        rd_src_s    <= '1';
        wr_enable_s <= '0';

        ula_src2_s  <= "01";
        ula_op_s    <= "010"; -- ADD


        case to_integer(cnt) is

            -- TESTE 0
            -- R1 = R0 + 5
            -- 5

            when 0 =>

                -- rs = R0
                instr_s(25 downto 21) <= "00000";

                -- rt = R1
                instr_s(20 downto 16) <= "00001";

                -- imediato = 5
                instr_s(15 downto 0) <= x"0005";

                rd_src_s    <= '1';
                wr_enable_s <= '1';
                ula_src2_s <= "01";
                ula_op_s <= "010";
					 
            -- TESTE 1
            -- R2 = R0 + 3
            -- 3

            when 1 =>

                instr_s(25 downto 21) <= "00000";
                instr_s(20 downto 16) <= "00010";
                instr_s(15 downto 0)  <= x"0003";

                rd_src_s    <= '1';
                wr_enable_s <= '1';

                ula_src2_s <= "01";

                ula_op_s <= "010";

            -- TESTE 2
            -- R3 = R1 + R2
            -- 5 + 3 = 8

            when 2 =>

                -- rs = R1
                instr_s(25 downto 21) <= "00001";

                -- rt = R2
                instr_s(20 downto 16) <= "00010";

                -- rd = R3
                instr_s(15 downto 11) <= "00011";

                rd_src_s    <= '0';
                wr_enable_s <= '1';

                -- segunda entrada = registrador
                ula_src2_s <= "00";

                -- ADD
                ula_op_s <= "010";

            -- TESTE 3
            -- R4 = R1 - R2
            -- 5 - 3 = 2

            when 3 =>

                instr_s(25 downto 21) <= "00001";
                instr_s(20 downto 16) <= "00010";
                instr_s(15 downto 11) <= "00100";

                rd_src_s    <= '0';
                wr_enable_s <= '1';

                ula_src2_s <= "00";

                -- SUB
                ula_op_s <= "011";


            -- TESTE 4
            -- R5 = R1 AND R2
            -- 5 AND 3

            when 4 =>

                instr_s(25 downto 21) <= "00001";
                instr_s(20 downto 16) <= "00010";
                instr_s(15 downto 11) <= "00101";

                rd_src_s    <= '0';
                wr_enable_s <= '1';

                ula_src2_s <= "00";

                -- AND
                ula_op_s <= "100";

            -- TESTE 5
            -- R6 = R1 OR R2
            -- 5 OR 3

            when 5 =>

                instr_s(25 downto 21) <= "00001";
                instr_s(20 downto 16) <= "00010";
                instr_s(15 downto 11) <= "00110";

                rd_src_s    <= '0';
                wr_enable_s <= '1';

                ula_src2_s <= "00";

                -- OR
                ula_op_s <= "101";


            -- TESTE 6
            -- R7 = R1 XOR R2
            -- 5 XOR 3 


            when 6 =>

                instr_s(25 downto 21) <= "00001";
                instr_s(20 downto 16) <= "00010";
                instr_s(15 downto 11) <= "00111";

                rd_src_s    <= '0';
                wr_enable_s <= '1';

                ula_src2_s <= "00";

                -- XOR
                ula_op_s <= "111";

            -- TESTE 7
            -- NOT R1

            when 7 =>

                instr_s(25 downto 21) <= "00001";
                instr_s(20 downto 16) <= "00000";
                instr_s(15 downto 11) <= "01000";

                rd_src_s    <= '0';
                wr_enable_s <= '0';

                ula_src2_s <= "00";

                -- NOT
                ula_op_s <= "110";


            when others =>

                null;

        end case;

    end process;

    U_MIPS : arith_machine
    port map(
        instr     => instr_s,

        rd_src    => rd_src_s,
        wr_enable => wr_enable_s,
        ula_src2  => ula_src2_s,
        ula_op    => ula_op_s,

        clk       => KEY(0),
        reset     => SW(0),

        overflow  => overflow_s,
        zero      => zero_s,
        negative  => negative_s,
        ula_out   => ula_out_s
    );


    LEDR <= ula_out_s(9 downto 0);



    HEX0 <= hex_to_7seg(std_logic_vector(cnt));


end architecture rtl;
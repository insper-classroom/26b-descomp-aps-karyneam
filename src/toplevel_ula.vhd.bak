library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity toplevel_ula is
    port (
        SW   : in  std_logic_vector(9 downto 0);
        LEDR : out std_logic_vector(9 downto 0);
        HEX0 : out std_logic_vector(6 downto 0)
    );
end entity toplevel_ula;

architecture rtl of toplevel_ula is

    component ULA is
        port (
            A             : in std_logic_vector(31 downto 0);
            B             : in  std_logic_vector(31 downto 0);
            control       : in  std_logic_vector(3 downto 0);
            result        : out std_logic_vector(31 downto 0);
            flag_neg      : out std_logic;
            flag_zero     : out std_logic;
            flag_overflow : out std_logic
        );
    end component;

    signal A_32      : std_logic_vector(31 downto 0);
    signal B_32      : std_logic_vector(31 downto 0);
    signal ctrl_4    : std_logic_vector(3 downto 0);
    signal res_32    : std_logic_vector(31 downto 0);
    signal display_4 : std_logic_vector(3 downto 0);

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
            when "1010" => return "0001000"; -- A
            when "1011" => return "0000011"; -- b
            when "1100" => return "1000110"; -- C
            when "1101" => return "0100001"; -- d
            when "1110" => return "0000110"; -- E
            when "1111" => return "0001110"; -- F
            when others => return "1111111";
        end case;
    end function;

begin

    A_32 <= (31 downto 3 => SW(2)) & SW(2 downto 0);
    B_32 <= (31 downto 3 => SW(5)) & SW(5 downto 3);
    ctrl_4 <= SW(9 downto 6);
	 
    U1: ULA
        port map (
            A             => A_32,
            B             => B_32,
            control       => ctrl_4,
            result        => res_32,
            flag_neg      => LEDR(7),
            flag_zero     => LEDR(8),
            flag_overflow => LEDR(9)
        );

    LEDR(6 downto 0) <= (others => '0');

    display_4 <= '0' & res_32(2 downto 0);
    HEX0      <= hex_to_7seg(display_4);

end architecture rtl;
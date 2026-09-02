library ieee;
use ieee.std_logic_1164.all;

entity ULA is
  port (
    A             : in  std_logic_vector(31 downto 0);
    B             : in  std_logic_vector(31 downto 0);
    control       : in  std_logic_vector(2 downto 0);
    result        : out std_logic_vector(31 downto 0);
    flag_neg      : out std_logic;
    flag_zero     : out std_logic;
    flag_overflow : out std_logic
  );
end entity ULA;

architecture rtl of ULA is

    component ula_32bits is
    port(
        a, b      : in  std_logic_vector(31 downto 0);
        control   : in  std_logic_vector(2 downto 0);
        outi      : out std_logic_vector(31 downto 0);
        cout30    : out std_logic;
        cout      : out std_logic
    );
    end component;

    component flags is
    port(
        c_out31       : in  std_logic;
        c_out30       : in  std_logic;
        ula_out       : in  std_logic_vector(31 downto 0);
        flag_neg      : out std_logic;
        flag_zero     : out std_logic;
        flag_overflow : out std_logic
    );
    end component;

    signal internal_result : std_logic_vector(31 downto 0);
    signal c30, c31        : std_logic;

begin

    u_ula_32bits : ula_32bits
        port map (
            a       => A,
            b       => B,
            control => control,
            outi    => internal_result,
            cout30  => c30,
            cout    => c31
        );

    u_flags : flags
        port map (
            c_out31       => c31,
            c_out30       => c30,
            ula_out       => internal_result,
            flag_neg      => flag_neg,
            flag_zero     => flag_zero,
            flag_overflow => flag_overflow
        );

    result <= internal_result;

end architecture;
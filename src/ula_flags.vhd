library ieee;
use ieee.std_logic_1164.all;

-------------------------------------------------
entity flags is
port(
    -- dados da saída da ULA
    c_out31      : in  std_logic;
    c_out30      : in  std_logic;
    ula_out      : in  std_logic_vector(31 downto 0);

    flag_neg     : out std_logic;
    flag_zero    : out std_logic;
    flag_overflow: out std_logic
);
end flags;

-------------------------------------------------

architecture behv1 of flags is

begin
flag_zero <= '1' when ula_out = "00000000000000000000000000000000" else '0';
flag_overflow <= c_out31 xor c_out30;
flag_neg <= ula_out(31);
end behv1;

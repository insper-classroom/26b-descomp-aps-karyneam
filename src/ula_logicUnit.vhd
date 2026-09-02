library ieee;
use ieee.std_logic_1164.all;

-------------------------------------------------
entity logicUnit is
port(
    a, b : in  std_logic;
    s    : in  std_logic_vector(1 downto 0);
    y    : out std_logic
);
end logicUnit;

-------------------------------------------------

architecture behv1 of logicUnit is
begin
y <= (a and b) when s = "00" else
 (a or b) when s = "01" else
 (a nor b) when s = "10" else
 (a xor b);

end behv1;

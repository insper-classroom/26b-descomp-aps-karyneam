-------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-------------------------------------------------

entity sign_extender is
port(	
   imm16         : 	in  std_logic_vector(15 downto 0);
   sign_ext_imm  : 	out  std_logic_vector(31 downto 0)
);
end sign_extender;

architecture behv1 of sign_extender is

begin

sign_ext_imm <= (31 downto 16 => imm16(15)) & imm16;


end behv1;

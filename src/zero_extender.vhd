-------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-------------------------------------------------

entity zero_extender is
port(	
   imm16  : 	in  std_logic_vector(15 downto 0);
   zero_ext_imm  : 	out  std_logic_vector(31 downto 0)
);
end zero_extender;

architecture behv1 of zero_extender is	
begin

    zero_ext_imm <= "0000000000000000" & imm16;

		 
end behv1;

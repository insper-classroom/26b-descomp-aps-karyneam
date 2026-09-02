library ieee;
use ieee.std_logic_1164.all;

-------------------------------------------------

entity ula_32bits is
port(
    a, b      : in  std_logic_vector(31 downto 0);
    control   : in  std_logic_vector( 2 downto 0);
    outi      : out std_logic_vector(31 downto 0);
    cout      : out std_logic);
end ula_32bits;

architecture behv1 of ula_32bits is

component ula_1bit is
port(
    a, b, cin : in  std_logic;
    control   : in  std_logic_vector(2 downto 0);
    outi, cout: out std_logic
);
end component;

signal c: std_logic_vector(32 downto 0);

begin

c(0) <= control(0);

gen_ula : for i in 0 to 31 generate
    ula : ula_1bit
    port map (
    a => a(i),
    b => b(i),
    cin => c(i),
    control => control,
    outi => outi(i),
    cout => c(i+1)
    );
end generate gen_ula;

cout <= c(32);




end behv1;

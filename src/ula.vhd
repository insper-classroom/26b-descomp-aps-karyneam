library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

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

architecture behv of ULA is
begin

    process(A, B, control)
        variable resultado : std_logic_vector(31 downto 0);
        variable overflow  : std_logic;
    begin

        resultado := (others => '0');
        overflow  := '0';

        case control is

            -- Soma signed
            when "010" =>
                resultado := std_logic_vector(signed(A) + signed(B));

                if (A(31) = B(31)) and
                   (resultado(31) /= A(31)) then
                    overflow := '1';
                end if;

            -- Subtração signed
            when "011" =>
                resultado := std_logic_vector(signed(A) - signed(B));

                if (A(31) /= B(31)) and
                   (resultado(31) /= A(31)) then
                    overflow := '1';
                end if;

            -- AND
            when "100" =>
                resultado := A and B;

            -- OR
            when "101" =>
                resultado := A or B;

            -- XOR
            when "111" =>
                resultado := A xor B;

            -- NOT A
            when "110" =>
                resultado := not A;

            when others =>
                resultado := (others => '0');

        end case;

        result <= resultado;

        flag_neg <= resultado(31);

        flag_overflow <= overflow;

        if resultado = x"00000000" then
            flag_zero <= '1';
        else
            flag_zero <= '0';
        end if;

    end process;

end architecture behv;
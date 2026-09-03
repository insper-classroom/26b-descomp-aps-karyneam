library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity ULA is
    port (
        A             : in  std_logic_vector(31 downto 0);
        B             : in  std_logic_vector(31 downto 0);
        control       : in  std_logic_vector(3 downto 0);
        result        : out  std_logic_vector(31 downto 0);
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
        -- Valores padrão
        resultado := (others => '0');
        overflow  := '0';

        case control is

            -- Soma signed
            when "0000" =>
                resultado := std_logic_vector(signed(A) + signed(B));

                -- Overflow para números signed de 3 bits
                if (A(2) = B(2)) and
                   (resultado(2) /= A(2)) then
                    overflow := '1';
                end if;

            -- Subtração signed
            when "0001" =>
                resultado := std_logic_vector(signed(A) - signed(B));

                -- Overflow para números signed de 3 bits
                if (A(2) /= B(2)) and
                   (resultado(2) /= A(2)) then
                    overflow := '1';
                end if;

            -- AND
            when "0010" =>
                resultado := A and B;

            -- OR
            when "0011" =>
                resultado := A or B;

            -- XOR
            when "0100" =>
                resultado := A xor B;

            -- NOT A
            when "0101" =>
                resultado := not A;

            -- Operações não utilizadas
            when others =>
                resultado := (others => '0');

        end case;

        -- Resultado da operação
        result <= resultado;

        -- Flag de negativo: bit de sinal do resultado de 3 bits
        flag_neg <= resultado(2);

        -- Flag de overflow
        flag_overflow <= overflow;

        -- Flag de zero
        if resultado(2 downto 0) = "000" then
            flag_zero <= '1';
        else
            flag_zero <= '0';
        end if;

    end process;

end architecture behv;
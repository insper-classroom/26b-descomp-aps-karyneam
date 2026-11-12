library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- RAM little-endian com 4 enables independentes por byte.
-- Endereco de entrada em BYTES; memoria de demonstracao = 64 palavras (256B).
-- Cada lane pode ser escrita sem alterar as demais.
-- Mantem leitura combinacional, necessaria ao datapath single-cycle.
entity mips_ram_bytes is
    generic (memoryAddrWidth : positive := 6);
    port (
        clk      : in  std_logic;
        reset    : in  std_logic;
        addr     : in  std_logic_vector(31 downto 0);
        data_in  : in  std_logic_vector(31 downto 0);
        byte_we  : in  std_logic_vector(3 downto 0);
        data_out : out std_logic_vector(31 downto 0)
    );
end entity;

architecture rtl of mips_ram_bytes is
    type byte_array is array (0 to 2**memoryAddrWidth - 1)
        of std_logic_vector(7 downto 0);
    signal lane0 : byte_array := (others => (others => '0'));
    signal lane1 : byte_array := (others => (others => '0'));
    signal lane2 : byte_array := (others => (others => '0'));
    signal lane3 : byte_array := (others => (others => '0'));
    signal word_index : integer range 0 to 2**memoryAddrWidth - 1;
begin
    word_index <= to_integer(unsigned(addr(memoryAddrWidth+1 downto 2)));
    data_out <= lane3(word_index) & lane2(word_index) &
                lane1(word_index) & lane0(word_index);

    process(clk, reset)
    begin
        if reset = '1' then
            lane0 <= (others => (others => '0'));
            lane1 <= (others => (others => '0'));
            lane2 <= (others => (others => '0'));
            lane3 <= (others => (others => '0'));
        elsif rising_edge(clk) then
            if byte_we(0) = '1' then
                lane0(word_index) <= data_in(7 downto 0);
            end if;
            if byte_we(1) = '1' then
                lane1(word_index) <= data_in(15 downto 8);
            end if;
            if byte_we(2) = '1' then
                lane2(word_index) <= data_in(23 downto 16);
            end if;
            if byte_we(3) = '1' then
                lane3(word_index) <= data_in(31 downto 24);
            end if;
        end if;
    end process;
end architecture;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- LT24: ILI9341, barramento 8080 paralelo de 16 bits, 240x320, RGB565.
-- Controlador original, sem framebuffer: renderiza as 9 casas a cada mudanca.
-- Uma maquina sequencial produz reset, configuracao, janela e pixels.
entity lt24_game_display is
    port (
        clk       : in  std_logic;
        rst       : in  std_logic;
        board     : in  std_logic_vector(17 downto 0);
        cursor    : in  std_logic_vector(3 downto 0);
        game_state: in  std_logic_vector(2 downto 0);
        lcd_data  : out std_logic_vector(15 downto 0);
        lcd_wr_n  : out std_logic;
        lcd_rd_n  : out std_logic;
        lcd_cs_n  : out std_logic;
        lcd_rs    : out std_logic;
        lcd_reset_n : out std_logic;
        lcd_on    : out std_logic;
        ready     : out std_logic
    );
end entity;

architecture rtl of lt24_game_display is
    type state_t is (RESET_LOW, RESET_HIGH, INIT_STEP, INIT_PAUSE,
                     WINDOW_STEP, PIXEL_STEP, NEXT_PIXEL, FRAME_END,
                     SEND_SETUP, SEND_LOW, SEND_HIGH);
    signal state : state_t := RESET_LOW;
    signal resume : state_t := INIT_STEP;
    signal wait_counter : integer range 0 to 6_000_000 := 0;
    signal pulse_counter : integer range 0 to 7 := 0;
    signal init_idx : integer range 0 to 127 := 0;
    signal window_idx : integer range 0 to 10 := 0;
    signal pixel_idx : integer range 0 to 76799 := 0;
    signal scan_x : integer range 0 to 239 := 0;
    signal scan_y : integer range 0 to 319 := 0;
    signal tx : std_logic_vector(15 downto 0) := (others => '0');
    signal tx_data : std_logic := '0';
    signal latched_board : std_logic_vector(17 downto 0) := (others => '0');
    signal latched_cursor : std_logic_vector(3 downto 0) := (others => '0');
    signal latched_state : std_logic_vector(2 downto 0) := (others => '0');
    signal initial_frame_done : std_logic := '0';

    -- A inicializacao segue a sequencia classica do controlador ILI9341.
    -- msb bit 8 = 1 significa dado (RS=1), bit 8 = 0 comando.
    type words_t is array(natural range <>) of std_logic_vector(8 downto 0);
    constant INIT : words_t := (
        '0'&x"01", -- SWRESET
        '0'&x"EF", '1'&x"03", '1'&x"80", '1'&x"02",
        '0'&x"CF", '1'&x"00", '1'&x"C1", '1'&x"30",
        '0'&x"ED", '1'&x"64", '1'&x"03", '1'&x"12", '1'&x"81",
        '0'&x"E8", '1'&x"85", '1'&x"00", '1'&x"78",
        '0'&x"CB", '1'&x"39", '1'&x"2C", '1'&x"00", '1'&x"34", '1'&x"02",
        '0'&x"F7", '1'&x"20",
        '0'&x"EA", '1'&x"00", '1'&x"00",
        '0'&x"C0", '1'&x"23",
        '0'&x"C1", '1'&x"10",
        '0'&x"C5", '1'&x"3E", '1'&x"28",
        '0'&x"C7", '1'&x"86",
        '0'&x"36", '1'&x"48", -- MADCTL
        '0'&x"3A", '1'&x"55", -- RGB565
        '0'&x"B1", '1'&x"00", '1'&x"18",
        '0'&x"B6", '1'&x"08", '1'&x"82", '1'&x"27",
        '0'&x"F2", '1'&x"00",
        '0'&x"26", '1'&x"01",
        '0'&x"E0", '1'&x"0F", '1'&x"31", '1'&x"2B", '1'&x"0C", '1'&x"0E",
                  '1'&x"08", '1'&x"4E", '1'&x"F1", '1'&x"37", '1'&x"07",
                  '1'&x"10", '1'&x"03", '1'&x"0E", '1'&x"09", '1'&x"00",
        '0'&x"E1", '1'&x"00", '1'&x"0E", '1'&x"14", '1'&x"03", '1'&x"11",
                  '1'&x"07", '1'&x"31", '1'&x"C1", '1'&x"48", '1'&x"08",
                  '1'&x"0F", '1'&x"0C", '1'&x"31", '1'&x"36", '1'&x"0F",
        '0'&x"11", -- EXIT_SLEEP: aguardar 120ms antes de DISPON
        '0'&x"29"  -- DISPLAY_ON
    );
    constant LAST_INIT : integer := INIT'length-1;

    constant WINDOW : words_t := (
        '0'&x"2A", '1'&x"00", '1'&x"00", '1'&x"00", '1'&x"EF",
        '0'&x"2B", '1'&x"00", '1'&x"00", '1'&x"01", '1'&x"3F",
        '0'&x"2C"
    );

    function abs_i(v : integer) return integer is
    begin
        if v < 0 then return -v; else return v; end if;
    end function;

    function pixel_color(x, y : integer;
                         b : std_logic_vector(17 downto 0);
                         c : std_logic_vector(3 downto 0);
                         st : std_logic_vector(2 downto 0)) return std_logic_vector is
        variable col, row, index, dx, dy, ax, ay : integer;
        variable symbol : std_logic_vector(1 downto 0);
        variable chosen : integer;
        variable maxabs : integer;
    begin
        -- Plano de fundo azul escuro
        if y < 32 then
            if st = "011" then return x"07E0"; end if; -- X venceu: verde
            if st = "100" then return x"F81F"; end if; -- O venceu: rosa
            if st = "101" then return x"FFE0"; end if; -- empate: amarelo
            if st = "010" then return x"F81F"; end if; -- vez do O
            return x"03FF"; -- vez do X
        end if;
        if x < 15 or x >= 225 or y < 60 or y >= 270 then
            return x"1082";
        end if;
        if x < 85 then col := 0; dx := x-50;
        elsif x < 155 then col := 1; dx := x-120;
        else col := 2; dx := x-190; end if;
        if y < 130 then row := 0; dy := y-95;
        elsif y < 200 then row := 1; dy := y-165;
        else row := 2; dy := y-235; end if;
        index := row*3+col;
        ax := abs_i(dx); ay := abs_i(dy);
        if ax >= 33 or ay >= 33 then return x"FFFF"; end if;
        chosen := to_integer(unsigned(c));
        if index = chosen and (ax >= 30 or ay >= 30) then return x"FFE0"; end if;
        symbol := b(2*index+1 downto 2*index);
        if symbol = "01" then
            if (ax <= 23 and ay <= 23) and
               (abs_i(dx-dy) <= 3 or abs_i(dx+dy) <= 3) then
                return x"07FF"; -- X ciano
            end if;
        elsif symbol = "10" then
            maxabs := ax;
            if ay > maxabs then maxabs := ay; end if;
            -- O como anel octogonal: evita multiplicadores no renderer.
            if maxabs >= 20 and maxabs <= 25 and ax+ay <= 38 then
                return x"F81F"; -- O magenta
            end if;
        end if;
        return x"2104";
    end function;
begin
    lcd_data <= tx;
    lcd_rs <= tx_data;
    lcd_cs_n <= '0';
    lcd_rd_n <= '1';
    lcd_wr_n <= '0' when state = SEND_LOW else '1';
    lcd_reset_n <= '0' when state = RESET_LOW else '1';
    lcd_on <= '1';
    ready <= initial_frame_done;

    process(clk, rst)
    begin
        if rst = '1' then
            state <= RESET_LOW;
            wait_counter <= 0;
            pulse_counter <= 0;
            init_idx <= 0;
            window_idx <= 0;
            pixel_idx <= 0;
            scan_x <= 0;
            scan_y <= 0;
            tx <= (others => '0');
            tx_data <= '0';
            latched_board <= (others => '0');
            latched_cursor <= (others => '0');
            latched_state <= (others => '0');
            initial_frame_done <= '0';
            resume <= INIT_STEP;
        elsif rising_edge(clk) then
            case state is
                when RESET_LOW =>
                    if wait_counter = 250_000 then
                        wait_counter <= 0;
                        state <= RESET_HIGH;
                    else wait_counter <= wait_counter+1; end if;
                when RESET_HIGH =>
                    if wait_counter = 250_000 then
                        wait_counter <= 0;
                        init_idx <= 0;
                        state <= INIT_STEP;
                    else wait_counter <= wait_counter+1; end if;
                when INIT_STEP =>
                    tx_data <= INIT(init_idx)(8);
                    tx <= x"00" & INIT(init_idx)(7 downto 0);
                    resume <= INIT_STEP;
                    state <= SEND_SETUP;
                    if init_idx = LAST_INIT then
                        init_idx <= 0;
                        resume <= WINDOW_STEP;
                        window_idx <= 0;
                        latched_board <= board;
                        latched_cursor <= cursor;
                        latched_state <= game_state;
                    elsif init_idx = LAST_INIT-1 or init_idx = 0 then
                        init_idx <= init_idx+1;
                        resume <= INIT_PAUSE;
                    else
                        init_idx <= init_idx+1;
                    end if;
                when INIT_PAUSE =>
                    if wait_counter = 6_000_000 then
                        wait_counter <= 0;
                        state <= INIT_STEP;
                    else wait_counter <= wait_counter+1; end if;
                when WINDOW_STEP =>
                    tx_data <= WINDOW(window_idx)(8);
                    tx <= x"00" & WINDOW(window_idx)(7 downto 0);
                    state <= SEND_SETUP;
                    if window_idx = 10 then
                        window_idx <= 0;
                        pixel_idx <= 0;
                        scan_x <= 0;
                        scan_y <= 0;
                        resume <= PIXEL_STEP;
                    else
                        window_idx <= window_idx + 1;
                        resume <= WINDOW_STEP;
                    end if;
                when PIXEL_STEP =>
                    tx <= pixel_color(scan_x,scan_y,latched_board,
                                      latched_cursor,latched_state);
                    tx_data <= '1';
                    resume <= NEXT_PIXEL;
                    state <= SEND_SETUP;
                when NEXT_PIXEL =>
                    if pixel_idx = 76799 then
                        state <= FRAME_END;
                        initial_frame_done <= '1';
                    else
                        pixel_idx <= pixel_idx+1;
                        if scan_x = 239 then
                            scan_x <= 0;
                            scan_y <= scan_y+1;
                        else
                            scan_x <= scan_x+1;
                        end if;
                        state <= PIXEL_STEP;
                    end if;
                when FRAME_END =>
                    if board /= latched_board or cursor /= latched_cursor or
                       game_state /= latched_state then
                        latched_board <= board;
                        latched_cursor <= cursor;
                        latched_state <= game_state;
                        window_idx <= 0;
                        state <= WINDOW_STEP;
                    end if;
                when SEND_SETUP =>
                    pulse_counter <= 0;
                    state <= SEND_LOW;
                when SEND_LOW =>
                    if pulse_counter = 3 then
                        pulse_counter <= 0;
                        state <= SEND_HIGH;
                    else pulse_counter <= pulse_counter+1; end if;
                when SEND_HIGH =>
                    if pulse_counter = 2 then
                        pulse_counter <= 0;
                        state <= resume;
                    else pulse_counter <= pulse_counter+1; end if;
            end case;
        end if;
    end process;
end architecture;

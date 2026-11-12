SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl
TOPLEVEL ?= ula
MODULE ?= test_ula

# O core usa process(all), recurso de VHDL-2008.
ifeq ($(SIM),ghdl)
    EXTRA_ARGS += --std=08
endif

ifeq ($(TOPLEVEL),mips_word_toplevel)
    VHDL_SOURCES = $(PWD)/../src/reg_file.vhd
    VHDL_SOURCES += $(PWD)/../src/mips_ram_bytes.vhd
    VHDL_SOURCES += $(PWD)/../src/mips_rom.vhd
    VHDL_SOURCES += $(PWD)/../src/mips_word_toplevel.vhd
else ifeq ($(TOPLEVEL),mips_rom)
    VHDL_SOURCES = $(PWD)/../src/mips_rom.vhd
else ifeq ($(TOPLEVEL),mips_ram_bytes)
    VHDL_SOURCES = $(PWD)/../src/mips_ram_bytes.vhd
else ifeq ($(TOPLEVEL),mips_ram)
    VHDL_SOURCES = $(PWD)/../src/mips_ram.vhd
else ifeq ($(TOPLEVEL),reg_file)
    VHDL_SOURCES = $(PWD)/../src/reg_file.vhd
else
    VHDL_SOURCES = $(PWD)/../src/ula_fullAdder.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_logicUnit.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_1bit.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_flags.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_32bits.vhd
    VHDL_SOURCES += $(PWD)/../src/ula.vhd
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

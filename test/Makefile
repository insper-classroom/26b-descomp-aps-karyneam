
SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

TOPLEVEL ?= ula
MODULE ?= test_ula

ifeq ($(TOPLEVEL),mips_rom)
    VHDL_SOURCES = $(PWD)/../src/mips_rom.vhd

else ifeq ($(TOPLEVEL),mips_ram)
    VHDL_SOURCES = $(PWD)/../src/mips_ram.vhd

else
    VHDL_SOURCES = $(PWD)/../src/ula_fullAdder.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_logicUnit.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_1bit.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_flags.vhd
    VHDL_SOURCES += $(PWD)/../src/ula_32bits.vhd
    VHDL_SOURCES += $(PWD)/../src/ula.vhd
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

SIM ?= ghdl
TOPLEVEL_LANG ?= vhdl

VHDL_SOURCES += $(PWD)/../src/ula_fullAdder.vhd
VHDL_SOURCES += $(PWD)/../src/ula_logicUnit.vhd
VHDL_SOURCES += $(PWD)/../src/ula_1bit.vhd
VHDL_SOURCES += $(PWD)/../src/ula_flags.vhd
VHDL_SOURCES += $(PWD)/../src/ula_32bits.vhd
VHDL_SOURCES += $(PWD)/../src/ula.vhd

TOPLEVEL = ula

MODULE = test_ula

include $(shell cocotb-config --makefiles)/Makefile.sim
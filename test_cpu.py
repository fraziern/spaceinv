import pytest
from CPU import CPU
from State import State, reg_codes
import opcodebytes

# 
def test_nop(cpu, state):
    state.ram[0] = opcodebytes.NOP
    cpu.run_cycle()
    for r in reg_codes:
        assert state.get_reg(r) == 0x00

def test_mov_m_b(cpu, state):
    state.set_reg('hl', 0x3345)
    state.set_reg('b', 0xf3)
    state.ram[0] = opcodebytes.MOV_M_B
    cpu.run_cycle()
    assert state.get_ram(0x3345) == 0xf3

def test_mov_c_m(cpu, state):
    state.set_reg('hl', 0x3345)
    state.ram[0x3345] = 0xf3
    state.ram[0] = opcodebytes.MOV_C_M
    cpu.run_cycle()
    assert state.get_reg('c') == 0xf3

def test_mov_c_b(cpu, state):
    state.set_reg('c', 0x45)
    state.set_reg('b', 0xf3)
    state.ram[0] = opcodebytes.MOV_C_B
    cpu.run_cycle()
    assert state.get_reg('c') == 0xf3

def test_mvi_e(cpu, state):
    state.ram[0:2] = [opcodebytes.MVI_E, 0x8f]
    cpu.run_cycle()
    assert state.get_reg('e') == 0x8f

def test_mvi_m(cpu, state):
    state.set_reg('hl', 0x3345)
    state.ram[0:2] = [opcodebytes.MVI_M, 0x8f]
    cpu.run_cycle()
    assert state.get_ram(0x3345) == 0x8f

def test_lxi_sp(cpu, state):
    state.ram[0:3] = [opcodebytes.LXI_SP, 0x38, 0x9f]
    cpu.run_cycle()
    assert state.get_sp() == 0x9f38

def test_lda(cpu, state):
    state.ram[0x3345] = 0xf3
    state.ram[0:3] = [opcodebytes.LDA, 0x45, 0x33]
    cpu.run_cycle()
    assert state.get_reg('a') == 0xf3

def test_sta(cpu, state):
    state.set_reg('a', 0xe2)
    state.ram[0:3] = [opcodebytes.STA, 0x41, 0x33]
    cpu.run_cycle()
    assert state.get_ram(0x3341) == 0xe2

def test_lhld(cpu, state):
    state.ram[0:3] = [opcodebytes.LHLD, 0x44, 0x23]
    state.ram[0x2344:0x2346] = [0x11, 0x22]
    cpu.run_cycle()
    assert state.get_reg('h') == 0x22
    assert state.get_reg('l') == 0x11

@pytest.fixture
def state():
    return State()

@pytest.fixture
def cpu(state):
    return CPU(state)
import pytest
from CPU import CPU
from State import State, reg_indices
import opcodebytes

# state tests
def test_set_ram_bad_location(state):
    with pytest.raises(IndexError):
        state.set_ram(0xffff, 0xff)

# instruction tests
def test_nop(cpu, state):
    state.ram[0] = opcodebytes.NOP
    cpu.run_cycle()
    for r in reg_indices:
        assert state.get_reg(r) == 0x00

# moves
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

def test_shld(cpu, state):
    state.ram[0:3] = [opcodebytes.SHLD, 0x44, 0x23]
    state.set_reg('h', 0x73)
    state.set_reg('l', 0xd4)
    cpu.run_cycle()
    assert state.get_ram(0x2344) == 0xd4
    assert state.get_ram(0x2345) == 0x73

def test_ldax_b(cpu, state):
    state.ram[0] = opcodebytes.LDAX_B
    state.set_reg('bc', 0x2349)
    state.ram[0x2349] = 0xf3
    cpu.run_cycle()
    assert state.get_reg('a') == 0xf3

def test_stax_d(cpu, state):
    state.ram[0] = opcodebytes.STAX_D
    state.set_reg('de', 0x2349)
    state.set_reg('a', 0x88)
    cpu.run_cycle()
    assert state.get_ram(0x2349) == 0x88

def test_xchg(cpu, state):
    state.ram[0] = opcodebytes.XCHG
    state.set_reg('hl', 0x2339)
    state.set_reg('de', 0xff4d)
    cpu.run_cycle()
    assert state.get_reg('hl') == 0xff4d
    assert state.get_reg('de') == 0x2339

# arithmetic
def test_add(cpu, state):
    state.set_reg('d', 0xd3)
    state.set_reg('a', 0x01)
    state.ram[0] = opcodebytes.ADD_D
    cpu.run_cycle()
    assert state.get_reg('a') == 0xd4
    # check parity
    assert state.get_flag('p') == True
    # check sign
    assert state.get_flag('s') == True

def test_add_carry(cpu, state):
    pass

def test_add_aux_carry(cpu, state):
    pass

def test_add_zero(cpu, state):
    # check parity too
    # check sign
    pass

@pytest.fixture
def state():
    return State()

@pytest.fixture
def cpu(state):
    return CPU(state)
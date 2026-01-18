import pytest
from CPU import CPU
from State import State, reg_indices
import opcodebytes

# state tests
def test_set_ram_bad_location(state):
    with pytest.raises(IndexError):
        state.set_ram(0xffff, 0xff)

def test_set_reg(state):
    state.set_reg('c', 0xff)
    assert state.get_reg('c') == 0xff

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
def test_add_d(cpu, state):
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
    state.set_reg('c', 0xff)
    state.set_reg('a', 0x01)
    state.ram[0] = opcodebytes.ADD_C
    cpu.run_cycle()
    assert state.get_reg('a') == 0x00
    # check parity
    assert state.get_flag('p') == True
    # check carry
    assert state.get_flag('c') == True

def test_add_aux_carry(cpu, state):
    state.set_reg('d', 0x0f)
    state.set_reg('a', 0x01)
    state.ram[0] = opcodebytes.ADD_D
    cpu.run_cycle()
    assert state.get_reg('a') == 0x10
    # check aux carry
    assert state.get_flag('ac') == True

def test_add_zero(cpu, state):
    state.set_reg('c', 0xff)
    state.set_reg('a', 0x01)
    state.ram[0] = opcodebytes.ADD_C
    cpu.run_cycle()
    assert state.get_flag('z') == True
    # check parity too
    assert state.get_flag('p') == True
    # check sign
    assert state.get_flag('s') == False

def test_add_m(cpu, state):
    state.set_reg('hl', 0x2225)
    state.set_reg('a', 0xff)
    state.ram[0] = opcodebytes.ADD_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0x01
    assert state.get_flag('c') == True

def test_adi(cpu, state):
    state.ram[0:2] = [opcodebytes.ADI, 0x56]
    state.set_reg('a', 0x50)
    cpu.run_cycle()
    assert state.get_reg('a') == 0xa6

def test_adc_c(cpu, state):
    state.set_flag('c', True)
    state.set_reg('c', 0x40)
    state.set_reg('a', 0x05)
    state.ram[0] = opcodebytes.ADC_C
    cpu.run_cycle()
    assert state.get_reg('a') == 0x46

def test_adc_m(cpu, state):
    state.set_flag('c', False)
    state.set_reg('hl', 0x2225)
    state.set_reg('a', 0xff)
    state.ram[0] = opcodebytes.ADC_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0x01
    assert state.get_flag('c') == True

def test_aci(cpu, state):
    state.ram[0:2] = [opcodebytes.ACI, 0x56]
    state.set_reg('a', 0x50)
    state.set_flag('c', True)
    cpu.run_cycle()
    assert state.get_reg('a') == 0xa7

def test_sub_b_with_borrow(cpu, state):
    state.ram[0] = opcodebytes.SUB_B
    state.set_reg('a', 0x50)
    state.set_reg('b', 0x55)
    cpu.run_cycle()
    assert state.get_reg('a') == 0b11111011 # 2s complement = -5
    assert state.get_flag('c') == True

def test_sub_a(cpu, state):
    state.ram[0] = opcodebytes.SUB_A
    state.set_reg('a', 0x50)
    cpu.run_cycle()
    assert state.get_reg('a') == 0
    assert state.get_flag('c') == False
    assert state.get_flag('z') == True
    assert state.get_flag('p') == True

def test_sub_m(cpu, state):
    state.set_reg('hl', 0x2225)
    state.set_reg('a', 0xff)
    state.ram[0] = opcodebytes.SUB_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0xfd
    assert state.get_flag('c') == False

def test_sbb_d(cpu, state):
    state.ram[0] = opcodebytes.SBB_D
    state.set_reg('a', 0x50)
    state.set_reg('d', 0xff)
    state.set_flag('c', True)
    cpu.run_cycle()
    assert state.get_reg('a') == 80 # 2s commplement low 8 bits of -176
    assert state.get_flag('c') == True
    assert state.get_flag('z') == False
    assert state.get_flag('p') == True

def test_sbb_m(cpu, state):
    state.set_flag('c', True)
    state.set_reg('hl', 0x2225)
    state.set_reg('a', 0xff)
    state.ram[0] = opcodebytes.SBB_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0xfc
    assert state.get_flag('c') == False

def test_sui(cpu, state):
    state.ram[0:2] = [opcodebytes.SUI, 0x6d]
    state.set_reg('a', 0x80)
    cpu.run_cycle()
    assert state.get_reg('a') == (0x80 - 0x6d)

def test_sbi(cpu, state):
    state.ram[0:2] = [opcodebytes.SBI, 0x6d]
    state.set_reg('a', 0x80)
    state.set_flag('c', True)
    cpu.run_cycle()
    assert state.get_reg('a') == (0x80 - 0x6d - 1)

def test_inr_h(cpu, state):
    state.ram[0] = opcodebytes.INR_H
    state.set_reg('h', 0xff)
    state.set_flag('c', False)
    cpu.run_cycle()
    assert state.get_reg('h') == 0
    assert state.get_flag('c') == False
    assert state.get_flag('z') == True

def test_inr_m(cpu, state):
    state.ram[0] = opcodebytes.INR_M
    state.ram[0x478] = 0x56
    state.set_reg('hl', 0x478)
    cpu.run_cycle()
    assert state.get_ram(0x478) == 0x57
    assert state.get_flag('p') == False # odd

def test_dcr_c(cpu, state):
    state.ram[0] = opcodebytes.DCR_C
    state.set_reg('c', 0xff)
    cpu.run_cycle()
    assert state.get_reg('c') == 0xfe

def test_dcr_b(cpu, state):
    state.ram[0] = opcodebytes.DCR_B
    state.set_reg('b', 0x00)
    cpu.run_cycle()
    assert state.get_reg('b') == 0xff

def test_inx_b(cpu, state):
    state.ram[0] = opcodebytes.INX_B
    state.set_reg('bc', 0x4545)
    cpu.run_cycle()
    assert state.get_reg('bc') == 0x4546

def test_dcx_sp(cpu, state):
    state.ram[0] = opcodebytes.DCX_SP
    state.set_reg('sp', 0x0001)
    cpu.run_cycle()
    assert state.get_reg('sp') == 0x0000

def test_dad_b(cpu, state):
    state.ram[0] = opcodebytes.DAD_B
    state.set_reg('bc', 0xffff)
    state.set_reg('hl', 0x0010)
    cpu.run_cycle()
    assert state.get_reg('hl') == 0x000f
    assert state.get_flag('c') == True


@pytest.fixture
def state():
    return State()

@pytest.fixture
def cpu(state):
    return CPU(state)
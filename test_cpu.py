import pytest
from CPU import CPU
from State import State, reg_indices
from Bus import Bus
from opcodebytes import Opcodebytes

# state tests
def test_set_ram_bad_location(state):
    with pytest.raises(IndexError):
        state.set_ram(0xffff, 0xff)

def test_set_reg(state):
    state.set_reg('c', 0xff)
    assert state.get_reg('c') == 0xff

# instruction tests
def test_nop(cpu, state):
    state.ram[0] = Opcodebytes.NOP
    cpu.run_cycle()
    for r in reg_indices:
        assert state.get_reg(r) == 0x00

# moves
def test_mov_m_b(cpu, state):
    state.set_reg('hl', 0x3345)
    state.set_reg('b', 0xf3)
    state.ram[0] = Opcodebytes.MOV_M_B
    cpu.run_cycle()
    assert state.get_ram(0x3345) == 0xf3

def test_mov_c_m(cpu, state):
    state.set_reg('hl', 0x3345)
    state.ram[0x3345] = 0xf3
    state.ram[0] = Opcodebytes.MOV_C_M
    cpu.run_cycle()
    assert state.get_reg('c') == 0xf3

def test_mov_c_b(cpu, state):
    state.set_reg('c', 0x45)
    state.set_reg('b', 0xf3)
    state.ram[0] = Opcodebytes.MOV_C_B
    cpu.run_cycle()
    assert state.get_reg('c') == 0xf3

def test_mvi_e(cpu, state):
    state.ram[0:2] = [Opcodebytes.MVI_E, 0x8f]
    cpu.run_cycle()
    assert state.get_reg('e') == 0x8f

def test_mvi_m(cpu, state):
    state.set_reg('hl', 0x3345)
    state.ram[0:2] = [Opcodebytes.MVI_M, 0x8f]
    cpu.run_cycle()
    assert state.get_ram(0x3345) == 0x8f

def test_lxi_sp(cpu, state):
    state.ram[0:3] = [Opcodebytes.LXI_SP, 0x38, 0x9f]
    cpu.run_cycle()
    assert state.get_sp() == 0x9f38

def test_lda(cpu, state):
    state.ram[0x3345] = 0xf3
    state.ram[0:3] = [Opcodebytes.LDA, 0x45, 0x33]
    cpu.run_cycle()
    assert state.get_reg('a') == 0xf3

def test_sta(cpu, state):
    state.set_reg('a', 0xe2)
    state.ram[0:3] = [Opcodebytes.STA, 0x41, 0x33]
    cpu.run_cycle()
    assert state.get_ram(0x3341) == 0xe2

def test_lhld(cpu, state):
    state.ram[0:3] = [Opcodebytes.LHLD, 0x44, 0x23]
    state.ram[0x2344:0x2346] = [0x11, 0x22]
    cpu.run_cycle()
    assert state.get_reg('h') == 0x22
    assert state.get_reg('l') == 0x11

def test_shld(cpu, state):
    state.ram[0:3] = [Opcodebytes.SHLD, 0x44, 0x23]
    state.set_reg('h', 0x73)
    state.set_reg('l', 0xd4)
    cpu.run_cycle()
    assert state.get_ram(0x2344) == 0xd4
    assert state.get_ram(0x2345) == 0x73

def test_ldax_b(cpu, state):
    state.ram[0] = Opcodebytes.LDAX_B
    state.set_reg('bc', 0x2349)
    state.ram[0x2349] = 0xf3
    cpu.run_cycle()
    assert state.get_reg('a') == 0xf3

def test_stax_d(cpu, state):
    state.ram[0] = Opcodebytes.STAX_D
    state.set_reg('de', 0x2349)
    state.set_reg('a', 0x88)
    cpu.run_cycle()
    assert state.get_ram(0x2349) == 0x88

def test_xchg(cpu, state):
    state.ram[0] = Opcodebytes.XCHG
    state.set_reg('hl', 0x2339)
    state.set_reg('de', 0xff4d)
    cpu.run_cycle()
    assert state.get_reg('hl') == 0xff4d
    assert state.get_reg('de') == 0x2339

# arithmetic
def test_add_d(cpu, state):
    state.set_reg('d', 0xfe)
    state.set_reg('a', 0x01)
    state.ram[0] = Opcodebytes.ADD_D
    cpu.run_cycle()
    assert state.get_reg('a') == 0xff
    # check parity
    assert state.get_flag('p') == True
    # check sign
    assert state.get_flag('c') == False

def test_add_a(cpu, state):
    state.set_reg('a', 0x88)
    state.ram[0] = Opcodebytes.ADD_A
    cpu.run_cycle()
    assert state.get_reg('a') == 0x10
    # check carry
    assert state.get_flag('c') == True
    # check sign
    assert state.get_flag('s') == False

def test_add_carry(cpu, state):
    state.set_reg('c', 0xff)
    state.set_reg('a', 0x01)
    state.ram[0] = Opcodebytes.ADD_C
    cpu.run_cycle()
    assert state.get_reg('a') == 0x00
    # check parity
    assert state.get_flag('p') == True
    # check carry
    assert state.get_flag('c') == True

def test_add_aux_carry(cpu, state):
    state.set_reg('d', 0x0f)
    state.set_reg('a', 0x01)
    state.ram[0] = Opcodebytes.ADD_D
    cpu.run_cycle()
    assert state.get_reg('a') == 0x10
    # check aux carry
    assert state.get_flag('a') == True

def test_add_zero(cpu, state):
    state.set_reg('c', 0xff)
    state.set_reg('a', 0x01)
    state.ram[0] = Opcodebytes.ADD_C
    cpu.run_cycle()
    assert state.get_flag('z') == True
    # check parity too
    assert state.get_flag('p') == True
    # check sign
    assert state.get_flag('s') == False

def test_add_m(cpu, state):
    state.set_reg('hl', 0x2225)
    state.set_reg('a', 0xff)
    state.ram[0] = Opcodebytes.ADD_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0x01
    assert state.get_flag('c') == True

def test_adi(cpu, state):
    state.ram[0:2] = [Opcodebytes.ADI, 0x56]
    state.set_reg('a', 0x50)
    cpu.run_cycle()
    assert state.get_reg('a') == 0xa6

def test_adc_c(cpu, state):
    state.set_flag('c', True)
    state.set_reg('c', 0x40)
    state.set_reg('a', 0x05)
    state.ram[0] = Opcodebytes.ADC_C
    cpu.run_cycle()
    assert state.get_reg('a') == 0x46

def test_adc_m(cpu, state):
    state.set_flag('c', False)
    state.set_reg('hl', 0x2225)
    state.set_reg('a', 0xff)
    state.ram[0] = Opcodebytes.ADC_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0x01
    assert state.get_flag('c') == True

def test_aci(cpu, state):
    state.ram[0:2] = [Opcodebytes.ACI, 0x56]
    state.set_reg('a', 0x50)
    state.set_flag('c', True)
    cpu.run_cycle()
    assert state.get_reg('a') == 0xa7

def test_sub_b_with_borrow(cpu, state):
    state.ram[0] = Opcodebytes.SUB_B
    state.set_reg('a', 0x50)
    state.set_reg('b', 0x55)
    cpu.run_cycle()
    assert state.get_reg('a') == 0b11111011 # 2s complement = -5
    assert state.get_flag('c') == True

def test_sub_a(cpu, state):
    state.ram[0] = Opcodebytes.SUB_A
    state.set_reg('a', 0x50)
    cpu.run_cycle()
    assert state.get_reg('a') == 0
    assert state.get_flag('c') == False
    assert state.get_flag('z') == True
    assert state.get_flag('p') == True

def test_sub_m(cpu, state):
    state.set_reg('hl', 0x2225)
    state.set_reg('a', 0xff)
    state.ram[0] = Opcodebytes.SUB_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0xfd
    assert state.get_flag('c') == False

def test_sbb_d(cpu, state):
    state.ram[0] = Opcodebytes.SBB_D
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
    state.ram[0] = Opcodebytes.SBB_M
    state.ram[0x2225] = 0x02
    cpu.run_cycle()
    assert state.get_reg('a') == 0xfc
    assert state.get_flag('c') == False

def test_sui(cpu, state):
    state.ram[0:2] = [Opcodebytes.SUI, 0x6d]
    state.set_reg('a', 0x80)
    cpu.run_cycle()
    assert state.get_reg('a') == (0x80 - 0x6d)

def test_sbi(cpu, state):
    state.ram[0:2] = [Opcodebytes.SBI, 0x6d]
    state.set_reg('a', 0x80)
    state.set_flag('c', True)
    cpu.run_cycle()
    assert state.get_reg('a') == (0x80 - 0x6d - 1)

def test_inr_h(cpu, state):
    state.ram[0] = Opcodebytes.INR_H
    state.set_reg('h', 0xff)
    state.set_flag('c', False)
    cpu.run_cycle()
    assert state.get_reg('h') == 0
    assert state.get_flag('c') == False
    assert state.get_flag('z') == True

def test_inr_m(cpu, state):
    state.ram[0] = Opcodebytes.INR_M
    state.ram[0x478] = 0x56
    state.set_reg('hl', 0x478)
    cpu.run_cycle()
    assert state.get_ram(0x478) == 0x57
    assert state.get_flag('p') == False # odd

def test_dcr_c(cpu, state):
    state.ram[0] = Opcodebytes.DCR_C
    state.set_reg('c', 0xff)
    cpu.run_cycle()
    assert state.get_reg('c') == 0xfe

def test_dcr_b(cpu, state):
    state.ram[0] = Opcodebytes.DCR_B
    state.set_reg('b', 0x00)
    cpu.run_cycle()
    assert state.get_reg('b') == 0xff

def test_inx_b(cpu, state):
    state.ram[0] = Opcodebytes.INX_B
    state.set_reg('bc', 0x4545)
    cpu.run_cycle()
    assert state.get_reg('bc') == 0x4546

def test_dcx_sp(cpu, state):
    state.ram[0] = Opcodebytes.DCX_SP
    state.set_reg('sp', 0x0001)
    cpu.run_cycle()
    assert state.get_reg('sp') == 0x0000

def test_dad_b(cpu, state):
    state.ram[0] = Opcodebytes.DAD_B
    state.set_reg('bc', 0xffff)
    state.set_reg('hl', 0x0010)
    cpu.run_cycle()
    assert state.get_reg('hl') == 0x000f
    assert state.get_flag('c') == True

def test_daa(cpu, state):
    state.ram[0] = Opcodebytes.DAA
    state.set_reg('a', 0x9b)
    cpu.run_cycle()
    assert state.get_reg('a') == 1
    assert state.get_flag('a') == True
    assert state.get_flag('c') == True

def test_ana_b(cpu, state):
    state.ram[0] = Opcodebytes.ANA_B
    state.set_reg('b', 0xdd)
    state.set_reg('a', 0xd5)
    cpu.run_cycle()
    assert state.get_reg('a') == 213
    assert state.get_flag('c') == False
    assert state.get_flag('p') == False

def test_ana_m(cpu, state):
    state.ram[0] = Opcodebytes.ANA_M
    state.set_reg('hl', 0x2222)
    state.ram[0x2222] = 0xd5
    state.set_reg('a', 0xdd)
    cpu.run_cycle()
    assert state.get_reg('a') == 213

def test_ani(cpu, state):
    state.ram[0:2] = [Opcodebytes.ANI, 0xd5]
    state.set_reg('a', 0xdd)
    cpu.run_cycle()
    assert state.get_reg('a') == 213

def test_xra_c(cpu, state):
    state.ram[0] = Opcodebytes.XRA_C
    state.set_reg('c', 0xdd)
    state.set_reg('a', 0xd5)
    cpu.run_cycle()
    assert state.get_reg('a') == 8
    assert state.get_flag('c') == False

def test_ora_c(cpu, state):
    state.ram[0] = Opcodebytes.ORA_C
    state.set_reg('c', 0xdd)
    state.set_reg('a', 0xd5)
    cpu.run_cycle()
    assert state.get_reg('a') == 221
    assert state.get_flag('c') == False

def test_cmp_e(cpu, state):
    state.ram[0] = Opcodebytes.CMP_E
    state.set_reg('e', 0x05)
    state.set_reg('a', 0x0a)
    cpu.run_cycle()
    assert state.get_flag('c') == False
    assert state.get_flag('z') == False
    assert state.get_reg('a') == 0x0a

def test_rlc(cpu, state):
    state.ram[0] = Opcodebytes.RLC
    state.set_reg('a', 0xf2)
    cpu.run_cycle()
    assert state.get_reg('a') == 0xe5
    assert state.get_flag('c') == True

def test_rrc(cpu, state):
    state.ram[0] = Opcodebytes.RRC
    state.set_reg('a', 0xf2)
    cpu.run_cycle()
    assert state.get_reg('a') == 0x79
    assert state.get_flag('c') == False

def test_ral(cpu, state):
    state.ram[0] = Opcodebytes.RAL
    state.set_reg('a', 0xb5)
    cpu.run_cycle()
    assert state.get_reg('a') == 0x6a
    assert state.get_flag('c') == True

def test_rar(cpu, state):
    state.ram[0] = Opcodebytes.RAR
    state.set_reg('a', 0x6a)
    state.set_flag('c',True)
    cpu.run_cycle()
    assert state.get_reg('a') == 0xb5
    assert state.get_flag('c') == False

def test_cma(cpu, state):
    state.ram[0] = Opcodebytes.CMA
    state.set_reg('a', 0x51)
    cpu.run_cycle()
    assert state.get_reg('a') == 0xae

def test_cmc(cpu, state):
    state.ram[0] = Opcodebytes.CMC
    state.set_flag('c', False)
    cpu.run_cycle()
    assert state.get_flag('c') == True

def test_stc(cpu, state):
    state.ram[0:2] = [Opcodebytes.STC, Opcodebytes.STC]
    state.set_flag('c', False)
    cpu.run_cycle()
    assert state.get_flag('c') == True
    cpu.run_cycle()
    assert state.get_flag('c') == True

# jump instructions
def test_jmp(cpu, state):
    state.ram[0:2] = [Opcodebytes.JMP, 0x20, 0x21]
    cpu.run_cycle()
    assert state.get_pc() == 0x2120

def test_jpo(cpu, state):
    state.ram[0:2] = [Opcodebytes.JPO, 0x20, 0x21]
    state.set_flag('p', False)
    cpu.run_cycle()
    assert state.get_pc() == 0x2120

# call instructions
def test_call(cpu, state):
    state.ram[0:2] = [Opcodebytes.CALL, 0x20, 0x21]
    cpu.run_cycle()
    assert state.get_ram(state.get_sp()) == 0x0003 # stack @ stack pointer should point to instruction 3
    state.ram[0x2120] = Opcodebytes.STC # set-carry-flag instruction
    cpu.run_cycle()
    assert state.get_flag('c') == True

def test_cc_notset(cpu, state):
    state.ram[0:2] = [Opcodebytes.CC, 0x20, 0x21]
    cpu.run_cycle()
    assert state.get_pc() == 0x0003

def test_cc_set(cpu, state):
    state.ram[0:2] = [Opcodebytes.CC, 0x20, 0x21]
    state.set_flag('c',True)
    cpu.run_cycle()
    assert state.get_ram(state.get_sp()) == 0x0003 # stack @ stack pointer should point to instruction 3
    assert state.get_pc() == 0x2120

def test_ret(cpu, state):
    state.ram[0:2] = [Opcodebytes.CALL, 0x20, 0x21]
    state.ram[0x2120] = Opcodebytes.RET
    cpu.run_cycle()
    cpu.run_cycle()
    assert state.get_pc() ==0x0003

def test_rst(cpu, state):
    state.ram[0] = Opcodebytes.RST_1 # call $8
    cpu.run_cycle()
    assert state.get_pc() == 0x0008

def test_pchl(cpu, state):
    state.ram[0] = Opcodebytes.PCHL
    state.set_reg('hl', 0x2120)
    cpu.run_cycle()
    assert state.get_pc() == 0x2120

def test_push(cpu, state):
    sp_start = state.get_sp()
    state.ram[0] = Opcodebytes.PUSH_B
    state.set_reg('bc', 0x6a77)
    cpu.run_cycle()
    assert state.get_sp() == sp_start - 2
    assert state.get_ram(state.get_sp()) == 0x77

def test_pop(cpu, state):
    state.ram[0:2] = [Opcodebytes.PUSH_D, Opcodebytes.POP_D]
    state.set_reg('de', 0x6a77)
    cpu.run_cycle()
    state.set_reg('de', 0)
    cpu.run_cycle()
    assert state.get_reg('de') == 0x6a77

def test_pushpsw(cpu, state):
    state.ram[0] = Opcodebytes.PUSH_PSW
    state.set_flags({'a':True, 'c':True})
    state.set_reg('a', 0x74)
    cpu.run_cycle()
    assert state.get_ram(state.get_sp()) == 0b00010011
    assert state.get_ram(state.get_sp() + 1) == 0x74

def test_poppsw(cpu, state):
    state.ram[0:2] = [Opcodebytes.PUSH_PSW, Opcodebytes.POP_PSW]
    state.set_flags({'a':True, 'c':True})
    state.set_reg('a', 0x74)
    cpu.run_cycle()
    state.set_flags({'a':False, 'c':False})
    cpu.run_cycle()
    assert state.get_flag('a') == True

def test_xthl(cpu, state):
    state.ram[0:3] = [Opcodebytes.PUSH_B, Opcodebytes.XTHL, Opcodebytes.POP_B]
    state.set_reg('hl', 0x2120)
    state.set_reg('bc', 0x6a77)
    cpu.run_cycle()
    cpu.run_cycle()
    cpu.run_cycle()
    assert state.get_reg('hl') == 0x6a77
    assert state.get_reg('bc') == 0x2120

def test_sphl(cpu, state):
    state.ram[0] = Opcodebytes.SPHL
    state.set_reg('hl', 0x2120)
    cpu.run_cycle()
    assert state.get_sp() == 0x2120

def test_add_then_daa(cpu, state):
    state.ram[0:3] = [0x3e, 0x88, 0x87, 0x27]
    cpu.run_cycle()
    cpu.run_cycle()
    assert state.get_flag('c') == True
    assert state.get_flag('a') == True
    cpu.run_cycle()
    assert state.get_reg('a') == 0x76

def test_daa_cnc(cpu, state):
    state.ram[0:3] = [0x3e, 0xaa, 0x27]
    cpu.run_cycle()
    cpu.run_cycle()
    assert state.get_flag('c') == True
    assert state.get_flag('a') == True


@pytest.fixture
def state():
    return State()

@pytest.fixture
def bus():
    return Bus()

@pytest.fixture
def cpu(state, bus):
    return CPU(state, bus)
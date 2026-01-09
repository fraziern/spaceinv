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


def test_lxi_sp(cpu, state):
    state.ram[0:3] = [opcodebytes.LXI_SP, 0x38, 0x9f]
    cpu.run_cycle()
    for r in reg_codes:
        assert state.get_sp() == 0x9f38


@pytest.fixture
def state():
    return State()

@pytest.fixture
def cpu(state):
    return CPU(state)
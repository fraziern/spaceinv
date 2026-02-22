import pytest
from Bus import Bus
from State import State

def test_shift_write(bus):
    bus.write(4, 0xaa)
    assert bus.shift_register == 0xaa00
    bus.write(4, 0xff)
    assert bus.shift_register == 0xffaa

def test_shift_read(bus):
    bus.write(4, 0xaa)
    bus.write(4, 0xff)
    assert bus.read(3) == 0xff

def test_shift_read_offset(bus):
    bus.write(4, 0xaa)
    bus.write(4, 0xff)
    bus.write(2, 2)
    # result should be 254
    assert bus.read(3) == 0xfe
    bus.write(2, 0)
    assert bus.read(3) == 0xff

def test_decode_sound_signal(bus):
    bits = bus._decode_sound_signal(3, 0b00001010)
    assert (3,1) in bits
    assert (3,3) in bits

@pytest.fixture
def state():
    return State()

@pytest.fixture
def bus(state):
    return Bus(state)
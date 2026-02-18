import pytest
from Bus import Bus

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

@pytest.fixture
def bus():
    return Bus()
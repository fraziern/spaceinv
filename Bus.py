from State import State
from Soundboard import Soundboard

class Bus():

    SOUNDBOARD_WIRING = {
        # (port, bit): sound index
        (3, 0): 0,
        (3, 1): 1,
        (3, 2): 2,
        (3, 3): 3,
        (5, 0): 4,
        (5, 1): 5,
        (5, 2): 6,
        (5, 3): 7,
        (5, 4): 8,
    }

    def __init__(self, state:State, soundboard:Soundboard=None):
        self.state = state
        self.soundboard = soundboard
    
    def write(self, port:int, value:int):
        if not isinstance(value, int):
            raise TypeError("Bus value must be int.")
        self.state.set_writebus(port, value % 256)
        if port in [3, 5]: # discrete sounds
            self._sound_signal(port, value)
        if port == 4:  # run bit shift
            self._shift()
    
    def read(self, port):
        if port == 3: # shift
            offset = self.state.get_writebus(2) & 0b00000111
            return (self.state.get_shift_register() >> (8 - offset)) % 256
        return self.state.get_readbus(port)
    
    def set_read_bit(self, port:int, bit:int, value:bool):
        current_value = self.state.get_readbus(port)
        new_value = self._update_bit(current_value, bit, value)
        self.state.set_readbus(port, new_value)

    def set_write_bit(self, port:int, bit:int, value:bool):
        pass

    def _update_bit(self, value:int, bit_index:int, new_bit:bool):
        # Clear the bit first, then set it if new_value is 1
        mask = ~(1 << bit_index)
        return (value & mask) | (new_bit << bit_index)
    
    def _shift(self):
        newvalue = self.state.get_shift_register() >> 8
        newvalue |= (self.state.get_writebus(4) << 8)
        self.state.set_shift_register(newvalue % 65_535) # 16 bit

    def _decode_sound_signal(self, port, value):
        # build a list of "on" bits
        set_bits = []
        for offset in range(5): # only first 5 bits could have sound signals
            trigger = (1 << offset) & value
            if trigger:
                set_bits.append((port, offset))
        return set_bits

    def _sound_signal(self, port, value):
        set_pins = self._decode_sound_signal(port, value)
        for pin in set_pins: # pin is (port, bit)
            sound_index = self.SOUNDBOARD_WIRING[pin]
            self.soundboard.play(sound_index)


                




    

    
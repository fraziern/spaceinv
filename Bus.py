from State import State

class Bus():

    def __init__(self, state:State):
        self.state = state
    
    def write(self, port:int, value:int):
        if not isinstance(value, int):
            raise TypeError("Bus value must be int.")
        self.state.set_writebus(port, value % 256)
        if port == 4:  # run bit shift
            self._shift()
    
    def read(self, port):
        if port == 3: # shift
            offset = self.state.get_writebus(2) & 0b00000111
            return (self.state.get_shift_register() >> (8 - offset)) % 256
        return self.state.get_readbus(port)
    
    def _shift(self):
        newvalue = self.state.get_shift_register() >> 8
        newvalue |= (self.state.get_writebus(4) << 8)
        self.state.set_shift_register(newvalue % 65_535) # 16 bit





    

    
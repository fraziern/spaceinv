class Bus():

    def __init__(self):
        self.writebus = [0] * 7
        self.readbus = [0] * 4
        self.shift_register = 0x0000 # 16 bit register

    
    def write(self, port:int, value:int):
        if not isinstance(value, int):
            raise TypeError("Bus value must be int.")
        
        self.writebus[port] = value % 256

        if port == 4:  # run bit shift
            self._shift()
    
    def read(self, port):
        if port == 3: # shift
            offset = self.writebus[2] & 0b00000111
            return (self.shift_register >> (8 - offset)) % 256
        return self.readbus[port]
    
    def _shift(self):
        newvalue = self.shift_register >> 8
        newvalue |= (self.writebus[4] << 8)
        self.shift_register = newvalue % 65_535 # 16 bit





    

    
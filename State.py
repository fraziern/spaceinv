reg_codes = {
        'b':0,
        'c':1,
        'd':2,
        'e':3,
        'h':4,
        'l':5,
        'a':6,
    }

class State():

    ROMSTART = 0x0000
    STACKSTART = 0x23FF
    MEMORY_SIZE = 16384


    def __init__(self):
        self.registers = bytearray(7)
        self.pc = self.ROMSTART
        self.ram = bytearray(self.MEMORY_SIZE)
        self.sp = self.STACKSTART
        self.ir = bytearray(3)


    def __str__(self):
        string = ""
        string += f'PC: {self.pc:4X}\n'
        string += f'Registers: {self.registers.hex(" ")}'
        return string


    def set_reg(self, reg_code, value):
        if type(value) == bytes or type(value) == bytearray:
            value = int.from_bytes(value)
        if reg_code in reg_codes:
            register = reg_codes[reg_code]
            self.registers[register] = value % 0xff
        elif reg_code in ['bc','de','hl']:
            register1, register2 = (reg_codes[reg_code[0]], reg_codes[reg_code[1]])
            self.registers[register1] = (value >> 8) & 0xff
            self.registers[register2] = value & 0xff
        elif reg_code =='sp':
            self.sp = value & 0xffff
        else:
            raise ValueError(f"Attempting to set non-existent register: {reg_code}")
        

    def get_reg(self, reg_code):
        if reg_code in reg_codes:
            register = reg_codes[reg_code]
            return self.registers[register]
        elif reg_code in ['bc','de','hl']:
            register1, register2 = (reg_codes[reg_code[0]], reg_codes[reg_code[1]])
            return (self.registers[register1] << 8) | self.registers[register2]
        elif reg_code == 'sp':
            return self.sp
        else:
            raise ValueError(f"Attempting to read non-existent register: {reg_code}")
    

    def get_sp(self):
        # convenience method
        return self.get_reg('sp')
    
    
    def increment_pc(self):
        self.pc = (self.pc + 1) % self.MEMORY_SIZE


    def get_pc(self):
        return self.pc
    

    def set_pc(self, value):
        self.pc = value % self.MEMORY_SIZE
    
    
    # convenience method
    def get_byte_at_pc(self):
        return self.get_ram(self.pc)
    

    def get_ram(self, address):
        if address < len(self.ram):
            return self.ram[address]
        else:
            raise IndexError(f"Attempting to read invalid RAM location: {address:4X}")


    def set_ram(self, address, value):
        if address < len(self.ram):
            self.ram[address] = value % 256
        else:
            raise IndexError("Attempting to write to invalid RAM location: {address:4X}")


    # def get_ram(self,length=1,address=None):
    #     # TODO checks
    #     # defaults to reading from location that index points to
    #     if address == None:
    #         address = self.index
    #     return self.ram[address:address+length]
    
    # def set_ram(self, data, address=None):
    #     if address == None:
    #         address = self.index
    #     if type(data) == int:
    #         data = data.to_bytes(1)
    #     elif type(data) == list:
    #         data = bytes(data)
    #     if type(data) != bytearray and type(data) != bytes:
    #         raise ValueError(f"Attempting to set RAM with wrong data type: {type(data)}")
    #     if address + len(data) > 4096:
    #         raise OverflowError("Out of memory while writing to RAM.")
    #     self.ram[address:address+len(data)] = data

    # def set_delay_timer(self, value):
    #     self.delay_timer = value
    
    # def get_delay_timer(self):
    #     return self.delay_timer
    
    # def set_sound_timer(self, value):
    #     self.sound_timer = value
    
    # def decrement_delay_timer(self):
    #     self.delay_timer = max(self.delay_timer - 1, 0)
    #     return self.delay_timer

    # def decrement_sound_timer(self):
    #     self.sound_timer = max(self.sound_timer - 1, 0)  
    #     return self.sound_timer

    # def stack_push(self, value):
    #     self.stack.append(value)

    # def stack_pop(self):
    #     if len(self.stack) <= 0:
    #         raise IndexError("Attempting to pop from empty stack.")
    #     return self.stack.pop()
    
    # def clear_key_state(self):
    #     self.key_state = [False]*16
    
    # def set_key_state(self,key:int,value:bool):
    #     if key >= 16 or key < 0:
    #         raise ValueError("Key value out of range.")
    #     if type(value) != bool:
    #         raise TypeError("Key state value must be a boolean.")
    #     self.key_state[key] = value
    
    # def get_key_state(self,key=None):
    #     if key == None:
    #         return self.key_state
    #     elif key >= 16 or key < 0:
    #         raise ValueError("Key value out of range.")
    #     else:
    #         return self.key_state[key]


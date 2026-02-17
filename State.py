from utils import bits_to_int, byte_to_bits

reg_indices = {
    'b':0,
    'c':1,
    'd':2,
    'e':3,
    'h':4,
    'l':5,
    'a':6,
    }

flag_indices = {
    's':0,
    'z':1,
    'a':3,
    'p':5,
    'c':7
}

class State():

    ROMSTART = 0x0000
    STACKSTART = 0x23FF
    MEMORY_SIZE = 16384


    def __init__(self, romstart=None):
        self.registers = bytearray(7)
        self.pc = self.ROMSTART if romstart is None else romstart
        self.ram = bytearray(self.MEMORY_SIZE)
        self.sp = self.STACKSTART
        self.flags = [0,0,0,0,0,0,1,0]

    def __str__(self):
        string = ""
        string += f'PC: {self.pc:4X}\n'
        string += f'Registers: ' + " ".join(
            [f'{reg}:{self.get_reg(reg):X} ' for reg in 'bcdehla']) + '\n'
        string += f'Flags: ' + " ".join(
            [f'{flag}:{self.get_flag(flag)} ' for flag in 'szapc'])
        return string


    def get_flag(self, flag:str) -> bool:
        return bool(self.flags[flag_indices[flag]])
    
    def set_flag(self, flag:str, value:bool):
        self.flags[flag_indices[flag]] = int(value)
    
    def set_flags(self, values:dict[str, bool]):
        for (flag,value) in values.items():
            self.set_flag(flag, value)

    def get_psw(self) -> int:
        # convenience function for getting PSW
        return bits_to_int(self.flags)
    
    def set_psw(self, psw:int):
        self.flags = byte_to_bits(psw)


    def set_reg(self, reg_code, value):
        if type(value) == bytes or type(value) == bytearray:
            value = int.from_bytes(value)
        if reg_code in reg_indices:
            register = reg_indices[reg_code]
            self.registers[register] = value % 256
        elif reg_code in ['bc','de','hl']:
            register1, register2 = (reg_indices[reg_code[0]], reg_indices[reg_code[1]])
            self.registers[register1] = (value >> 8) & 0xff
            self.registers[register2] = value & 0xff
        elif reg_code =='sp':
            self.sp = value & 0xffff
        else:
            raise ValueError(f"Attempting to set non-existent register: {reg_code}")
        
    def get_reg(self, reg_code):
        if reg_code in reg_indices:
            register = reg_indices[reg_code]
            return self.registers[register]
        elif reg_code in ['bc','de','hl']:
            register1, register2 = (reg_indices[reg_code[0]], reg_indices[reg_code[1]])
            return (self.registers[register1] << 8) | self.registers[register2]
        elif reg_code == 'sp':
            return self.sp
        else:
            raise ValueError(f"Attempting to read non-existent register: {reg_code}")
    
    def get_sp(self):
        return self.sp
    
    def set_sp(self, value):
        self.sp = value % self.MEMORY_SIZE

    def increment_pc(self):
        self.pc = (self.pc + 1) % self.MEMORY_SIZE

    def get_pc(self):
        return self.pc
    
    def set_pc(self, value):
        self.pc = value % self.MEMORY_SIZE
    
    # convenience method
    def get_byte_at_pc(self):
        return self.get_ram(self.pc)
    

    def get_ram(self, address_or_reg, end_address=None):
        address = self.get_reg(address_or_reg) if isinstance(address_or_reg, 
                                                             str) else address_or_reg
        if end_address:
            return self.ram[address:end_address]
        else:
            return self.ram[address]

    def set_ram(self, address, data):
        if address > self.MEMORY_SIZE:
            raise IndexError("Out of memory range.")
        if type(data) == int:
            data = data.to_bytes(1)
        elif type(data) == list:
            data = bytes(data)
        if type(data) != bytearray and type(data) != bytes:
            raise ValueError(f"Attempting to set RAM with wrong data type: {type(data)}")
        self.ram[address:address+len(data)] = data

    def find(self, value, start_address=0):
        # return the location of a value in ram
        # used for testing
        return self.ram.find(value, start_address)
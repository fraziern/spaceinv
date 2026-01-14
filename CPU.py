import random
# from OpcodeDetails import opcodes
# import opcodebytes

register_codes = {
    0b111: 'a',
    0b000: 'b',
    0b001: 'c',
    0b010: 'd',
    0b011: 'e',
    0b100: 'h',
    0b101: 'l',
}

register_codes_16b = {
    0b00: 'bc',
    0b01: 'de',
    0b10: 'hl',
    0b11: 'sp'
}

class CPU():
    # ROMSTART = 0x200

    def __init__(self, state, switches=None, display=None, config={}):
        self.config = {'debug':False}
        self.config |= config # in-place update
        self.state = state
        self.switches = switches
        self.display = display


    def _byte_to_bits(self, op):
        # Not exactly a "decode" but used to get bits in opcode
        # Format the integer to a binary string, padding with leading zeros to ensure correct length
        binary_string = format(op, f'08b')

        # Convert the binary string to a list of integers (bits)
        list_of_bits = [int(bit) for bit in binary_string]

        return list_of_bits
    

    def _get_r_from_bits(self, bits):
        binary_string = "".join(map(str, bits))
        decimal_number = int(binary_string, 2)
        if len(bits) == 2:
            # rp
            return register_codes_16b[decimal_number]
        elif len(bits) == 3:
            return register_codes[decimal_number]
        else:
            raise ValueError("Incorrect number of bits for conversion.")


    def _fetch_next_byte(self):
        # get next byte that PC points to, then step the PC
        value = self.state.get_byte_at_pc()
        self.state.increment_pc()
        return value


    def _fetch_next_two_bytes(self):
        # get next 2 bytes in ram, return them as little-endian 16 bit value
        lsb = self._fetch_next_byte()
        msb = self._fetch_next_byte() << 8
        value = lsb | msb
        return value


    def _run(self, instruction:list):
        match instruction:
            # Machine control group
            case [ 0, 0, 0, 0, 0, 0, 0, 0]: # instr_string = "NOP"
                return 4
            case [ 0, 1, 1, 1, 0, 1, 1, 0]: # instr_string = "HLT"
                # TODO Halt flag
                return 7
            # Data transfer group
            case [ 0, 0, 1, 1, 1, 0, 1, 0]: # instr_string = "LDA"
                address = self._fetch_next_two_bytes()
                self._mov(source_data=self.state.get_ram(address),
                          dest_r='a')
                return 13
            case [ 0, 0, 1, 1, 0, 0, 1, 0]: # instr_string = "STA"
                address = self._fetch_next_two_bytes()
                self._mov(source_r='a', dest_addr=address)
                return 13
            case [ 0, 0, 1, 0, 1, 0, 1, 0]: # instr_string = "LHLD"
                address = self._fetch_next_two_bytes()
                self._mov(source_data=self.state.get_ram(address),   dest_r='l')
                self._mov(source_data=self.state.get_ram(address+1), dest_r='h')
            case [ 0, 1, 1, 1, 0,s1,s2,s3]: # instr_string = "MOV M,r"
                self._mov(source_r=self._get_r_from_bits([s1,s2,s3]),
                          dest_addr_reg='hl')
                return 7
            case [ 0, 1,d1,d2,d3, 1, 1, 0]: # instr_string = "MOV r,M"
                self._mov(source_addr_reg='hl',
                          dest_r=self._get_r_from_bits([d1,d2,d3]))
                return 7
            case [ 0, 1,d1,d2,d3,s1,s2,s3]: # instr_string = "MOV r1,r2"
                self._mov(source_r=self._get_r_from_bits([s1,s2,s3]),
                          dest_r=self._get_r_from_bits([d1,d2,d3]))
                return 5
            case [ 0, 0, 1, 1, 0, 1, 1, 0]: # instr_string = "MVI M,data"
                data = self._fetch_next_byte()
                self._mov(source_data=data,
                          dest_addr_reg='hl')
                return 10
            case [ 0, 0, r, p, 0, 0, 0, 1]: # instr_string = "LXI rp, data16"
                data = self._fetch_next_two_bytes()
                self._mov(source_data=data,
                          dest_r=self._get_r_from_bits([r,p]))
            case [ 0, 0,d1,d2,d3, 1, 1, 0]: # instr_string = "MVI r,data"
                data = self._fetch_next_byte()
                self._mov(source_data=data,
                          dest_r=self._get_r_from_bits([d1,d2,d3]))
                return 7
            case _:
                raise NotImplementedError()
            
    
    def _mov(self, source_data=None, source_r=None, source_addr_reg=None, dest_addr=None,
             dest_r=None, dest_addr_reg=None):
        if source_data:
            source = source_data
        elif source_r:
            source = self.state.get_reg(source_r)
        elif source_addr_reg:
            source = self.state.get_ram(self.state.get_reg(source_addr_reg))
        else:
            raise ValueError("Source data not defined for move instruction.")
        
        if dest_addr:
            self.state.set_ram(dest_addr, source)
        elif dest_r:
            self.state.set_reg(dest_r, source)
        elif dest_addr_reg:
            self.state.set_ram(self.state.get_reg(dest_addr_reg), source)
        else:
            raise ValueError("Destination not defined for move instruction.")


    # def _add(self, state, a, b, result_to=None):
    #     if result_to is None:
    #         result_to = a
    #     value = state.get_vx(a) + state.get_vx(b)
    #     value, vf = (value % 256, 1) if value > 255 else (value, 0)
    #     state.set_vx(result_to,value)
    #     state.set_vx(0xf,vf) # carry


    # def _subtract(self, state, a, b, result_to=None): 
    #     # function for 8xy5 and 8xy7, subtracts a - b and updates state
    #     if result_to is None:
    #         result_to = a
    #     value = state.get_vx(a) - state.get_vx(b)
    #     value, vf = ((value + 256) % 256, 0) if value < 0 else (value, 1)
    #     state.set_vx(result_to,value)
    #     state.set_vx(0xf, vf)


    # def _right_shift(self, state, a, b, result_to=None):
    #     # 8xy6
    #     if result_to is None:
    #         result_to = a
    #     if self.config['nineties_shift']:
    #         state.set_vx(a, state.get_vx(b))
    #     vf = state.get_vx(a) & 0x1 # grab the rightmost bit
    #     state.set_vx(a, state.get_vx(a) >> 1)
    #     state.set_vx(0xf, vf)


    # def _left_shift(self, state, a, b, result_to=None):
    #     # 8xye
    #     if result_to is None:
    #         result_to = a
    #     if self.config['nineties_shift']:
    #         state.set_vx(a, state.get_vx(b))
    #     vf = (state.get_vx(a) >> 7) & 0x1 # grab the leftmost bit
    #     state.set_vx(a, state.get_vx(a) << 1)
    #     state.set_vx(0xf, vf)


    # def _draw_instr(self, state, display, vx, vy, n):
    #     x = state.get_vx(vx)
    #     y = state.get_vx(vy)
    #     sprite = state.get_ram(n)
    #     vf = display.update_screen(x, y, sprite)
    #     state.set_vx(0xf, vf)


    def run_cycle(self):
        # 1. Fetch instruction opcode
        op = self._fetch_next_byte()
        # 2. Decode, into list of bits
        instruction_bits = self._byte_to_bits(op)
        try:
            used_cycles = self._run(instruction_bits)
        except NotImplementedError:
            raise NotImplementedError(f"Instruction not implemented: {op:X}")
        print(self.state)
        print(instruction_bits)

from State import State

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

    def __init__(self, state:State, switches=None, display=None, config={}):
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
                return 16
            case [ 0, 0, 1, 0, 0, 0, 1, 0]: # instr_string = "SHLD"
                address = self._fetch_next_two_bytes()
                self._mov(source_r='l', dest_addr=address)
                self._mov(source_r='h', dest_addr=address+1)
                return 16
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
            case [ 1, 1, 1, 0, 1, 0, 1, 1]: # instr_string = "XCHG"
                temp = self.state.get_reg('de')
                self._mov(source_r='hl', dest_r='de')
                self._mov(source_data=temp, dest_r='hl')
                return 4
            case [ 0, 0, r, p, 0, 0, 0, 1]: # instr_string = "LXI rp, data16"
                data = self._fetch_next_two_bytes()
                self._mov(source_data=data,
                          dest_r=self._get_r_from_bits([r,p]))
                return 10
            case [ 0, 0, r, p, 1, 0, 1, 0]: # instr_string = "LDAX rp"
                if r == 1:
                    raise ValueError("LDAX can only use register pairs BC and DE.")
                self._mov(source_addr_reg=self._get_r_from_bits([r,p]),
                          dest_r='a')
                return 7
            case [ 0, 0, r, p, 0, 0, 1, 0]: # instr_string = "STAX rp"
                if r == 1:
                    raise ValueError("STAX can only use register pairs BC and DE.")
                self._mov(source_r='a', 
                          dest_addr=self.state.get_reg(self._get_r_from_bits([r,p])))
                return 7          
            case [ 0, 0,d1,d2,d3, 1, 1, 0]: # instr_string = "MVI r,data"
                data = self._fetch_next_byte()
                self._mov(source_data=data,
                          dest_r=self._get_r_from_bits([d1,d2,d3]))
                return 7
            
            # Arithmetic group
            case [ 1, 0, 0, 0, 0, 1, 1, 0]: # instr_string = "ADD m"
                data = self.state.get_ram(self.state.get_reg('hl'))
                self._add(source_data=data)
                return 7
            case [ 1, 0, 0, 0, 0,s1,s2,s3]: # instr_string = "ADD r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._add(source_r=source_reg)
                return 4
            case [ 1, 1, 0, 0, 0, 1, 1, 0]: # instr_string = "ADI data"
                data = self._fetch_next_byte()
                self._add(source_data=data)
                return 7
            case [ 1, 1, 0, 0, 1, 1, 1, 0]: # instr_string = "ACI data"
                data = self._fetch_next_byte()
                self._add(source_data=data, add_carry=True)
                return 7
            case [ 1, 0, 0, 0, 1, 1, 1, 0]: # instr_string = "ADC m"
                data = self.state.get_ram(self.state.get_reg('hl'))
                self._add(source_data=data, add_carry=True)
                return 7
            case [ 1, 0, 0, 0, 1,s1,s2,s3]: # instr_string = "ADC r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._add(source_r=source_reg, add_carry=True)
                return 4
            case [ 1, 0, 0, 1, 0, 1, 1, 0]: # instr_string = "SUB m"
                data = self.state.get_ram(self.state.get_reg('hl'))
                self._sub(source_data=data)
                return 7
            case [ 1, 0, 0, 1, 0,s1,s2,s3]: # instr_string = "SUB r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._sub(source_r=source_reg)
                return 4
            case [ 1, 0, 0, 1, 1, 1, 1, 0]: # instr_string = "SBB m"
                data = self.state.get_ram(self.state.get_reg('hl'))
                self._sub(source_data=data, sub_carry=True)
                return 7
            case [ 1, 0, 0, 1, 1,s1,s2,s3]: # instr_string = "SBB r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._sub(source_r=source_reg, sub_carry=True)
                return 4
            case [ 1, 1, 0, 1, 0, 1, 1, 0]: # instr_string = "SUI data"
                data = self._fetch_next_byte()
                self._sub(source_data=data)
                return 7
            case [ 1, 1, 0, 1, 1, 1, 1, 0]: # instr_string = "SBI data"
                data = self._fetch_next_byte()
                self._sub(source_data=data, sub_carry=True)
                return 7
            case [ 0, 0, 1, 1, 0, 1, 0, 0]: # instr_string = "INR M"
                self._inc(use_hl_address=True)
                return 10
            case [ 0, 0,d1,d2,d3, 1, 0, 0]: # instr_string = "INR r"
                self._inc(register=self._get_r_from_bits([d1,d2,d3]))
                return 5
            case [ 0, 0, 1, 1, 0, 1, 0, 1]: # instr_string = "DCR M"
                self._dec(use_hl_address=True)
                return 10
            case [ 0, 0,d1,d2,d3, 1, 0, 1]: # instr_string = "DCR r"
                self._dec(register=self._get_r_from_bits([d1,d2,d3]))
                return 5
            case [ 0, 0, r, p, 0, 0, 1, 1]: # instr_string = "INX rp"
                register = self._get_r_from_bits([r,p])
                self.state.set_reg(register, self.state.get_reg(register) + 1)
                return 5
            case [ 0, 0, r, p, 1, 0, 1, 1]: # instr_string = "DCX rp"
                register = self._get_r_from_bits([r,p])
                self.state.set_reg(register, self.state.get_reg(register) - 1)
                return 5
            case [ 0, 0, r, p, 1, 0, 0, 1]: # instr_string = "DAD rp"
                self._dad(self._get_r_from_bits([r,p]))
                return 10
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
        
        if dest_addr:
            self.state.set_ram(dest_addr, source)
        elif dest_r:
            self.state.set_reg(dest_r, source)
        elif dest_addr_reg:
            self.state.set_ram(self.state.get_reg(dest_addr_reg), source)
        else:
            raise ValueError("Destination not defined for move instruction.")

    def _add(self, source_data=None, source_r=None, add_carry=False, use_negative=False):
        acc_value = self.state.get_reg('a')
        if source_r:
            source = self.state.get_reg(source_r)
        elif source_data:
            source = source_data
        
        # add carry bit if add_carry is True
        source = source + self.state.get_flag('c') if add_carry else source

        # negate if this is a subtract operation
        source = -source if use_negative else source
        
        byte_result = (source + acc_value) & 0xff
        self.state.set_reg('a', byte_result)
        # condition flag checks
        flags = [
            bool(byte_result >> 7), # s
            bool(not byte_result),  # z
            False,
            ((source & 0xf) + (acc_value & 0xf) > 0xf), # ac
            False,
            not bool(sum(self._byte_to_bits(byte_result)) % 2), # p
            False,
            ((-source > acc_value) if use_negative else 
             (source + acc_value >= 0xff)) # c
        ]
        self.state.set_flags(flags)

    def _inc(self, register=None, use_hl_address=False, negative=False):
        inc_by = -1 if negative else 1
        if register:
            initial_value = self.state.get_reg(register)
            byte_result = (initial_value + inc_by) % 256
            self.state.set_reg(register, byte_result)
        elif use_hl_address:
            address = self.state.get_reg('hl')
            initial_value = self.state.get_ram(address)
            byte_result = (initial_value + inc_by) & 0xff
            self.state.set_ram(address, byte_result)
        flags = [
            bool(byte_result >> 7), # s
            bool(not byte_result),  # z
            False,
            ((initial_value & 0xf) + inc_by > 0xf), # ac
            False,
            not bool(sum(self._byte_to_bits(byte_result)) % 2), # p
            False,
            self.state.get_flag('c') # don't touch c here
        ]
        self.state.set_flags(flags)

    def _sub(self, source_data=None, source_r=None, sub_carry=False):
        self._add(source_data, source_r, add_carry=sub_carry, use_negative=True)

    def _dec(self, register=None, use_hl_address=False):
        self._inc(register, use_hl_address, negative=True)

    def _dad(self, register):
        # add register pair to hl, set carry flag if needed
        hl_value = self.state.get_reg('hl')
        result = self.state.get_reg(register) + hl_value
        self.state.set_reg('hl', result & 0xffff)
        self.state.set_flag('c', result > 0xffff)


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

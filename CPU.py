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

    def _set_nc_flags(self, byte_result): # set non-carry flags
        self.state.set_flags({
            's': bool(byte_result >> 7), # s
            'z': bool(not byte_result),  # z
            'p': not bool(sum(self._byte_to_bits(byte_result)) % 2), # p
        })

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
                self._mov(self.state.get_ram(address), 'a')
                return 13
            case [ 0, 0, 1, 1, 0, 0, 1, 0]: # instr_string = "STA"
                address = self._fetch_next_two_bytes()
                self._mov('a', address)
                return 13
            case [ 0, 0, 1, 0, 1, 0, 1, 0]: # instr_string = "LHLD"
                address = self._fetch_next_two_bytes()
                self._mov(self.state.get_ram(address),   'l')
                self._mov(self.state.get_ram(address+1), 'h')
                return 16
            case [ 0, 0, 1, 0, 0, 0, 1, 0]: # instr_string = "SHLD"
                address = self._fetch_next_two_bytes()
                self._mov('l', address)
                self._mov('h', address+1)
                return 16
            case [ 0, 1, 1, 1, 0,s1,s2,s3]: # instr_string = "MOV M,r"
                self._mov(self._get_r_from_bits([s1,s2,s3]), 'hl', write_reg_address=True)
                return 7
            case [ 0, 1,d1,d2,d3, 1, 1, 0]: # instr_string = "MOV r,M"
                data = self.state.get_ram('hl')
                self._mov(data, self._get_r_from_bits([d1,d2,d3]))
                return 7
            case [ 0, 1,d1,d2,d3,s1,s2,s3]: # instr_string = "MOV r1,r2"
                self._mov(self._get_r_from_bits([s1,s2,s3]),
                          self._get_r_from_bits([d1,d2,d3]))
                return 5
            case [ 0, 0, 1, 1, 0, 1, 1, 0]: # instr_string = "MVI M,data"
                self._mov(self._fetch_next_byte(), 'hl', write_reg_address=True)
                return 10
            case [ 1, 1, 1, 0, 1, 0, 1, 1]: # instr_string = "XCHG"
                temp = self.state.get_reg('de')
                self._mov('hl', 'de')
                self._mov(temp, 'hl')
                return 4
            case [ 0, 0, r, p, 0, 0, 0, 1]: # instr_string = "LXI rp, data16"
                self._mov(self._fetch_next_two_bytes(),
                          self._get_r_from_bits([r,p]))
                return 10
            case [ 0, 0, r, p, 1, 0, 1, 0]: # instr_string = "LDAX rp"
                if r == 1:
                    raise ValueError("LDAX can only use register pairs BC and DE.")
                data = self.state.get_ram(self._get_r_from_bits([r,p]))
                self._mov(data, 'a')
                return 7
            case [ 0, 0, r, p, 0, 0, 1, 0]: # instr_string = "STAX rp"
                if r == 1:
                    raise ValueError("STAX can only use register pairs BC and DE.")
                self._mov('a', 
                          self.state.get_reg(self._get_r_from_bits([r,p])))
                return 7          
            case [ 0, 0,d1,d2,d3, 1, 1, 0]: # instr_string = "MVI r,data"
                self._mov(self._fetch_next_byte(),
                          self._get_r_from_bits([d1,d2,d3]))
                return 7
            
            # Arithmetic group
            case [ 0, 0, 1, 0, 0, 1, 1, 1]: # instr_string = "DAA rp"
                self._daa()
                return 4
            case [ 1, 0, 0, 0, 0, 1, 1, 0]: # instr_string = "ADD m"
                data = self.state.get_ram('hl')
                self._add(data)
                return 7
            case [ 1, 0, 0, 0, 0,s1,s2,s3]: # instr_string = "ADD r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._add(source_reg)
                return 4
            case [ 1, 1, 0, 0, 0, 1, 1, 0]: # instr_string = "ADI data"
                data = self._fetch_next_byte()
                self._add(data)
                return 7
            case [ 1, 1, 0, 0, 1, 1, 1, 0]: # instr_string = "ACI data"
                data = self._fetch_next_byte()
                self._add(data, add_carry=True)
                return 7
            case [ 1, 0, 0, 0, 1, 1, 1, 0]: # instr_string = "ADC m"
                data = self.state.get_ram('hl')
                self._add(data, add_carry=True)
                return 7
            case [ 1, 0, 0, 0, 1,s1,s2,s3]: # instr_string = "ADC r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._add(source_reg, add_carry=True)
                return 4
            case [ 1, 0, 0, 1, 0, 1, 1, 0]: # instr_string = "SUB m"
                data = self.state.get_ram('hl')
                self._sub(data)
                return 7
            case [ 1, 0, 0, 1, 0,s1,s2,s3]: # instr_string = "SUB r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._sub(source_reg)
                return 4
            case [ 1, 0, 0, 1, 1, 1, 1, 0]: # instr_string = "SBB m"
                data = self.state.get_ram('hl')
                self._sub(data, sub_carry=True)
                return 7
            case [ 1, 0, 0, 1, 1,s1,s2,s3]: # instr_string = "SBB r"
                source_reg = self._get_r_from_bits([s1,s2,s3])
                self._sub(source_reg, sub_carry=True)
                return 4
            case [ 1, 1, 0, 1, 0, 1, 1, 0]: # instr_string = "SUI data"
                data = self._fetch_next_byte()
                self._sub(data)
                return 7
            case [ 1, 1, 0, 1, 1, 1, 1, 0]: # instr_string = "SBI data"
                data = self._fetch_next_byte()
                self._sub(data, sub_carry=True)
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
            
            # logical group
            case [ 1, 0, 1, 0, 0, 1, 1, 0]: # instr_string = "ANA M"
                data = self.state.get_ram('hl')
                self._ana(data)
                return 7
            case [ 1, 0, 1, 0, 0,s1,s2,s3]: # instr_string = "ANA r"
                self._ana(self._get_r_from_bits([s1,s2,s3]))
                return 4
            case [ 1, 1, 1, 0, 0, 1, 1, 0]: # instr_string = "ANI data"
                self._ana(self._fetch_next_byte())
                return 7
            case [ 1, 0, 1, 0, 1, 1, 1, 0]: # instr_string = "XRA M"
                data = self.state.get_ram('hl')
                self._xra(data)
                return 7
            case [ 1, 0, 1, 0, 1,s1,s2,s3]: # instr_string = "XRA r"
                self._xra(self._get_r_from_bits([s1,s2,s3]))
                return 4
            case [ 1, 1, 1, 0, 1, 1, 1, 0]: # instr_string = "XRI data"
                self._xra(self._fetch_next_byte())
                return 7
            case [ 1, 0, 1, 1, 0, 1, 1, 0]: # instr_string = "ORA M"
                data = self.state.get_ram('hl')
                self._ora(data)
                return 7
            case [ 1, 0, 1, 1, 0,s1,s2,s3]: # instr_string = "ORA r"
                self._ora(self._get_r_from_bits([s1,s2,s3]))
                return 4
            case [ 1, 1, 1, 1, 0, 1, 1, 0]: # instr_string = "ORI data"
                self._ora(self._fetch_next_byte())
                return 7
            case [ 1, 0, 1, 1, 1, 1, 1, 0]: # instr_string = "CMP M"
                data = self.state.get_ram('hl')
                self._cmp(data)
                return 7
            case [ 1, 0, 1, 1, 1,s1,s2,s3]: # instr_string = "CMP r"
                self._cmp(self._get_r_from_bits([s1,s2,s3]))
                return 4
            case [ 1, 1, 1, 1, 1, 1, 1, 0]: # instr_string = "CPI data"
                self._cmp(self._fetch_next_byte())
                return 7
            case [ 0, 0, 0, 0, 0, 1, 1, 1]: # instr_string = "RLC"
                self._rlc()
                return 4
            case _:
                raise NotImplementedError()
            
    
    def _mov(self, source, dest, write_reg_address=False):
        # source can be a register or direct data.
        if isinstance(source, str):  # register
            source = self.state.get_reg(source)
        
        if isinstance(dest, str):
            if write_reg_address:
                self.state.set_ram(self.state.get_reg(dest), source)
            else:
                self.state.set_reg(dest, source)
        else:
            self.state.set_ram(dest, source)

    def _add(self, source, add_carry=False, use_negative=False):
        acc_value = self.state.get_reg('a')
        if isinstance(source, str):
            source = self.state.get_reg(source)
        
        # add carry bit if add_carry is True
        source = source + self.state.get_flag('c') if add_carry else source

        # negate if this is a subtract operation
        source = -source if use_negative else source
        
        byte_result = (source + acc_value) & 0xff
        self.state.set_reg('a', byte_result)
        # condition flag checks
        self._set_nc_flags(byte_result)
        self.state.set_flags({
            'a': ((source & 0xf) + (acc_value & 0xf) > 0xf), # ac
            'c': ((-source > acc_value) if use_negative else 
             (source + acc_value >= 0xff)) # c
        })

    def _inc(self, register=None, use_hl_address=False, negative=False):
        inc_by = -1 if negative else 1
        if register:
            initial_value = self.state.get_reg(register)
            byte_result = (initial_value + inc_by) & 0xff
            self.state.set_reg(register, byte_result)
        elif use_hl_address:
            address = self.state.get_reg('hl')
            initial_value = self.state.get_ram(address)
            byte_result = (initial_value + inc_by) & 0xff
            self.state.set_ram(address, byte_result)
        self._set_nc_flags(byte_result)
        self.state.set_flag('a',((initial_value & 0xf) + inc_by > 0xf))

    def _sub(self, source, sub_carry=False):
        self._add(source, add_carry=sub_carry, use_negative=True)

    def _dec(self, register=None, use_hl_address=False):
        self._inc(register, use_hl_address, negative=True)

    def _dad(self, register):
        # add register pair to hl, set carry flag if needed
        hl_value = self.state.get_reg('hl')
        result = self.state.get_reg(register) + hl_value
        self.state.set_reg('hl', result & 0xffff)
        self.state.set_flag('c', result > 0xffff)

    def _daa(self):
        if ((self.state.get_reg('a') & 0xf) > 9) or self.state.get_flag('a'):
            self._add(6)
        saved_aux_carry = self.state.get_flag('a') # save aux carry value in case of overwrite
        if ((self.state.get_reg('a') >> 4) > 9) or self.state.get_flag('c'):
            self._add(6 << 4)
            self.state.set_flag('a', saved_aux_carry)

    def _logic(self, register_or_data, operation):
        if isinstance(register_or_data, str):  # register
            source = self.state.get_reg(register_or_data)
        else:
            source = register_or_data
        match operation:
            case 'and':
                byte_result = self.state.get_reg('a') & source
            case 'or':
                byte_result = self.state.get_reg('a') | source
            case 'xor':
                byte_result = self.state.get_reg('a') ^ source

        self.state.set_reg('a', byte_result)

        self._set_nc_flags(byte_result)
        self.state.set_flag('c', False)  
        self.state.set_flag('a', False)

    def _ana(self, register_or_data):
        self._logic(register_or_data, 'and')
    
    def _xra(self, register_or_data):
        self._logic(register_or_data, 'xor')
    
    def _ora(self, register_or_data):
        self._logic(register_or_data, 'or')

    def _cmp(self, register_or_data):
        saved_acc_value = self.state.get_reg('a')
        self._sub(register_or_data)
        self.state.set_reg('a', saved_acc_value)

    def _rlc(self):
        acc_value = self.state.get_reg('a')
        high_bit = acc_value >> 7
        self.state.set_reg('a', (acc_value << 1) | high_bit)
        self.state.set_flag('c', high_bit)
    
    def _rrc(self):
        acc_value = self.state.get_reg('a')
        low_bit = acc_value & 0x01
        self.state.set_reg('a', (acc_value >> 1) | (low_bit << 7))
        self.state.set_flag('c', low_bit)


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

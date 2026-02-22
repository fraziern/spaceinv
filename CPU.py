from State import State
from Bus import Bus
from utils import bits_to_int, byte_to_bits
import time

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

    def __init__(self, state:State, bus:Bus, config={}):
        self.config = {'debug':False}
        self.config |= config # in-place update
        self.state = state
        self.bus = bus
    

    def _get_r_from_bits(self, bits):
        decimal_number = bits_to_int(bits)
        if len(bits) == 2:
            # rp
            return register_codes_16b[decimal_number]
        elif len(bits) == 3:
            return register_codes[decimal_number]


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
            'p': not bool(sum(byte_to_bits(byte_result)) % 2), # p
        })


    def _run(self, instruction:list):
        match instruction:
            # Machine control group
            case [ 0, 0, 0, 0, 0, 0, 0, 0]: # instr_string = "NOP"
                return 4
            case [ 0, 1, 1, 1, 0, 1, 1, 0]: # instr_string = "HLT"
                # TODO Halt flag?
                return None
            
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
                # ######## BREAK
                # hl = self.state.get_reg('hl')
                # if hl > 0x3fff:
                #     return -7
                # ######## BREAK END
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
            case [ 0, 0, 0, 0, 1, 1, 1, 1]: # instr_string = "RRC"
                self._rrc()
                return 4
            case [ 0, 0, 0, 1, 0, 1, 1, 1]: # instr_string = "RAL"
                self._ral()
                return 4
            case [ 0, 0, 0, 1, 1, 1, 1, 1]: # instr_string = "RAR"
                self._rar()
                return 4
            case [ 0, 0, 1, 0, 1, 1, 1, 1]: # instr_string = "CMA"
                acc_value = self.state.get_reg('a')
                self.state.set_reg('a', ~acc_value & 0xff)
                return 4
            case [ 0, 0, 1, 1, 1, 1, 1, 1]: # instr_string = "CMC"
                carry = self.state.get_flag('c')
                self.state.set_flag('c', (carry == False))
                return 4
            case [ 0, 0, 1, 1, 0, 1, 1, 1]: # instr_string = "STC"
                self.state.set_flag('c', True)
                return 4
            
            # branch instructions
            case [ 1, 1, 0, 0, 0, 0, 1, 1]: # instr_string = "JMP data"
                data = self._fetch_next_two_bytes()
                self.state.set_pc(data)
                return 10
            case [ 1, 1,c1,c2,c3, 0, 1, 0]: # instr_string = "Jcondition data"
                data = self._fetch_next_two_bytes()
                if self._check_conditions(bits_to_int([c1,c2,c3])):
                    self.state.set_pc(data)
                return 10
            
            # call instructions
            case [ 1, 1, 0, 0, 1, 1, 0, 1]: # instr_string = "CALL addr"
                data = self._fetch_next_two_bytes()
                self._call(data)
                return 17
            case [ 1, 1,c1,c2,c3, 1, 0, 0]: # instr_string = "Ccondition addr"
                data = self._fetch_next_two_bytes()
                if self._check_conditions(bits_to_int([c1,c2,c3])):
                    self._call(data)
                    return 17
                return 11
            case [ 1, 1, 0, 0, 1, 0, 0, 1]: # instr_string = "RET"
                self._ret()
                return 10
            case [ 1, 1,c1,c2,c3, 0, 0, 0]: # instr_string = "Rcondition"
                if self._check_conditions(bits_to_int([c1,c2,c3])):
                    self._ret()
                    return 11
                return 5
            case [ 1, 1,n1,n2,n3, 1, 1, 1]: # instr_string = "RST n"
                address = bits_to_int([n1,n2,n3]) * 8
                self._call(address)
                return 11
            case [ 1, 1, 1, 0, 1, 0, 0, 1]: # instr_string = "PCHL"
                self.state.set_pc(self.state.get_reg('hl'))
                return 5
            
            # push pop
            case [ 1, 1, 1, 1, 0, 1, 0, 1]: # instr_string = "PUSH psw"
                self._pushpsw()
                return 11
            case [ 1, 1, r, p, 0, 1, 0, 1]: # instr_string = "PUSH rp"
                register = self._get_r_from_bits([r,p])
                self._push(register)
                return 11
            case [ 1, 1, 1, 1, 0, 0, 0, 1]: # instr_string = "POP psw"
                self._poppsw()
                return 10
            case [ 1, 1, r, p, 0, 0, 0, 1]: # instr_string = "POP rp"
                register = self._get_r_from_bits([r,p])
                self._pop(register)
                return 10
            case [ 1, 1, 1, 0, 0, 0, 1, 1]: # instr_string = "XTHL"
                self._xthl()
                return 18
            case [ 1, 1, 1, 1, 1, 0, 0, 1]: # instr_string = "XTHL"
                hl = self.state.get_reg('hl')
                self.state.set_sp(hl)
                return 5
            
            # interrupts and I/O
            case [ 1, 1, 1, 1, 1, 0, 1, 1]: # instr_string = "EI"
                # TODO what do we do here
                return 4
            case [ 1, 1, 1, 1, 0, 0, 1, 1]: # instr_string = "DI"
                # TODO what do we do here
                return 4
            case [ 1, 1, 0, 1, 1, 0, 1, 1]: # instr_string = "IN"
                port = self._fetch_next_byte()
                self.state.set_reg('a', self.bus.read(port))
                return 10
            case [ 1, 1, 0, 1, 0, 0, 1, 1]: # instr_string = "OUT"
                port = self._fetch_next_byte()
                self.bus.write(port, self.state.get_reg('a'))
                return 10

            case _:
                raise NotImplementedError()
            
    
    def _mov(self, source, dest, write_reg_address=False):
        # source can be a register or direct data.
        if isinstance(source, str):  # register
            source = self.state.get_reg(source)
        
        if isinstance(dest, str):
            if write_reg_address:
                self.state.set_ram(self.state.get_reg(dest), source)
                # print(f"Writing to: {self.state.get_reg(dest)} at instr {self.state.pc:04x}")
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
             ((source + acc_value) > 0xff)) # c
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
        saved_carry = self.state.get_flag('c') # save carry value in case of overwrite
        if ((self.state.get_reg('a') & 0xf) > 9) or self.state.get_flag('a'):
            self._add(6)
            self.state.set_flag('c', saved_carry)
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


    def _ral(self):
        acc_value = self.state.get_reg('a')
        carry = int(self.state.get_flag('c'))
        high_bit = acc_value >> 7
        self.state.set_reg('a', (acc_value << 1) | carry)
        self.state.set_flag('c', high_bit)


    def _rar(self):
        acc_value = self.state.get_reg('a')
        carry = int(self.state.get_flag('c'))
        low_bit = bool(acc_value & 0x01)
        self.state.set_reg('a', (acc_value >> 1) | (carry << 7))
        self.state.set_flag('c', low_bit)


    def _check_conditions(self, operation:int) -> bool:
        match operation:
            case 0b000:
                return self.state.get_flag('z') == False
            case 0b001:
                return self.state.get_flag('z') == True
            case 0b010:
                return self.state.get_flag('c') == False
            case 0b011:
                return self.state.get_flag('c') == True
            case 0b100:
                return self.state.get_flag('p') == False
            case 0b101:
                return self.state.get_flag('p') == True
            case 0b110:
                return self.state.get_flag('s') == False
            case 0b111:
                return self.state.get_flag('s') == True


    def _push_to_stack(self, value):
        sp_start = self.state.get_sp()
        self.state.set_ram(sp_start - 1, value >> 8)
        self.state.set_ram(sp_start - 2, value & 0xff)
        self.state.set_sp(sp_start - 2)


    def _pop_from_stack(self):
        sp_start = self.state.get_sp()
        sl = self.state.get_ram(sp_start)
        sh = self.state.get_ram(sp_start + 1)
        self.state.set_sp(sp_start + 2)
        return ((sh << 8) | sl)


    def _call(self, address):
        pc = self.state.get_pc()
        self._push_to_stack(pc)
        self.state.set_pc(address)


    def _ret(self):
        value = self._pop_from_stack()
        self.state.set_pc(value)


    def _push(self, register):
        if register == 'sp':
            raise ValueError("SP may not be pushed in PUSH operation.")
        value = self.state.get_reg(register)
        self._push_to_stack(value)


    def _pop(self, register):
        if register == 'sp':
            raise ValueError("SP may not be pushed in PUSH operation.")
        value = self._pop_from_stack()
        self.state.set_reg(register, value)


    def _pushpsw(self):
        psw = self.state.get_psw()
        a = self.state.get_reg('a')
        self._push_to_stack((a << 8) | psw)


    def _poppsw(self):
        value = self._pop_from_stack()
        a = value >> 8
        psw = value & 0xff
        self.state.set_reg('a', a)
        self.state.set_psw(psw)


    def _xthl(self):
        hl = self.state.get_reg('hl')
        stack = self._pop_from_stack()
        self._push_to_stack(hl)
        self.state.set_reg('hl', stack)
        

    def run_cycle(self, rst=None):
        # interrupt
        if rst:
            op = rst
        # 1. Fetch instruction opcode, advance PC
        else:
            op = self._fetch_next_byte()
        # 2. Decode, into list of bits
        instruction_bits = byte_to_bits(op)
        try:
            used_cycles = self._run(instruction_bits)
        except NotImplementedError:
            raise NotImplementedError(f"Instruction not implemented: {op:X} ({instruction_bits})")
        return used_cycles


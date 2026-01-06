import random
from dataclasses import dataclass

class CPU():
    # ROMSTART = 0x200

    def __init__(self, state, switches=None, display=None, config={}):
        self.config = {'debug':False}
        self.config |= config # in-place update
        self.state = state
        self.switches = switches
        self.display = display


    def run_cycle(self):
        # 1. Fetch instruction opcode, and operands if needed
        instruction_index = 0
        instruction = OpcodeDetails()

        while instruction_index < instruction.length:
            op = self.state.get_byte_at_pc()
            self.state.increment_pc()
            self.state.set_ir(instruction_index, op)
            if instruction_index == 0:
                instruction = self.get_instruction(op)
            instruction_index += 1

        print(self.state)
        print(instruction)


    # # instr will be a 1 byte opcode
    # # and optionally 1-2 data bytes
    # def _decode_instruction(self, instr:bytearray):
        
    #     # nibbles
    #     n1 = (instr[0] >> 4) & 0xf
    #     n2 = instr[0] & 0xf
    #     n3 = (instr[1] >> 4) & 0xf
    #     n4 = instr[1] & 0xf
    #     nn = instr[1]
    #     nnn = (n2 << 8) | (n3 << 4) | n4

    #     return n1, n2, n3, n4, nn, nnn


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



        # # 4. Decode/Execute instruction
        # n1, n2, n3, n4, nn, nnn = self._decode_instruction(instr)
        # if self.config['debug']:
        #     definition = get_instr_definition(n1, n2, n3, n4, nn, nnn)
        #     print(f'Instruction {self.state.get_pc()-self.ROMSTART:X}: {instr.hex()} {definition}')

        # match n1:

# clear IR

@dataclass
class OpcodeDetails:
    length: int = 1
    cycles: int = 1
    instruction: str = 'Undefined'

opcodes = {
    0x00: OpcodeDetails(length=1, cycles=4, instruction='NOP')
}
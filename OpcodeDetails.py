from dataclasses import dataclass
import opcodebytes


@dataclass
class OpcodeDetails:
    length: int = 1
    cycles: int = 1
    instruction: str = 'Undefined'

opcodes = {
    opcodebytes.NOP: OpcodeDetails(length=1, cycles=4, instruction='NOP')
}
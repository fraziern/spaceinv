import numpy as np

def bits_to_int(bits:list) -> int:
    # convert a list of 1s and 0s into an int
    binary_string = "".join(map(str, bits))
    decimal_number = int(binary_string, 2)
    return decimal_number

def byte_to_bits(op):
    # Not exactly a "decode" but used to get bits in opcode
    op_np = np.array([op], dtype=np.uint8)
    list_of_bits = np.unpackbits(op_np).tolist()
    return list_of_bits
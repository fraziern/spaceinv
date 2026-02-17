def bits_to_int(bits:list) -> int:
    # convert a list of 1s and 0s into an int
    binary_string = "".join(map(str, bits))
    decimal_number = int(binary_string, 2)
    return decimal_number

def byte_to_bits(op):
    # Not exactly a "decode" but used to get bits in opcode
    # Format the integer to a binary string, padding with leading zeros to ensure correct length
    binary_string = format(op, f'08b')

    # Convert the binary string to a list of integers (bits)
    list_of_bits = [int(bit) for bit in binary_string]

    return list_of_bits
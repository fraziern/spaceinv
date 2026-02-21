import numpy as np
    
def byte_to_bits(op):
    op_np = np.array([op], dtype=np.uint8)
    list_of_bits = np.unpackbits(op_np).tolist()
    return list_of_bits

for i in range(256):
    bit_list = byte_to_bits(i)
    print(f"{i}: {bit_list},")
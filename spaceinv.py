import pygame
from PygameDisplay import Display
from State import State
from Bus import Bus
from CPU import CPU
from opcodebytes import Opcodebytes


rom_filename = r''

# invaders.h 0000-07FF
# invaders.g 0800-0FFF
# invaders.f 1000-17FF
# invaders.e 1800-1FFF

DEBUG = False
FPS = 60 # Frames per second - do not change!
CPF = int(2_000_000 / 60) # cycles per frame on a 2MHz 8080
ROMSTART = 0x0000

# Create a value-to-name mapping - for debugging
# vars(MyClass) returns a dictionary of class attributes
opcode_names = {value: name for name, value in vars(Opcodebytes).items() if name.isupper()}


def main():

    pygame.init()

    state = State(romstart=ROMSTART)
    display = Display(state)
    bus = Bus()
    cpu = CPU(state, bus)


    #####################################################
    ### load the program rom
    with open(rom_filename,'rb') as file:
        full_rom = file.read()
        state.set_ram(ROMSTART, full_rom)

    clock = pygame.time.Clock()
    running = True


    ### MAIN LOOP
    while(running):
    
        # 3. cpu cycle
        current_cycles = 0

        while (current_cycles < CPF):
            # output handler
            curr_address = state.get_pc()
            next_ram = state.get_ram(curr_address, curr_address+3)
            next_instruction = state.get_byte_at_pc()
            if curr_address == 0x0005:
                c_register = state.get_reg('c')
                if c_register == 9:
                    start = state.get_reg('de')
                    end = state.find(b'$', start)
                    bytestring = state.get_ram(start, end)
                    print(bytestring.decode('ascii'))
                elif c_register == 2:
                    char = state.get_reg('e')
                    print(chr(char), end='')
                else:
                    raise ValueError(f"Unrecognized output code in C register: {c_register}")


            cycles = cpu.run_cycle()
            if (cycles is None):
                print("Halt code executed.")
                quit()
            else:
                current_cycles += cycles
            
            if DEBUG:
                opcode = opcode_names[next_instruction]
                print(f"Instruction: {opcode}")
                print(f"RAM slice: {next_ram.hex(' ')}")
                print(state)
                input("Enter to continue")

        # 4. Update display
        display.render_screen()

        # 5. sleep until FPS met
        clock.tick(FPS)
        


if __name__ == "__main__":
    main()

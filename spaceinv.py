import pygame
from PygameDisplay import Display
from State import State
from Bus import Bus
from CPU import CPU
from opcodebytes import Opcodebytes


rom_filenames = [r'roms\invaders.h',r'roms\invaders.g',r'roms\invaders.f',r'roms\invaders.e']

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
    ### load the program roms
    # invaders.h 0000-07FF
    # invaders.g 0800-0FFF
    # invaders.f 1000-17FF
    # invaders.e 1800-1FFF
    for r in range(4):
        with open(rom_filenames[r],'rb') as file:
            full_rom = file.read()
            state.set_ram(ROMSTART+(r*0x800), full_rom)

    clock = pygame.time.Clock()
    running = True


    ### MAIN LOOP
    while(running):
        # 1. Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # Set the flag to False to break the while loop
    
        # 2. cpu frame
        current_cycles = 0

        while (current_cycles < CPF):
            curr_address = state.get_pc()
            next_ram = state.get_ram(curr_address, curr_address+3)
            next_instruction = state.get_byte_at_pc()

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

        # 3. Update display
        display.render_screen()

        # 4. sleep until FPS met
        clock.tick(FPS)
        


if __name__ == "__main__":
    main()

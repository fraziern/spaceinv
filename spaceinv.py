import pickle
import pygame
from NumpyDisplay import Display
from State import State
from Bus import Bus
from CPU import CPU
from Keyboard import Keyboard
from opcodebytes import Opcodebytes


rom_filenames = [r'roms\invaders.h',r'roms\invaders.g',r'roms\invaders.f',r'roms\invaders.e']


FPS = 60 # Frames per second
CPF = 2_000_000 // FPS # cycles per frame on a 2MHz 8080
ROMSTART = 0x0000

# Create a value-to-name mapping - for debugging
# vars(MyClass) returns a dictionary of class attributes
opcode_names = {value: name for name, value in vars(Opcodebytes).items() if name.isupper()}


def wait_for_key(state):
    print("Paused: (s) to save state (l) to load state (d) to debug")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_s:
                    # save state
                    with open('state.pkl', 'wb') as file:
                        pickle.dump(state, file)
                    print("Saved state.")
                elif event.key == pygame.K_l:
                    with open('state.pkl', 'rb') as file:
                        new_state = pickle.load(file)
                        state.copy(new_state)
                    print("Loaded state.")
                elif event.key == pygame.K_d:
                    print("Debug mode enabled.")
                    return True # go into step mode
    return False

def print_debug_data(state):
    curr_address = state.get_pc()
    opcode = opcode_names[state.get_byte_at_pc()]
    print(f"Completed instruction: {opcode}")
    print(f"RAM slice: {state.get_ram(curr_address, curr_address+3).hex(' ')}")
    print(state)
    print()

def main():
    pygame.init()

    state = State(romstart=ROMSTART)
    display = Display(state)
    bus = Bus(state)
    cpu = CPU(state, bus)
    keyboard = Keyboard(bus)


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
    step = False
    print("Space to pause.")

    ### MAIN FRAME LOOP
    while(running):
        screen_bottom = False  # for interrupts

        # 1. Event handling loop
        # wait_for_input = True
        # while (wait_for_input):
        keyboard.get_state()
        if (keyboard.request_quit):
            running = False
        elif keyboard.request_pause:
            keyboard.clear_pause_request()
            step = wait_for_key(state)


        # 2. cpu frame
        current_cycles = 0

        next_step = False
        if step:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                next_step = True
        if (next_step and step) or not step:
            while (current_cycles < CPF):

                cycles = cpu.run_cycle()
                if (cycles is None):
                    print("Halt code executed.")
                    quit()
                elif cycles < 0:  # breakpoint
                    step = True
                    current_cycles -= cycles
                else:
                    current_cycles += cycles
                
                if step:
                    print_debug_data(state)

                # Interrupts here
                # RST 1 opcode at middle of frame
                if not screen_bottom and current_cycles >= (CPF // 2):
                    current_cycles += cpu.run_cycle(0xcf)
                    screen_bottom = True
                # RST 2 opcode at end of frame
                elif screen_bottom and current_cycles >= CPF:
                    current_cycles += cpu.run_cycle(0xd7)
                    screen_bottom = False


        # 4. Update display
        display.render_screen()

        # 5. sleep until FPS met
        clock.tick(FPS)
        



if __name__ == "__main__":
    main()

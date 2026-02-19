import pygame
from PygameDisplay import Display
from State import State
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

    clock = pygame.time.Clock()
    running = True

    # test vram data
    state.set_ram(0x2400, 0xf0)
    state.set_ram(0x3fff, 0xff)

    ### MAIN LOOP
    while(running):
        # 1. Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # Set the flag to False to break the while loop

        # 2. Update display
        display.render_screen()

        # 3. sleep until FPS met
        clock.tick(FPS)
        


if __name__ == "__main__":
    main()

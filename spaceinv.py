import pygame
# from PygameDisplay import Display
from State import State
# from Beeper import Beeper
# from Keyboard import Keyboard
from CPU import CPU


rom_filename = r'"C:\Users\Nick\source\repos\spaceinv\tests\8080PRE.COM"'

DEBUG = False
FPS = 60 # Frames per second - do not change!

ROMSTART = 0x0100

def main():

    pygame.init()

    state = State()
    cpu = CPU(state)


    #####################################################
    ### load the program rom
    with open(rom_filename,'rb') as file:
        full_rom = file.read()
        state.set_ram(full_rom, ROMSTART)


    clock = pygame.time.Clock()
    running = True
    if DEBUG:
        print("Press any key to advance to next frame.")

    ### MAIN LOOP
    while(running):
    
        # 1. Check events
        wait_for_input = True
        while (wait_for_input):
            keyboard.get_state()
            if (keyboard.request_quit):
                running = False
                wait_for_input = False
            elif (keyboard.is_pressed() or DEBUG != True):
                wait_for_input = False

        # 2. Manage timers
        state.decrement_delay_timer()
        sound_tx_value = state.decrement_sound_timer()
        if sound_tx_value > 0:
            beeper.play()
        else:
            beeper.stop()

        # 3. cpu cycle
        actual_cps = CYCLES_PER_FRAME if not DEBUG else 1
        for _ in range(actual_cps):
            cpu.run_cycle()

        # 4. Update display
        display.render_screen()

        # 5. sleep until FPS met
        clock.tick(FPS)
        

    display.quit()


if __name__ == "__main__":
    main()

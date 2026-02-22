import pygame
from Bus import Bus

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False # Set the flag to False to break the while loop
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_SPACE:
        #             step = wait_for_key(state)

class Keyboard():
    
    #     Port 1
#  bit 0 = CREDIT (1 if deposit)
#  bit 1 = 2P start (1 if pressed)
#  bit 2 = 1P start (1 if pressed)
#  bit 3 = Always 1
#  bit 4 = 1P shot (1 if pressed)
#  bit 5 = 1P left (1 if pressed)
#  bit 6 = 1P right (1 if pressed)
#  bit 7 = Not connected

    keytable = { 
        pygame.K_LEFT:  0,
        pygame.K_RIGHT: 1,
        pygame.K_UP:    2,
        pygame.K_c:     3,
        pygame.K_s:     4,
        }

    bustable = {
        # key: (port, bit)
        0: (1, 5),
        1: (1, 6),
        2: (1, 4),
        3: (1, 0),
        4: (1, 2),
    }


    def __init__(self, bus:Bus):
        pygame.init()
        self.bus = bus
        # current_state and previous_state hold true/false for each key
        # simulates a buffer chip
        self.previous_state = [False] * 16
        self.current_state = [False] * 16
        self.request_quit = False
        self.request_pause = False
    
    def clear_pause_request(self):
        self.request_pause = False

    def get_state(self):
        # self.previous_state = self.current_state.copy()
        update = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.request_quit = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.request_pause = True
            elif event.type == pygame.KEYDOWN and event.key in self.keytable:
                self.current_state[self.keytable[event.key]] = True
                update = True
            elif event.type == pygame.KEYUP and event.key in self.keytable:
                self.current_state[self.keytable[event.key]] = False
                update = True
        
        if update:
            self._update_bus()
        
    
    def _update_bus(self):
        # run through current state and update bus accordingly
        for index in self.bustable.keys():
            (port, bit) = self.bustable[index]
            self.bus.set_read_bit(port, bit, self.current_state[index])

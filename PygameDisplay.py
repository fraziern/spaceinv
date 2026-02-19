import pygame
from State import State
from utils import byte_to_bits

class Display():

    # unrotated video - landscape
    WIDTH = 256
    HEIGHT = 224
    BYTEWIDTH = WIDTH // 8

    # TODO cellophane
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self, state:State):
        pygame.init()

        self.state = state
        self.window = pygame.display.set_mode((self.HEIGHT, self.WIDTH))
        self.window.fill(self.BLACK)

        pygame.display.set_caption("Space Invaders")
        pygame.display.flip()

        self.pixel_surface = pygame.Surface((self.WIDTH, self.HEIGHT))
    
    def render_screen(self):
        # self.window.fill(self.BLACK)

        vram = self.state.get_ram(0x2400, 0x4000) # 7K VRAM

        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                bit_index = y*self.WIDTH + x
                byte_index = bit_index // 8
                offset = bit_index % 8 # bits are backwards visually, so bit 0 is at the left
                vram_pixel = bool(vram[byte_index] & (1 << offset))
                if vram_pixel:
                    self.pixel_surface.set_at((x, y), self.WHITE)
                else:
                    self.pixel_surface.set_at((x, y), self.BLACK)

        rotated_surface = pygame.transform.rotate(self.pixel_surface, 90)
        self.window.blit(rotated_surface, (0,0))
        pygame.display.flip()
                    

    
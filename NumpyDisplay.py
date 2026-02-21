import numpy as np
import pygame
import pygame.surfarray
from State import State

class Display():

    # unrotated video - landscape
    WIDTH = 256
    HEIGHT = 224

    # TODO cellophane
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self, state: State):
        pygame.init()

        self.state = state
        self.window = pygame.display.set_mode((self.HEIGHT, self.WIDTH))
        self.window.fill(self.BLACK)

        pygame.display.set_caption("Space Invaders")
        pygame.display.flip()

        self.pixel_surface = pygame.Surface((self.WIDTH, self.HEIGHT), depth=32)


    def clear_screen(self):
        self.window.fill(self.BLACK)
        pygame.display.flip()


    def render_screen(self):
        vram = self.state.get_ram(0x2400, 0x4000) # 7K VRAM

        # # Convert 7KB VRAM bytearray to numpy array, unpack bytes to individual bits
        vram_np = np.frombuffer(vram, dtype=np.uint8)
        pixels = np.unpackbits(vram_np, bitorder='little') # bit 0 = leftmost pixel

        pixels_2d = pixels.reshape((self.HEIGHT, self.WIDTH))
        mono = (pixels_2d * 255).astype(np.uint8)
        rgb = np.stack((mono,)*3, axis=-1)
        pygame.surfarray.blit_array(self.pixel_surface, rgb.transpose((1, 0, 2)))

        # Rotate 90° for vertical arcade orientation and display
        rotated_surface = pygame.transform.rotate(self.pixel_surface, 90)
        self.window.blit(rotated_surface, (0, 0))
        pygame.display.flip()

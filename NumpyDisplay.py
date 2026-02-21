import numpy as np
import pygame
import pygame.surfarray
from State import State

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

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
        self.window = pygame.display.set_mode((self.HEIGHT*2, self.WIDTH*3))
        self.window.fill(self.BLACK)

        pygame.display.set_caption("Space Invaders")
        pygame.display.flip()

        self.pixel_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        # Create cellophane overlay
        self.overlay_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.overlay_surface.fill((255,255,255))
        draw_rect_alpha(self.overlay_surface, (20, 204, 96, 150), (0, 0, 20, 70))
        draw_rect_alpha(self.overlay_surface, (20, 204, 96, 150), (20, 0, 20, 224))


    def _apply_glow(self, screen):
        width, height = screen.get_size()
        glow_surf = pygame.transform.smoothscale(screen, (width // 2, height // 2))
        glow_surf = pygame.transform.smoothscale(glow_surf, (width, height))
        glow_surf.set_alpha(100)
        screen.blit(glow_surf, (0, 0))

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
        # self.pixel_surface.blit(self.overlay_surface, (0, 0))
        self.pixel_surface.blit(self.overlay_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        rotated_surface = pygame.transform.rotate(self.pixel_surface, 90)
        scaled_surface = pygame.transform.scale(rotated_surface, (self.HEIGHT*2, self.WIDTH*3))

        glow_surf = pygame.transform.smoothscale(scaled_surface, (self.HEIGHT, self.WIDTH))
        glow_surf = pygame.transform.smoothscale(glow_surf, (self.HEIGHT*2, self.WIDTH*3))
        glow_surf.set_alpha(100)
        scaled_surface.blit(glow_surf, (0, 0))

        self.window.blit(scaled_surface, (0, 0))
        pygame.display.flip()


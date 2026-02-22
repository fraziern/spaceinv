import pygame
# 4 5 6 7 are fleet movement sounds
# correspond to bit 0-3 on output port 5

ufo_repeat_file =       r"samples\8.wav"
shot_file =             r"samples\3.wav"
flash_file =            r"samples\0.wav"
invader_die_file =      r"samples\2.wav"
fleet_movement_1_file = r"samples\4.wav"
fleet_movement_2_file = r"samples\5.wav"
fleet_movement_3_file = r"samples\6.wav"
fleet_movement_4_file = r"samples\7.wav"
ufo_hit_file =          r"samples\9.wav"


class Soundboard():

    def __init__(self):
        pygame.mixer.init()
        self.sounds = [
            pygame.mixer.Sound(ufo_repeat_file),
            pygame.mixer.Sound(shot_file),
            pygame.mixer.Sound(flash_file),
            pygame.mixer.Sound(invader_die_file),
            pygame.mixer.Sound(fleet_movement_1_file),
            pygame.mixer.Sound(fleet_movement_2_file),
            pygame.mixer.Sound(fleet_movement_3_file),
            pygame.mixer.Sound(fleet_movement_4_file),
            pygame.mixer.Sound(ufo_hit_file),
        ]

    def play(self, sound_index):
        # self.beep.play(10)
        if sound_index >= len(self.sounds):
            raise IndexError(f"Bad sound index: {sound_index}")
        if self.sounds[sound_index]:
            self.sounds[sound_index].play()



    
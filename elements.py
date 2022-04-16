import pygame
import time

from pygame.locals import SRCALPHA

from constants import BOLD_FONTS, VEC, Anchors
from utils import Sprite

class MainGameTimer(Sprite):
    def __init__(self, menu):
        menu.elements.append(self)
        self.menu = menu
        self.max_time = 15
        self.start_time = time.time()
        self.current_time = self.max_time - (time.time() - self.start_time)

    def update(self, dt):
        self.current_time = self.max_time - (time.time() - self.start_time)
        if self.current_time <= 0:
            self.menu.running = False
            self.menu.manager.new_menu("EndMenu")

    def draw(self, screen):
        self.text_surface = BOLD_FONTS[40].render(" " + str(int(self.current_time)) + " ", True, (230, 230, 230))
        self.size = self.text_surface.get_size()

        pygame.draw.rect(screen, (150, 150, 150), (0, 0, *self.size))
        screen.blit(self.text_surface, (0, 0))

        if self.current_time < 10 and self.current_time % 1 > 0.5:
            if 0.5 < self.current_time % 1 < 0.625:
                self.border_opacity = 255 * ((self.current_time % 1 - 0.5) / 0.125)
            elif 0.875 < self.current_time % 1 < 1:
                self.border_opacity = 255 * ((1 - self.current_time % 1) / 0.125)

            tmp_surf = pygame.Surface(self.size, SRCALPHA)
            pygame.draw.rect(tmp_surf, (208, 52, 44, self.border_opacity), (0, 0, *self.size), 4)
            screen.blit(tmp_surf, (0, 0))

class Label(Sprite):
    def __init__(self, menu, pos, text, font, color, anchor=Anchors.CENTER):
        menu.elements.append(self)
        self.surface = font.render(text, True, color)
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self, dt):
        # ...
        pass

    def draw(self, screen):
        screen.blit(self.surface, self.pos)

class Image(Sprite):
    def __init__(self, menu, pos, surface, anchor=Anchors.CENTER):
        menu.elements.append(self)
        self.surface = surface
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self, dt):
        # ...
        pass

    def draw(self, screen):
        screen.blit(self.surface, self.pos)
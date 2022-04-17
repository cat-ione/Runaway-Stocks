from abc import abstractmethod
import pygame
import time

from pygame.locals import SRCALPHA

from constants import BOLD_FONTS, VEC, Anchors
from utils import Sprite, pygame_draw_pie

class Element(Sprite):
    def __init__(self, manager):
        super().__init__(manager)
        self.scene.elements.append(self)

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class Label(Element):
    def __init__(self, manager, pos, text, font, color, anchor=Anchors.CENTER):
        super().__init__(manager)
        self.surface = font.render(text, True, color)
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self):
        # ...
        pass

    def draw(self):
        self.manager.screen.blit(self.surface, self.pos)

class Image(Element):
    def __init__(self, manager, pos, surface, anchor=Anchors.CENTER):
        super().__init__(manager)
        self.surface = surface
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self):
        # ...
        pass

    def draw(self):
        self.manager.screen.blit(self.surface, self.pos)

class Timer:
    def __init__(self, max_time):
        self.max_time = max_time
        self.start_time = time.time()
        self.current_time = self.max_time - (time.time() - self.start_time)
        self.ended = False

    def update(self):
        self.current_time = self.max_time - (time.time() - self.start_time)
        if self.current_time <= 0:
            self.ended = True

class MainGameTimer(Timer, Element):
    def __init__(self, manager):
        Element.__init__(self, manager)
        Timer.__init__(self, 60)

    def update(self):
        super().update()
        if self.ended:
            self.scene.running = False
            self.scene.manager.new_scene("EndMenu")

    def draw(self):
        self.text_surface = BOLD_FONTS[40].render(" " + str(int(self.current_time)) + " ", True, (230, 230, 230))
        self.size = self.text_surface.get_size()

        pygame.draw.rect(self.manager.screen, (150, 150, 150), (0, 0, *self.size))
        self.manager.screen.blit(self.text_surface, (0, 0))

        if self.current_time < 10 and self.current_time % 1 > 0.5:
            if 0.5 < self.current_time % 1 < 0.625:
                self.border_opacity = 255 * ((self.current_time % 1 - 0.5) / 0.125)
            elif 0.875 < self.current_time % 1 < 1:
                self.border_opacity = 255 * ((1 - self.current_time % 1) / 0.125)

            tmp_surf = pygame.Surface(self.size, SRCALPHA)
            pygame.draw.rect(tmp_surf, (208, 52, 44, self.border_opacity), (0, 0, *self.size), 4)
            self.manager.screen.blit(tmp_surf, (0, 0))

class TimeIndicator(Timer, Sprite):
    def __init__(self, manager, max_time):
        super().__init__(manager=manager, max_time=max_time)

    def update(self):
        super().update()
        if self.ended:
            pass

    def draw(self):
        pygame_draw_pie(self.manager.screen, (255, 255, 255, 100), self.scene.manager.player.pos, 50, 0, self.current_time / self.max_time * 360)
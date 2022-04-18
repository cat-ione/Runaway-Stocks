from __future__ import annotations
from typing import TYPE_CHECKING

from numpy import cos, radians, sin

if TYPE_CHECKING: from manager import GameManager

from abc import abstractmethod
import pygame
import time

from pygame.locals import SRCALPHA

from constants import BOLD_FONTS, VEC, Anchors, _pos, _color
from barrier_powers import Power, barrier_powers
from utils import Sprite, pygame_draw_pie
from effects import Shockwave

class Element(Sprite):
    def __init__(self, manager: GameManager) -> None:
        super().__init__(manager)
        self.scene.elements.append(self)

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

class Label(Element):
    def __init__(self, manager: GameManager, pos: _pos, text: str, font: pygame.font.Font, color: _color, anchor: Anchors = Anchors.CENTER) -> None:
        super().__init__(manager)
        self.surface = font.render(text, True, color)
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self) -> None:
        # ...
        pass

    def draw(self) -> None:
        self.manager.screen.blit(self.surface, self.pos)

class Image(Element):
    def __init__(self, manager: GameManager, pos: _pos, surface: pygame.Surface, anchor: Anchors = Anchors.CENTER) -> None:
        super().__init__(manager)
        self.surface = surface
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self) -> None:
        # ...
        pass

    def draw(self) -> None:
        self.manager.screen.blit(self.surface, self.pos)

class Timer:
    def __init__(self, max_time: int) -> None:
        self.max_time = max_time
        self.start_time = time.time()
        self.current_time = self.max_time - (time.time() - self.start_time)
        self.ended = False

    def update(self) -> None:
        self.current_time = self.max_time - (time.time() - self.start_time)
        if self.current_time <= 0:
            self.ended = True

class MainGameTimer(Timer, Element):
    def __init__(self, manager: GameManager) -> None:
        Element.__init__(self, manager)
        Timer.__init__(self, 60)

    def update(self) -> None:
        super().update()
        if self.ended:
            self.scene.running = False
            self.scene.manager.new_scene("EndMenu")

    def draw(self) -> None:
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

class PowerTimer(Timer, Element):
    instances = {power: [] for power in barrier_powers}
    
    def __init__(self, manager: GameManager, power: Power) -> None:
        self.__class__.instances[power].append(self)
        Element.__init__(self, manager)
        self.power = power
        self.power.init = True
        self.power.reset(manager)
        Timer.__init__(self, self.power.max_time)

    def update(self) -> None:
        super().update()
        if self.ended:
            self.power.init = False
            Shockwave(self.manager, self.scene.player.pos, (180, 180, 180), 8, 160, 14)
            self.scene.elements.remove(self)
            self.__class__.instances[self.power].remove(self)
            del self

    def draw(self) -> None:
        center = self.scene.player.pos - self.scene.player.camera.offset
        angle = int(self.current_time / self.max_time * 360) + 180
        rad = 35
        pygame_draw_pie(self.manager.screen, (255, 255, 255, 70), center, rad, 180, angle)
        pygame.draw.line(self.manager.screen, (150, 150, 150), center, center + VEC(sin(radians(180)), -cos(radians(180))) * rad, 1)
        pygame.draw.line(self.manager.screen, (150, 150, 150), center, center + VEC(sin(radians(angle)), -cos(radians(angle))) * rad, 1)
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

from numpy import cos, radians, sin
from pygame.locals import SRCALPHA
import pygame

from src.game.effects import Shockwave, PowerTimerPlayerDisplay
from src.game.barrier_powers import Power, barrier_powers
from src.management.sprite import VisibleSprite, Layers
from src.common.constants import BOLD_FONTS, VEC
from src.common.utils import pygame_draw_pie
from src.common.images import power_images
from src.common.timer import ComplexTimer
from src.common.audio import power_end

class MainGameTimer(ComplexTimer, VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        VisibleSprite.__init__(self, scene, Layers.HUD)
        ComplexTimer.__init__(self, 5)

    def update(self) -> None:
        super().update()
        if self.ended:
            self.scene.manager.new_scene("EndMenu")

    def draw(self) -> None:
        self.text_surface = BOLD_FONTS[40].render(" " + str(int(self.current_time)) + " ", True, (230, 230, 230))
        self.size = self.text_surface.get_size() + VEC(0, 2)

        trans_surf = pygame.Surface(self.size, SRCALPHA)
        trans_surf.fill((150, 150, 150, 150))
        self.scene.surface.blit(trans_surf, (0, 0))
        self.scene.surface.blit(self.text_surface, (0, 0))

        if self.current_time < 10 and self.current_time % 1 > 0.5:
            if 0.5 < self.current_time % 1 < 0.625:
                self.border_opacity = 255 * ((self.current_time % 1 - 0.5) / 0.125)
            elif 0.875 < self.current_time % 1 < 1:
                self.border_opacity = 255 * ((1 - self.current_time % 1) / 0.125)

            tmp_surf = pygame.Surface(self.size, SRCALPHA)
            pygame.draw.rect(tmp_surf, (208, 52, 44, self.border_opacity), (0, 0, *self.size), 4)
            self.scene.surface.blit(tmp_surf, (0, 0))

class PowerTimer(ComplexTimer, VisibleSprite):
    instances = []
    sorted_instances = {power: [] for power in barrier_powers}
    
    def __init__(self, scene: Scene, power: Power) -> None:
        self.__class__.instances.insert(0, self)
        self.__class__.sorted_instances[power].append(self)
        VisibleSprite.__init__(self, scene, Layers.HUD)
        self.power = power
        self.power.init = True
        self.power.reset(scene)
        ComplexTimer.__init__(self, self.power.max_time)
        self.player_display = PowerTimerPlayerDisplay(scene, self)

    def update(self) -> None:
        super().update()
        if self.ended:
            self.kill()

    def draw(self) -> None:
        rad = 24
        center = VEC(0 + rad + 5, 50 + rad + 10 + self.__class__.instances.index(self) * 50)
        angle = int(self.current_time / self.max_time * 360)
        pygame_draw_pie(self.scene.surface, (255, 255, 255, 120), center, rad, 0, angle)
        pygame.draw.line(self.scene.surface, (200, 200, 200), center, center + VEC(sin(radians(0)), -cos(radians(0))) * rad, 2)
        pygame.draw.line(self.scene.surface, (200, 200, 200), center, center + VEC(sin(radians(angle)), -cos(radians(angle))) * rad, 2)
        self.scene.surface.blit(power_images[self.power.__name__.lower()], center - (16, 16))

    def kill(self) -> None:
        if self.scene.__class__.__name__ == "MainGame":
            power_end.play()
        self.power.init = False
        Shockwave(self.scene, self.scene.player.pos, (180, 180, 180), 8, 160, 14)
        self.player_display.kill()
        self.__class__.instances.remove(self)
        try:
            self.__class__.sorted_instances[self.power].remove(self)
        except ValueError:
            pass
        super().kill()
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from manager import GameManager

from pygame.locals import SRCALPHA
from random import randint
import pygame

from constants import FONTS, VEC, _pos, BULL_COLOR, BEAR_COLOR
from effects import Particle, Shockwave
from utils import Sprite, inttup

class Points(Sprite):
    instances = {}
    
    @classmethod
    def update_all(cls) -> None:
        for instance in cls.instances.copy().values():
            instance.update()

    @classmethod
    def draw_all(cls) -> None:
        for instance in cls.instances.values():
            instance.draw()

    def __init__(self, manager: GameManager, val: int, pos: _pos) -> None:
        super().__init__(manager)
        __class__.instances[pos] = self
        self.val = val
        self.color = BULL_COLOR if self.val > 0 else BEAR_COLOR
        self.pos = VEC(pos)

    def update(self) -> None:
        if self.pos.distance_to(self.scene.player.pos) < 10:
            self.scene.player.score += self.val
            self.kill()
            return
        screen_pos = self.pos - self.scene.player.camera.offset
        if screen_pos.x < -50:
            self.delete()

    def draw(self) -> None:
        draw_center = self.pos - self.scene.player.camera.offset
        r = 6
        trans_surf = pygame.Surface((r * 2, r * 2), SRCALPHA)
        pygame.draw.circle(trans_surf, (*self.color, 100), (r, r), r)
        self.manager.screen.blit(trans_surf, draw_center - VEC(r, r))
        pygame.draw.circle(self.manager.screen, self.color, draw_center, r - 2)
        self.manager.screen.blit(FONTS[16].render(str(self.val), True, self.color), draw_center + VEC(3, 1))

    def kill(self) -> None:
        for _ in range(randint(60, 80)):
            Particle(self.manager, self.pos, self.color)
        Shockwave(self.manager, self.pos, self.color, 5, 50, 6)
        self.delete()

    def delete(self) -> None:
        del __class__.instances[inttup(self.pos)]
        del self
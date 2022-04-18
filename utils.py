from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from manager import GameManager

from abc import ABC as AbstractClass
from numpy import sin, cos, radians
from abc import abstractmethod
import pygame.gfxdraw
import pygame

from constants import VEC, _pos, _color

inttup = lambda tup: tuple(map(int, tuple(tup)))
intvec = lambda vec: VEC(int(vec.x), int(vec.y))

def pygame_draw_pie(screen: pygame.Surface, color: _color, center: _pos, rad: int, start_ang: int, end_ang: int, step: int = 10):
    if end_ang <= start_ang:
        return
    vertices = [center]
    for angle in range(start_ang, end_ang + 1, step):
        vertices.append(center + VEC(sin(radians(angle)), -cos(radians(angle))) * rad)
    last_angle = radians(angle + end_ang % step)
    vertices.append(center + VEC(sin(last_angle), -cos(last_angle)) * rad)
    pygame.gfxdraw.filled_polygon(screen, vertices, color)

class Sprite(AbstractClass):
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager
        self.scene = self.manager.scene

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass
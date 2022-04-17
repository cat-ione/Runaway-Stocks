from abc import ABC as AbstractClass
from numpy import sin, cos, radians
from abc import abstractmethod
import pygame.gfxdraw

from constants import VEC

inttup = lambda tup: tuple(map(int, tuple(tup)))
intvec = lambda vec: VEC(int(vec.x), int(vec.y))

def pygame_draw_pie(screen, color, center, rad, start_ang, end_ang, step=10):
    vertices = [center]
    for angle in range(start_ang, end_ang + 1, step):
        vertices.append(center + VEC(sin(radians(angle)), -cos(radians(angle))) * rad)
    last_angle = radians(angle + end_ang % step)
    vertices.append(center + VEC(sin(last_angle), -cos(last_angle)) * rad)
    pygame.gfxdraw.filled_polygon(screen, vertices, color)

class Sprite(AbstractClass):
    def __init__(self, manager) -> None:
        self.manager = manager
        self.scene = self.manager.scene

    @abstractmethod
    def update(self, dt) -> None:
        pass

    @abstractmethod
    def draw(self, screen) -> None:
        pass
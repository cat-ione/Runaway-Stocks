from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from manager import GameManager

from random import randint, choices
import pygame

from barrier_powers import BarrierPower, barrier_powers
from constants import WIDTH, HEIGHT, GRID_SPACE, VEC
from effects import Particle, Shockwave
from elements import TimeIndicator
from points import Points
from utils import Sprite

class HorizontalGridline(Sprite):
    instances = {}

    @classmethod
    def update_all(cls, manager: GameManager) -> None:
        player = manager.scene.player
        on_screen_lines = set()
        for y in range(int(player.pos.y / GRID_SPACE.y - WIDTH / GRID_SPACE.y / 2 - 1), int(player.pos.y / GRID_SPACE.y + WIDTH / GRID_SPACE.y / 2 + 2)):
            on_screen_lines.add(y)
            if y not in cls.instances:
                cls(manager, y)
        for unrendered_line in set(cls.instances.keys()) - on_screen_lines:
            del cls.instances[unrendered_line]
        for instance in cls.instances.copy().values():
            instance.update()
            
    @classmethod
    def draw_all(cls) -> None:
        for instance in cls.instances.values():
            instance.draw()

    def __init__(self, manager: GameManager, y: int) -> None:
        super().__init__(manager)
        __class__.instances[y] = self
        self.y = y
        for _ in range(randint(1, 3)):
            Points(self.manager, randint(-10, 10), (GRID_SPACE.x * randint(int(self.scene.player.pos.x / GRID_SPACE.x - HEIGHT / GRID_SPACE.x - 10), int(self.scene.player.pos.x / GRID_SPACE.x + HEIGHT / GRID_SPACE.x + 10)), GRID_SPACE.y * self.y))

    def update(self) -> None:
        self.on_screen_start = VEC(0, self.y * GRID_SPACE.y - self.scene.player.camera.offset.y)
        self.on_screen_end = VEC(WIDTH, self.y * GRID_SPACE.y - self.scene.player.camera.offset.y)

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (150, 150, 150), self.on_screen_start, self.on_screen_end)

class VerticalGridline(Sprite):
    instances = {}

    @classmethod
    def update_all(cls, manager: GameManager) -> None:
        player = manager.scene.player
        on_screen_lines = set()
        for x in range(int(player.pos.x / GRID_SPACE.x - WIDTH / GRID_SPACE.x / 2 - 1), int(player.pos.x / GRID_SPACE.x + WIDTH / GRID_SPACE.x / 2 + 2)):
            on_screen_lines.add(x)
            if x not in cls.instances:
                cls(manager, x)
                if randint(0, 24) == 0 and not Barrier.instance:
                    Barrier(manager, x, choices(list(barrier_powers.keys()), list(barrier_powers.values()))[0])
        for unrendered_line in set(cls.instances.keys()) - on_screen_lines:
            del cls.instances[unrendered_line]
        for instance in cls.instances.copy().values():
            instance.update()

    @classmethod
    def draw_all(cls) -> None:
        for instance in cls.instances.values():
            instance.draw()

    def __init__(self, manager: GameManager, x: int) -> None:
        super().__init__(manager)
        __class__.instances[x] = self
        self.x = x
        for _ in range(randint(1, 4)):
            Points(self.manager, randint(-10, 10), (GRID_SPACE.x * self.x, GRID_SPACE.y * randint(int(self.scene.player.pos.y / GRID_SPACE.y - HEIGHT / GRID_SPACE.y / 2 - 10), int(self.scene.player.pos.y / GRID_SPACE.y + HEIGHT / GRID_SPACE.y / 2 + 10))))
        self.on_screen_start = VEC(0, 0)
        self.on_screen_end = VEC(0, 0)

    def update(self) -> None:
        self.on_screen_start = VEC(self.x * GRID_SPACE.x - self.scene.player.camera.offset.x, 0)
        self.on_screen_end = VEC(self.x * GRID_SPACE.x - self.scene.player.camera.offset.x, HEIGHT)
        if self.on_screen_start.x < -100:
            try:
                del __class__.instances[self.x]
            except KeyError:
                pass
            del self

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (150, 150, 150), self.on_screen_start, self.on_screen_end)

class Barrier(VerticalGridline):
    instance = None

    @classmethod
    def update_all(cls) -> None:
        if cls.instance:
            cls.instance.update()

    @classmethod
    def draw_all(cls) -> None:
        if cls.instance:
            cls.instance.draw()

    def __init__(self, manager: GameManager, x: int, power: BarrierPower) -> None:
        Sprite.__init__(self, manager)
        self.__class__.instance = self
        self.x = x
        self.power = power

    def update(self) -> None:
        if self.x * GRID_SPACE.x < self.scene.player.pos.x < self.x * GRID_SPACE.x + 25:
            self.power(self.manager)
            for _ in range(400):
                Particle(self.manager, (self.x * GRID_SPACE.x, randint(self.on_screen_start.y - 100, self.on_screen_end.y + 100) + self.scene.player.camera.offset.y), (180, 180, 180))
            Shockwave(self.manager, self.scene.player.pos, (180, 180, 180), 10, 160, 14)
            self.__class__.instance = None
            del self
            return
        if self.x * GRID_SPACE.x < -100:
            self.__class__.instance = None
            del self
            return
        super().update()

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (180, 180, 180), self.on_screen_start, self.on_screen_end, 4)
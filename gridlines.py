from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING: from manager import GameManager

from random import randint, choices
import pygame

from constants import WIDTH, HEIGHT, GRID_SPACE, VEC
from barrier_powers import Power, barrier_powers
from effects import Particle, Shockwave
from elements import PowerTimer
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
                chosen_power = choices(list(barrier_powers.keys()), list(barrier_powers.values()))[0]
                try:
                    if randint(0, 50 - (x - Barrier.last_position) + (50 if chosen_power.init else 0)) == 0 and not Barrier.instance:
                        Barrier(manager, x, chosen_power)
                # There are cases where the randint range is negative thus erroring, in the case of that, create a Barrier
                except ValueError:
                    Barrier(manager, x, chosen_power)
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
    last_position = 0

    @classmethod
    def update_all(cls) -> None:
        if cls.instance:
            cls.instance.update()

    @classmethod
    def draw_all(cls) -> None:
        if cls.instance:
            cls.instance.draw()

    def __init__(self, manager: GameManager, x: int, power: Power) -> None:
        Sprite.__init__(self, manager)
        self.__class__.instance = self
        self.x = x
        self.power = power
        self.__class__.last_position = self.x

    def update(self) -> None:
        if self.x * GRID_SPACE.x < self.scene.player.pos.x < self.x * GRID_SPACE.x + 25:
            if PowerTimer.sorted_instances[self.power] and not self.power.stackable:
                self.power.init = False
                try:
                    self.manager.scene.elements.remove(PowerTimer.sorted_instances[self.power][0])
                except ValueError: # Sometimes the PowerTimer no longer exists FSR so idk
                    pass
                del PowerTimer.sorted_instances[self.power][0]
            else:
                PowerTimer(self.manager, self.power)
            self.effects()
            self.kill()
            return
        if self.x * GRID_SPACE.x < -100:
            self.kill()
            return
        super().update()

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (180, 180, 180), self.on_screen_start, self.on_screen_end, 4)
        
    def kill(self) -> None:
        self.__class__.instance = None
        del self
        
    def effects(self) -> None:
        for _ in range(400):
            Particle(self.manager, (self.x * GRID_SPACE.x, randint(self.on_screen_start.y - 100, self.on_screen_end.y + 100) + self.scene.player.camera.offset.y), (180, 180, 180))
        Shockwave(self.manager, self.scene.player.pos, (180, 180, 180), 10, 160, 14)
        self.manager.scene.player.camera.shaking = True
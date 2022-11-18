from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

from random import randint, choices, sample
from math import ceil
import pygame

from src.common.constants import WIDTH, HEIGHT, GRID_SPACE, VEC
from src.game.barrier_powers import Power, barrier_powers
from src.management.sprite import VisibleSprite, Layers
from src.game.effects import Particle, Shockwave
from src.common.audio import break_barrier
from src.game.points import Point
from src.gui.hud import PowerTimer

class GridManager:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.manager = self.scene.manager
        for line in VerticalGridline.instances.copy():
            VerticalGridline.instances[line].kill()
        for line in HorizontalGridline.instances.copy():
            HorizontalGridline.instances[line].kill()

    def update_horizontal(self) -> None:
        player = self.scene.player
        lines_range = (
            ceil(player.pos.y / GRID_SPACE.y - HEIGHT / GRID_SPACE.y / 2 - 1),
            ceil(player.pos.y / GRID_SPACE.y + HEIGHT / GRID_SPACE.y / 2 + 2)
        )
        for y in HorizontalGridline.instances.copy():
            if not lines_range[0] <= y < lines_range[1]:
                HorizontalGridline.instances[y].kill()
        for y in range(*lines_range):
            if y not in HorizontalGridline.instances:
                HorizontalGridline(self.scene, y)
        for instance in HorizontalGridline.instances.copy().values():
            instance.update()

    def update_vertical(self) -> None:
        player = self.scene.player
        lines_range = (
            ceil(player.pos.x / GRID_SPACE.x - WIDTH / GRID_SPACE.x / 2 - 1),
            ceil(player.pos.x / GRID_SPACE.x + WIDTH / GRID_SPACE.x / 2 + 2)
        )
        for x in VerticalGridline.instances.copy():
            if not lines_range[0] <= x < lines_range[1]:
                VerticalGridline.instances[x].kill()
        for x in range(*lines_range):
            if x not in VerticalGridline.instances:
                VerticalGridline(self.scene, x)
                chosen_power = choices(list(barrier_powers.keys()), list(barrier_powers.values()))[0]
                try:
                    if randint(0, 50 - (x - Barrier.last_position) + (50 if chosen_power.init else 0)) == 0 and not Barrier.instance:
                        Barrier(self.scene, x, chosen_power)
                # There are cases where the randint range is negative thus erroring, in the case of that, create a Barrier
                except ValueError:
                    Barrier(self.scene, x, chosen_power)
        for instance in VerticalGridline.instances.copy().values():
            instance.update()

    def update(self) -> None:
        self.update_horizontal()
        self.update_vertical()

class HorizontalGridline(VisibleSprite):
    instances = {}

    def __init__(self, scene: Scene, y: int) -> None:
        super().__init__(scene, Layers.GRID)
        self.__class__.instances[y] = self
        self.y = y

    def update(self) -> None:
        self.on_screen_start = VEC(0, self.y * GRID_SPACE.y - self.scene.player.camera.offset.y)
        self.on_screen_end = VEC(WIDTH, self.y * GRID_SPACE.y - self.scene.player.camera.offset.y)

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (120, 120, 120), self.on_screen_start, self.on_screen_end, 2)
        pygame.draw.line(self.manager.screen, (80, 80, 80), self.on_screen_start + (0, 2), self.on_screen_end + (0, 2), 1)

    def kill(self) -> None:
        try:
            del self.__class__.instances[self.y]
        except KeyError:
            pass
        super().kill()

class VerticalGridline(VisibleSprite):
    instances = {}

    def __init__(self, scene: Scene, x: int) -> None:
        super().__init__(scene, Layers.GRID)
        self.__class__.instances[x] = self
        self.x = x
        y_range = (
            int(self.scene.player.pos.y / GRID_SPACE.y - HEIGHT / GRID_SPACE.y / 2 - 18),
            int(self.scene.player.pos.y / GRID_SPACE.y + HEIGHT / GRID_SPACE.y / 2 + 18)
        )
        for y in sample(range(*y_range), randint(4, 7)):
            Point(self.scene, randint(-10, 10), (GRID_SPACE.x * self.x, GRID_SPACE.y * y))

    def update(self) -> None:
        self.on_screen_start = VEC(self.x * GRID_SPACE.x - self.scene.player.camera.offset.x, 0)
        self.on_screen_end = VEC(self.x * GRID_SPACE.x - self.scene.player.camera.offset.x, HEIGHT)

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (120, 120, 120), self.on_screen_start, self.on_screen_end, 2)
        pygame.draw.line(self.manager.screen, (80, 80, 80), self.on_screen_start + (2, 0), self.on_screen_end + (2, 0), 1)

    def kill(self) -> None:
        try:
            del self.__class__.instances[self.x]
        except KeyError:
            pass
        super().kill()

class Barrier(VerticalGridline):
    instance = None
    last_position = 0

    @classmethod
    def reset(cls):
        cls.instance = None
        cls.last_position = 0
        for power in barrier_powers:
            power.init = False

    def __init__(self, scene: Scene, x: int, power: Power) -> None:
        VisibleSprite.__init__(self, scene, Layers.BARRIERS)
        self.__class__.instance = self
        self.x = x
        self.power = power
        self.__class__.last_position = self.x
        self.on_screen_start = VEC(0, 0)
        self.on_screen_end = VEC(0, 0)

    def update(self) -> None:
        if self.x * GRID_SPACE.x < self.scene.player.pos.x < self.x * GRID_SPACE.x + 25:
            if PowerTimer.sorted_instances[self.power] and not self.power.stackable:
                self.power.init = False
                del PowerTimer.sorted_instances[self.power][0]
            else:
                PowerTimer(self.scene, self.power)
            self.scene.slowdown = 0.5
            self.effects()
            self.kill()
            return
        if self.x * GRID_SPACE.x < -100:
            self.kill()
            return
        super().update()

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (60, 60, 60), self.on_screen_start, self.on_screen_end, 10)
        pygame.draw.line(self.manager.screen, (110, 110, 110), self.on_screen_start, self.on_screen_end, 6)
        pygame.draw.line(self.manager.screen, (180, 180, 180), self.on_screen_start, self.on_screen_end, 4)
        
    def kill(self) -> None:
        self.__class__.instance = None
        super().kill()
        
    def effects(self) -> None:
        if self.scene.__class__.__name__ == "MainGame":
            break_barrier.play()
        for _ in range(400):
            Particle(self.scene, (self.x * GRID_SPACE.x, randint(self.on_screen_start.y - 100, self.on_screen_end.y + 100) + self.scene.player.camera.offset.y), (180, 180, 180))
        Shockwave(self.scene, self.scene.player.pos, (180, 180, 180), 10, 160, 14)
        self.scene.player.camera.shake(0.3, 6)
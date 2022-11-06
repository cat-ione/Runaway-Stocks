from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager
    from scene import Scene

from random import randint, choices, sample
import pygame

from constants import WIDTH, HEIGHT, GRID_SPACE, VEC
from barrier_powers import Power, barrier_powers
from sprite import VisibleSprite, Layers
from effects import Particle, Shockwave
from hud import PowerTimer
from points import Point

class GridManager:
    def __init__(self, manager: GameManager, scene: Scene = None) -> None:
        self.manager = manager
        self.scene = scene if scene else self.manager.scene
        for line in VerticalGridline.instances.copy():
            VerticalGridline.instances[line].kill()
        for line in HorizontalGridline.instances.copy():
            HorizontalGridline.instances[line].kill()

    def update_horizontal(self) -> None:
        player = self.scene.player
        on_screen_lines = set()
        lines_range = (
            int(player.pos.y / GRID_SPACE.y - WIDTH / GRID_SPACE.y / 2 - 1),
            int(player.pos.y / GRID_SPACE.y + WIDTH / GRID_SPACE.y / 2 + 2)
        )
        for y in range(*lines_range):
            on_screen_lines.add(y)
            if y not in HorizontalGridline.instances:
                HorizontalGridline(self.manager, y, self.scene)
        for unrendered_line in set(HorizontalGridline.instances.keys()) - on_screen_lines:
            del HorizontalGridline.instances[unrendered_line]
        for instance in HorizontalGridline.instances.copy().values():
            instance.update()

    def update_vertical(self) -> None:
        player = self.scene.player
        on_screen_lines = set()
        lines_range = (
            int(player.pos.x / GRID_SPACE.x - WIDTH / GRID_SPACE.x / 2 - 1),
            int(player.pos.x / GRID_SPACE.x + WIDTH / GRID_SPACE.x / 2 + 2)
        )
        for x in range(*lines_range):
            on_screen_lines.add(x)
            if x not in VerticalGridline.instances:
                VerticalGridline(self.manager, x, self.scene)
                chosen_power = choices(list(barrier_powers.keys()), list(barrier_powers.values()))[0]
                try:
                    if randint(0, 50 - (x - Barrier.last_position) + (50 if chosen_power.init else 0)) == 0 and not Barrier.instance:
                        Barrier(self.manager, x, chosen_power, self.scene)
                # There are cases where the randint range is negative thus erroring, in the case of that, create a Barrier
                except ValueError:
                    Barrier(self.manager, x, chosen_power, self.scene)
        for unrendered_line in set(VerticalGridline.instances.keys()) - on_screen_lines:
            del VerticalGridline.instances[unrendered_line]
        for instance in VerticalGridline.instances.copy().values():
            instance.update()

    def update(self) -> None:
        self.update_horizontal()
        self.update_vertical()

class HorizontalGridline(VisibleSprite):
    instances = {}

    def __init__(self, manager: GameManager, y: int, scene: Scene = None) -> None:
        super().__init__(manager, Layers.GRID, scene)
        self.__class__.instances[y] = self
        self.y = y

    def update(self) -> None:
        self.on_screen_start = VEC(0, self.y * GRID_SPACE.y - self.scene.player.camera.offset.y)
        self.on_screen_end = VEC(WIDTH, self.y * GRID_SPACE.y - self.scene.player.camera.offset.y)

    def draw(self) -> None:
        pygame.draw.line(self.manager.screen, (120, 120, 120), self.on_screen_start, self.on_screen_end, 2)
        pygame.draw.line(self.manager.screen, (80, 80, 80), self.on_screen_start + (0, 2), self.on_screen_end + (0, 2), 1)
        if not -100 < self.on_screen_start.y < HEIGHT + 100:
            self.kill()

    def kill(self) -> None:
        try:
            del __class__.instances[self.y]
        except KeyError:
            pass
        super().kill()

class VerticalGridline(VisibleSprite):
    instances = {}

    def __init__(self, manager: GameManager, x: int, scene: Scene = None) -> None:
        super().__init__(manager, Layers.GRID, scene)
        self.__class__.instances[x] = self
        self.x = x
        y_range = (
            int(self.scene.player.pos.y / GRID_SPACE.y - HEIGHT / GRID_SPACE.y / 2 - 18),
            int(self.scene.player.pos.y / GRID_SPACE.y + HEIGHT / GRID_SPACE.y / 2 + 18)
        )
        for y in sample(range(*y_range), randint(4, 7)):
            Point(self.manager, randint(-10, 10), (GRID_SPACE.x * self.x, GRID_SPACE.y * y), self.scene)

    def update(self) -> None:
        self.on_screen_start = VEC(self.x * GRID_SPACE.x - self.scene.player.camera.offset.x, 0)
        self.on_screen_end = VEC(self.x * GRID_SPACE.x - self.scene.player.camera.offset.x, HEIGHT)
        if self.on_screen_start.x < -10:
            self.kill()

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

    def __init__(self, manager: GameManager, x: int, power: Power, scene: Scene = None) -> None:
        VisibleSprite.__init__(self, manager, Layers.BARRIERS, scene)
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
                PowerTimer(self.manager, self.power, self.scene)
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
        for _ in range(400):
            Particle(self.manager, (self.x * GRID_SPACE.x, randint(self.on_screen_start.y - 100, self.on_screen_end.y + 100) + self.scene.player.camera.offset.y), (180, 180, 180), self.scene)
        Shockwave(self.manager, self.scene.player.pos, (180, 180, 180), 10, 160, 14, self.scene)
        self.scene.player.camera.shake(0.3, 6)
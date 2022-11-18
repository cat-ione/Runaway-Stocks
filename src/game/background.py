from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

from random import randint, choice, sample
import pygame.gfxdraw
import pygame

from src.common.constants import WIDTH, HEIGHT, BG_GRID_SPACE, VEC, BG_PARALLAX, _pair, _color, BG_BULL_COLOR, BG_BEAR_COLOR
from src.management.sprite import VisibleSprite, Layers

class BGGridManager:
    def __init__(self, scene: Scene = None) -> None:
        self.scene = scene
        self.manager = scene.manager
        for line in BGVerticalGridline.instances.copy():
            BGVerticalGridline.instances[line].kill()
        for line in BGHorizontalGridline.instances.copy():
            BGHorizontalGridline.instances[line].kill()

    def update_horizontal(self) -> None:
        player = self.scene.player
        on_screen_lines = set()
        lines_range = (
            int(player.pos.y / BG_GRID_SPACE.y - WIDTH / BG_GRID_SPACE.y / 2 - 1),
            int(player.pos.y / BG_GRID_SPACE.y + WIDTH / BG_GRID_SPACE.y / 2 + 2)
        )
        for y in range(*lines_range):
            on_screen_lines.add(y)
            if y not in BGHorizontalGridline.instances:
                BGHorizontalGridline(self.scene, y)
        for unrendered_line in set(BGHorizontalGridline.instances.keys()) - on_screen_lines:
            del BGHorizontalGridline.instances[unrendered_line]
        for instance in BGHorizontalGridline.instances.copy().values():
            instance.update()

    def update_vertical(self) -> None:
        player = self.scene.player
        on_screen_lines = set()
        lines_range = (
            int(player.pos.x / BG_GRID_SPACE.x - WIDTH / BG_GRID_SPACE.x / 2 - 1),
            int(player.pos.x / BG_GRID_SPACE.x + WIDTH / BG_GRID_SPACE.x / 2 + 2)
        )
        for x in range(*lines_range):
            on_screen_lines.add(x)
            if x not in BGVerticalGridline.instances:
                BGVerticalGridline(self.scene, x)
        for unrendered_line in set(BGVerticalGridline.instances.keys()) - on_screen_lines:
            del BGVerticalGridline.instances[unrendered_line]
        for instance in BGVerticalGridline.instances.copy().values():
            instance.update()

    def update(self) -> None:
        self.update_horizontal()
        self.update_vertical()

class BGHorizontalGridline(VisibleSprite):
    instances = {}

    def __init__(self, scene: Scene, y: int) -> None:
        super().__init__(scene, Layers.BACKGROUND_GRID)
        self.__class__.instances[y] = self
        self.y = y

    def update(self) -> None:
        self.on_screen_start = VEC(0, self.y * BG_GRID_SPACE.y - self.scene.player.camera.offset.y * BG_PARALLAX)
        self.on_screen_end = VEC(WIDTH, self.y * BG_GRID_SPACE.y - self.scene.player.camera.offset.y * BG_PARALLAX)
        if not -40 < self.on_screen_start.y < HEIGHT + 40:
            self.kill()

    def draw(self) -> None:
        pygame.gfxdraw.hline(self.manager.screen, int(self.on_screen_start.x), int(self.on_screen_end.y), int(self.on_screen_start.y), (50, 50, 50))

    def kill(self) -> None:
        try:
            del __class__.instances[self.y]
        except KeyError:
            pass
        super().kill()

class BGVerticalGridline(VisibleSprite):
    instances = {}

    def __init__(self, scene: Scene, x: int) -> None:
        super().__init__(scene, Layers.BACKGROUND_GRID)
        self.__class__.instances[x] = self
        self.x = x
        y_range = (
            int(self.scene.player.pos.y / BG_GRID_SPACE.y - HEIGHT / BG_GRID_SPACE.y / 2 - 24),
            int(self.scene.player.pos.y / BG_GRID_SPACE.y + HEIGHT / BG_GRID_SPACE.y / 2 + 24)
        )
        for y in sample(range(*y_range), randint(3, 5)):
            BGPoint(self.scene, (BG_GRID_SPACE.x * self.x, BG_GRID_SPACE.y * y), choice([BG_BULL_COLOR, BG_BEAR_COLOR]))

    def update(self) -> None:
        self.on_screen_start = VEC(self.x * BG_GRID_SPACE.x - self.scene.player.camera.offset.x * BG_PARALLAX, 0)
        self.on_screen_end = VEC(self.x * BG_GRID_SPACE.x - self.scene.player.camera.offset.x * BG_PARALLAX, HEIGHT)
        if self.on_screen_start.x < -10:
            self.kill()

    def draw(self) -> None:
        pygame.gfxdraw.vline(self.manager.screen, int(self.on_screen_start.x), int(self.on_screen_start.y), int(self.on_screen_end.y), (50, 50, 50))

    def kill(self) -> None:
        try:
            del __class__.instances[self.x]
        except KeyError:
            pass
        super().kill()

class BGPoint(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pair, color: _color) -> None:
        super().__init__(scene, Layers.BACKGROUND_POINTS)
        self.color = color
        self.pos = VEC(pos)

    def update(self) -> None:
        if self.pos.x - self.scene.player.camera.offset.x * BG_PARALLAX < -20:
            super().kill()

    def draw(self) -> None:
        draw_center = self.pos - self.scene.player.camera.offset * BG_PARALLAX
        pygame.draw.circle(self.manager.screen, self.color, draw_center, 4)
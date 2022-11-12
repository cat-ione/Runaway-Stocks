from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.gui.hud import PowerTimer
    from src.management.scene import Scene

from random import uniform, randint, choice
from numpy import cos, radians, sin
import pygame
import time

from src.management.sprite import VisibleSprite, Layers
from src.common.utils import inttup, pygame_draw_pie
from src.common.constants import VEC, _pos, _color

class Particle(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pos, color: _color):
        super().__init__(scene, Layers.EFFECTS)
        self.pos = VEC(pos)
        self.vel = VEC(uniform(-30, 30), uniform(-30, 30))
        while self.vel.x == 0 and self.vel.y == 0:
            self.vel = VEC(uniform(-160, 160), uniform(-160, 160))
        self.size = randint(1, 2)
        self.color = color

    def update(self) -> None:
        if self.vel.x <= 2 and self.vel.y < 2:
            self.kill()
            return
        self.vel -= self.vel.normalize() * 30 * self.manager.dt
        self.pos += self.vel * self.manager.dt

    def draw(self) -> None:
        pygame.draw.circle(self.manager.screen, self.color, inttup(self.pos - self.scene.player.camera.offset), self.size)

class Shockwave(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pos, color: _color, start_width: int, expansion_speed: float, thinnen_speed: float) -> None:
        super().__init__(scene, Layers.EFFECTS)
        self.pos = VEC(pos)
        self.color = color
        self.radius = 0
        self.width = start_width
        self.expansion_speed = expansion_speed
        self.thinnen_speed = thinnen_speed

    def update(self) -> None:
        self.radius += self.expansion_speed * self.manager.dt
        self.width -= self.thinnen_speed * self.manager.dt
        if self.width <= 0.6:
            self.kill()

    def draw(self) -> None:
        pygame.draw.circle(self.manager.screen, self.color, self.pos - self.scene.player.camera.offset, self.radius, round(self.width))

class PowerTimerPlayerDisplay(VisibleSprite):
    def __init__(self, scene: Scene, master: PowerTimer) -> None:
        super().__init__(scene, Layers.PLAYER_TIMER)
        self.master = master

    def update(self) -> None:
        # Nothing to do here lol
        pass

    def draw(self) -> None:
        center = self.scene.player.pos - self.scene.player.camera.offset
        angle = int(self.master.current_time / self.master.max_time * 360) + 180
        rad = 35
        pygame_draw_pie(self.manager.screen, (255, 255, 255, 70), center, rad, 180, angle)
        pygame.draw.line(self.manager.screen, (150, 150, 150), center, center + VEC(sin(radians(180)), -cos(radians(180))) * rad, 1)
        pygame.draw.line(self.manager.screen, (150, 150, 150), center, center + VEC(sin(radians(angle)), -cos(radians(angle))) * rad, 1)

class Glitch(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pos) -> None:
        super().__init__(scene, Layers.GLITCHES)
        self.orig_pos = VEC(pos)
        self.pos = self.orig_pos
        self.glitch_count = 0
        self.glitch_start = time.time()
        self.glitch_duration = uniform(0.02, 0.08)
        self.size = VEC(randint(30, 60), randint(6, 8))
        self.on_screen_pos = self.pos - self.scene.player.camera.offset
        try:
            self.surface = self.manager.screen.subsurface(self.on_screen_pos, self.size).copy()
        except ValueError:
            self.kill()

    def update(self) -> None:
        self.on_screen_pos = self.pos - self.scene.player.camera.offset
        if time.time() - self.glitch_start > self.glitch_duration:
            self.glitch_count += 1
            self.glitch_start = time.time()
            self.glitch_duration = uniform(0.02, 0.08)
            self.pos = self.orig_pos + VEC(choice([randint(-10, -5), randint(5, 10)]), randint(-2, 2))
        if self.glitch_count >= 8:
            self.kill()

    def draw(self) -> None:
        self.manager.screen.fill((30, 30, 30), (*self.on_screen_pos, *self.size))
        self.manager.screen.blit(self.surface, self.on_screen_pos)
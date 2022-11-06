from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager
    from scene import Scene

from numpy import cos, radians, sin
from random import uniform
from math import hypot
import pygame
import time

from pygame.locals import K_UP, K_DOWN, SRCALPHA, BLEND_RGB_SUB

from constants import VEC, WIDTH, HEIGHT, Dir, BOLD_FONTS, BULL_COLOR, BEAR_COLOR, SHADOW_OFFSET
from sprite import VisibleSprite, Layers
from utils import intvec, inttup
import barrier_powers as powers

class Camera:
    def __init__(self, manager: GameManager, master: object) -> None:
        self.manager = manager
        self.master = master
        self.actual_offset = self.master.pos - VEC(WIDTH, HEIGHT) / 2
        self.offset = intvec(self.actual_offset)
        self.shaking = False
        self.shake_start = time.time()
        self.shake_duration = 0
        self.per_shake_start = time.time()
        self.per_shake_duration = 0.05
        self.shake_intensity = 0

    def update(self) -> None:
        tick_offset = self.master.pos - self.offset - VEC(WIDTH, HEIGHT) / 2
        self.actual_offset += tick_offset * 5 * self.manager.dt
        if self.shaking and time.time() - self.shake_start < self.shake_duration:
            if time.time() - self.per_shake_start < self.per_shake_duration:
                self.actual_offset += VEC(uniform(-(si := self.shake_intensity), si), uniform(-si, si))
            else:
                self.per_shake_start = time.time()
        else:
            self.shaking = False
            self.shake_duration = 0
            self.shake_intensity = 0
            self.shake_start = time.time()
        self.offset = intvec(self.actual_offset)

    def shake(self, duration: float, intensity: int):
        self.shaking = True
        self.shake_duration = duration if duration > self.shake_duration else self.shake_duration
        self.shake_intensity = intensity if intensity > self.shake_intensity else self.shake_intensity

class Player(VisibleSprite):
    class Segment(VisibleSprite):
        def __init__(self, manager: GameManager, player: Player, scene: Scene = None) -> None:
            super().__init__(manager, Layers.PLAYER, scene)
            self.player = player
            self.player.segments.append(self)
            self.speed = player.speed
            self.direction = player.direction
            self.color = player.color
            self.angle = player.angle
            self.start_pos = player.pos.copy()
            self.end_pos = self.start_pos.copy()

        def update(self) -> None:
            if self.start_pos.x - self.player.camera.offset.x < 0:
                self.kill()

        def draw(self) -> None:
            width = 6
            start_pos = self.start_pos - self.player.camera.offset
            end_pos = self.end_pos - self.player.camera.offset
            start_1 = VEC(start_pos.x, start_pos.y - width // 2)
            start_2 = VEC(start_pos.x, start_pos.y + width // 2)
            end_1 = VEC(end_pos.x, end_pos.y - width // 2)
            end_2 = VEC(end_pos.x, end_pos.y + width // 2)

            pygame.draw.line(self.player.shadow.surface, (60, 60, 60), start_pos + SHADOW_OFFSET, end_pos + SHADOW_OFFSET, 8)

            pygame.draw.aaline(self.manager.screen, self.color, start_1, end_1)
            pygame.draw.aaline(self.manager.screen, self.color, start_2, end_2)
            pygame.gfxdraw.filled_polygon(self.manager.screen, tuple(map(lambda p: p + (0, 1), (start_1, start_2, end_2, end_1))), self.color)

        def kill(self) -> None:
            self.player.segments.remove(self)
            super().kill()

    class SegmentShadows(VisibleSprite):
        def __init__(self, manager: GameManager, scene: Scene = None) -> None:
            super().__init__(manager, Layers.PLAYER_SHADOW, scene)
            self.surface = pygame.Surface((WIDTH, HEIGHT))

        def update(self) -> None:
            # Nothing to do in here
            pass

        def draw(self) -> None:
            self.manager.screen.blit(self.surface, (0, 0), special_flags=BLEND_RGB_SUB)
            self.surface = pygame.Surface((WIDTH, HEIGHT))

    def __init__(self, manager: GameManager, scene: Scene = None) -> None:
        super().__init__(manager, Layers.PLAYER, scene)
        self.speed = 200
        self.pos = VEC(0, 0)
        self.camera = Camera(self.manager, self)
        self.direction = Dir.UP
        self.color = BULL_COLOR
        self.angle = 40
        self.segments = []
        self.Segment(self.manager, self, self.scene)
        self.shadow = self.SegmentShadows(self.manager, self.scene)
        self.tip_offsets_upright = [VEC(0, 15), VEC(-6, -5), VEC(6, -5)]
        self.tip_offset_func = lambda c: inttup(self.pos + VEC(c) - self.camera.offset)
        self.tip_rotation_func = lambda c: c.rotate((90 - self.angle) * -self.direction.value) * self.direction.value
        self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
        self.score = 0
        self.start_time = time.time()

    def update(self) -> None:
        keys = pygame.key.get_pressed()
        if not powers.Flip.init:
            up_key, down_key = K_UP, K_DOWN
        else:
            up_key, down_key = K_DOWN, K_UP
        if powers.Angle.init:
            self.angle = powers.Angle.angle
            self.update_segments(self.direction)
        else:
            self.angle = 40
            powers.Angle.reset(self.manager)
            self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
        if powers.Speed.init:
            self.speed = powers.Speed.speed
            self.camera.shake(0.1, 1)
        else:
            self.speed = 200

        if not (keys[up_key] and keys[down_key]):
            if keys[up_key] and self.direction != Dir.UP:
                self.start_time = time.time()
                self.update_segments(Dir.UP)
            elif keys[down_key] and self.direction != Dir.DOWN:
                self.start_time = time.time()
                self.update_segments(Dir.DOWN)

        if time.time() - self.start_time > 1:
            self.score += -self.direction.value
            self.start_time = time.time()

        self.pos.x += cos(radians(self.angle * self.direction.value)) * self.speed * self.manager.dt
        self.pos.y += sin(radians(self.angle * self.direction.value)) * self.speed * self.manager.dt

        for segment in self.segments:
            segment.update()
        self.segments[-1].start_pos = self.pos.copy()

        self.camera.update()

    def draw(self) -> None:
        for segment in self.segments:
            segment.draw()
        pygame.draw.polygon(self.manager.screen, self.color, list(map(self.tip_offset_func, self.tip_offsets)))
        pygame.draw.polygon(self.shadow.surface, (60, 60, 60), list(map(lambda c: self.tip_offset_func(c) + SHADOW_OFFSET, self.tip_offsets)))
        text_surf = BOLD_FONTS[18].render(str(self.score), True, (230, 230, 230))
        self.manager.screen.blit(text_surf, (self.pos - self.camera.offset - VEC(text_surf.get_size()) // 2 - VEC(0, 20)))

    def update_segments(self, direction: Dir):
        self.direction = direction
        self.color = BULL_COLOR if direction == Dir.UP else BEAR_COLOR
        self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
        self.Segment(self.manager, self, self.scene)
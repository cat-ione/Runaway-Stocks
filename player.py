from __future__ import annotations
from turtle import update
from typing import TYPE_CHECKING

if TYPE_CHECKING: from manager import GameManager

from numpy import cos, radians, sin
from random import uniform
import pygame
import time

from pygame.locals import K_UP, K_DOWN

from constants import VEC, WIDTH, HEIGHT, Dir, BOLD_FONTS
from utils import intvec, Sprite, inttup
import barrier_powers as powers

class Camera:
    def __init__(self, manager: GameManager, master: object) -> None:
        self.manager = manager
        self.master = master
        self.actual_offset = self.master.pos - VEC(WIDTH, HEIGHT) / 2
        self.offset = intvec(self.actual_offset)
        self.shaking = False
        self.shaking_timer = time.time()

    def update(self) -> None:
        tick_offset = self.master.pos - self.offset - VEC(WIDTH, HEIGHT) / 2
        if -1 < tick_offset.x < 1:
            tick_offset.x = 0
        if -1 < tick_offset.y < 1:
            tick_offset.y = 0
        self.actual_offset += tick_offset * 5 * self.manager.dt
        if self.shaking and time.time() - self.shaking_timer < 0.25:
            self.actual_offset += VEC(uniform(-2, 2), uniform(-2, 2))
        else:
            self.shaking = False
            self.shaking_timer = time.time()
        self.offset = intvec(self.actual_offset)

class Player(Sprite):
    class Segment(Sprite):
        def __init__(self, manager: GameManager, player: Player) -> None:
            super().__init__(manager)
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
                self.player.segments.remove(self)
                del self

        def draw(self) -> None:
            for y in range(-3, 4):
                pygame.draw.aaline(self.manager.screen, self.color, self.start_pos - self.player.camera.offset + (0, y), self.end_pos - self.player.camera.offset + (0, y))

    def __init__(self, manager: GameManager) -> None:
        super().__init__(manager)
        self.speed = 200
        self.pos = VEC(0, 0)
        self.camera = Camera(self.manager, self)
        self.direction = Dir.UP
        self.color = (232, 87, 87)
        self.angle = 40
        self.segments = []
        self.Segment(self.manager, self)
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
            self.update_segments(self.direction)
        if powers.Speed.init:
            self.speed = powers.Speed.speed
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
        text_surf = BOLD_FONTS[18].render(str(self.score), True, (230, 230, 230))
        self.manager.screen.blit(text_surf, (self.pos - self.camera.offset - VEC(text_surf.get_size()) // 2 - VEC(0, 20)))
        
    def update_segments(self, direction: Dir):
        self.direction = direction
        self.color = (232, 87, 87) if direction == Dir.UP else (12, 120, 38)
        self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
        self.Segment(self.manager, self)
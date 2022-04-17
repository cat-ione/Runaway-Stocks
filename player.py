from numpy import cos, radians, sin
import pygame
import time

from pygame.locals import K_UP, K_DOWN

from constants import VEC, WIDTH, HEIGHT, Dir, BOLD_FONTS
from utils import intvec, Sprite, inttup

class Camera:
    def __init__(self, manager, master):
        self.manager = manager
        self.master = master
        self.actual_offset = self.master.pos - VEC(WIDTH, HEIGHT) / 2
        self.offset = intvec(self.actual_offset)

    def update(self):
        tick_offset = self.master.pos - self.offset - VEC(WIDTH, HEIGHT) / 2
        if -1 < tick_offset.x < 1:
            tick_offset.x = 0
        if -1 < tick_offset.y < 1:
            tick_offset.y = 0
        self.actual_offset += tick_offset * 5 * self.manager.dt
        self.offset = intvec(self.actual_offset)

class Player(Sprite):
    class Segment(Sprite):
        def __init__(self, manager, player):
            super().__init__(manager)
            self.player = player
            self.player.segments.append(self)
            self.speed = player.speed
            self.direction = player.direction
            self.color = player.color
            self.angle = player.angle
            self.start_pos = player.pos.copy()
            self.end_pos = self.start_pos.copy()

        def update(self):
            if self.start_pos.x - self.player.camera.offset.x < 0:
                self.player.segments.remove(self)
                del self

        def draw(self):
            pygame.draw.line(self.manager.screen, self.color, self.start_pos - self.player.camera.offset, self.end_pos - self.player.camera.offset, 6)

    def __init__(self, manager):
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
        self.reverse = False
        self.reverse_timer = time.time()
        self.reverse_max_time = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if not self.reverse:
            up_key, down_key = K_UP, K_DOWN
            self.reverse_timer = time.time()
        else:
            up_key, down_key = K_DOWN, K_UP
            if time.time() - self.reverse_timer > self.reverse_max_time:
                self.reverse = False
        if not (keys[up_key] and keys[down_key]):
            if keys[up_key] and self.direction != Dir.UP:
                self.start_time = time.time()
                self.direction = Dir.UP
                self.color = (232, 87, 87)
                self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
                self.Segment(self.manager, self)
            elif keys[down_key] and self.direction != Dir.DOWN:
                self.start_time = time.time()
                self.direction = Dir.DOWN
                self.color = (12, 120, 38)
                self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
                self.Segment(self.manager, self)

        if time.time() - self.start_time > 1:
            self.score += -self.direction.value
            self.start_time = time.time()

        self.pos.x += cos(radians(self.angle * self.direction.value)) * self.speed * self.manager.dt
        self.pos.y += sin(radians(self.angle * self.direction.value)) * self.speed * self.manager.dt

        for segment in self.segments:
            segment.update()
        self.segments[-1].start_pos = self.pos.copy()

        self.camera.update()

    def draw(self):
        for segment in self.segments:
            segment.draw()
        pygame.draw.polygon(self.manager.screen, self.color, list(map(self.tip_offset_func, self.tip_offsets)))
        text_surf = BOLD_FONTS[18].render(str(self.score), True, (230, 230, 230))
        self.manager.screen.blit(text_surf, (self.pos - self.camera.offset - VEC(text_surf.get_size()) // 2 - VEC(0, 20)))
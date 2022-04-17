from random import uniform, randint
import pygame

from utils import Sprite, inttup
from constants import VEC

class Particle(Sprite):
    instances = []
    
    @classmethod
    def update_all(cls):
        for instance in cls.instances:
            instance.update()
            
    @classmethod
    def draw_all(cls):
        for instance in cls.instances:
            instance.draw()

    def __init__(self, manager, pos, color):
        super().__init__(manager)
        __class__.instances.append(self)
        self.pos = VEC(pos)
        self.vel = VEC(uniform(-30, 30), uniform(-30, 30))
        while self.vel.x == 0 and self.vel.y == 0:
            self.vel = VEC(uniform(-160, 160), uniform(-160, 160))
        self.size = randint(1, 2)
        self.color = color

    def update(self):
        if self.vel.x <= 2 and self.vel.y < 2:
            __class__.instances.remove(self)
            del self
            return
        self.vel -= self.vel.normalize() * 30 * self.manager.dt
        self.pos += self.vel * self.manager.dt

    def draw(self):
        pygame.draw.circle(self.manager.screen, self.color, inttup(self.pos - self.scene.player.camera.offset), self.size)

class Shockwave(Sprite):
    instances = []
    
    @classmethod
    def update_all(cls):
        for instance in cls.instances:
            instance.update()

    @classmethod
    def draw_all(cls):
        for instance in cls.instances:
            instance.draw()

    def __init__(self, manager, pos, color, start_width, expansion_speed, thinnen_speed):
        super().__init__(manager)
        __class__.instances.append(self)
        self.pos = VEC(pos)
        self.color = color
        self.radius = 0
        self.width = start_width
        self.expansion_speed = expansion_speed
        self.thinnen_speed = thinnen_speed

    def update(self):
        self.radius += self.expansion_speed * self.manager.dt
        self.width -= self.thinnen_speed * self.manager.dt
        if self.width <= 0.6:
            __class__.instances.remove(self)
            del self

    def draw(self):
        pygame.draw.circle(self.manager.screen, self.color, self.pos - self.scene.player.camera.offset, self.radius, round(self.width))
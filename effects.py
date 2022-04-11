from random import uniform, randint

from utils import *
from constants import *

class Particle(Sprite):
    instances = []

    @classmethod
    def tick(cls, dt, screen):
        for instance in cls.instances:
            instance.update(dt)
            instance.draw(screen)

    def __init__(self, player, pos, color):
        __class__.instances.append(self)
        self.player = player
        self.pos = VEC(pos)
        self.vel = VEC(uniform(-30, 30), uniform(-30, 30))
        while self.vel.x == 0 and self.vel.y == 0:
            self.vel = VEC(uniform(-160, 160), uniform(-160, 160))
        self.size = randint(1, 2)
        self.color = color

    def update(self, dt):
        if self.vel.x <= 2 and self.vel.y < 2:
            __class__.instances.remove(self)
            del self
            return
        self.vel -= self.vel.normalize() * 30 * dt
        self.pos += self.vel * dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, inttup(self.pos - self.player.camera.offset), self.size)

class Shockwave(Sprite):
    instances = []

    @classmethod
    def tick(cls, dt, screen):
        for instance in cls.instances:
            instance.update(dt)
            instance.draw(screen)

    def __init__(self, player, pos, color, start_width, expansion_speed, thinnen_speed):
        __class__.instances.append(self)
        self.player = player
        self.pos = VEC(pos)
        self.color = color
        self.radius = 0
        self.width = start_width
        self.expansion_speed = expansion_speed
        self.thinnen_speed = thinnen_speed

    def update(self, dt):
        self.radius += self.expansion_speed * dt
        self.width -= self.thinnen_speed * dt
        if self.width <= 0.6:
            __class__.instances.remove(self)
            del self

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos - self.player.camera.offset, self.radius, round(self.width))
from random import randint
import pygame

from effects import Particle, Shockwave
from utils import Sprite, inttup
from constants import FONTS, VEC

class Points(Sprite):
    instances = {}
    
    @classmethod
    def update_all(cls, dt):
        for instance in cls.instances.copy().values():
            instance.update(dt)

    @classmethod
    def draw_all(cls, screen):
        for instance in cls.instances.values():
            instance.draw(screen)

    def __init__(self, manager, val, pos):
        super().__init__(manager)
        __class__.instances[pos] = self
        self.val = val
        self.color = (232, 87, 87) if self.val > 0 else (12, 120, 38)
        self.pos = VEC(pos)

    def update(self, dt):
        if self.pos.distance_to(self.scene.player.pos) < 10:
            self.scene.player.score += self.val
            self.kill()
            return
        screen_pos = self.pos - self.scene.player.camera.offset
        if screen_pos.x < -50:
            self.delete()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos - self.scene.player.camera.offset, 4)
        screen.blit(FONTS[16].render(str(self.val), True, self.color), self.pos - self.scene.player.camera.offset + VEC(3, 1))

    def kill(self):
        for _ in range(randint(80, 100)):
            Particle(self.scene.player, self.pos, self.color)
        Shockwave(self.scene.player, self.pos, self.color, 5, 50, 6)
        self.delete()

    def delete(self):
        del __class__.instances[inttup(self.pos)]
        del self

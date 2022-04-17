from random import randint
import pygame

from effects import Particle, Shockwave
from utils import Sprite, inttup
from constants import FONTS, VEC

class Points(Sprite):
    instances = {}
    
    @classmethod
    def update_all(cls):
        for instance in cls.instances.copy().values():
            instance.update()

    @classmethod
    def draw_all(cls):
        for instance in cls.instances.values():
            instance.draw()

    def __init__(self, manager, val, pos):
        super().__init__(manager)
        __class__.instances[pos] = self
        self.val = val
        self.color = (232, 87, 87) if self.val > 0 else (12, 120, 38)
        self.pos = VEC(pos)

    def update(self):
        if self.pos.distance_to(self.scene.player.pos) < 10:
            self.scene.player.score += self.val
            self.kill()
            return
        screen_pos = self.pos - self.scene.player.camera.offset
        if screen_pos.x < -50:
            self.delete()

    def draw(self):
        pygame.draw.circle(self.manager.screen, self.color, self.pos - self.scene.player.camera.offset, 4)
        self.manager.screen.blit(FONTS[16].render(str(self.val), True, self.color), self.pos - self.scene.player.camera.offset + VEC(3, 1))

    def kill(self):
        for _ in range(randint(80, 100)):
            Particle(self.manager, self.pos, self.color)
        Shockwave(self.manager, self.pos, self.color, 5, 50, 6)
        self.delete()

    def delete(self):
        del __class__.instances[inttup(self.pos)]
        del self

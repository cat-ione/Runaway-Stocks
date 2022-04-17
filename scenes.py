from PIL.Image import open as open_image
from PIL.ImageFilter import BoxBlur
import pygame
import os

from pygame.locals import KEYDOWN, K_SPACE

from gridlines import VerticalGridline, HorizontalGridline, Barrier
from constants import HIGHSCORE_FILE, CENTER, BOLD_FONTS, Anchors
from elements import Image, Label, MainGameTimer
from effects import Particle, Shockwave
from player import Player
from points import Points

class Scene:
    def __init__(self, manager, previous_scene):
        self.manager = manager
        self.previous_scene = previous_scene
        self.elements = []

    def update(self):
        for element in self.elements:
            element.update(self.manager.dt)

    def draw(self):
        for element in self.elements:
            element.draw(self.manager.screen)

class MainGame(Scene):
    def __init__(self, manager, previous_scene):
        super().__init__(manager, previous_scene)
        
    def setup(self):
        MainGameTimer(self.manager)
        self.player = Player()
        Points.instances.clear()
        VerticalGridline.instances.clear()
        HorizontalGridline.instances.clear()
        Particle.instances.clear()
        Shockwave.instances.clear()

        self.running = True

    def update(self):
        dt = self.manager.dt

        HorizontalGridline.update_all(self.player, dt)
        VerticalGridline.update_all(self.player, dt)
        Barrier.update_all(dt)
        Points.update_all(dt)
        Particle.update_all(dt)
        Shockwave.update_all(dt)
        self.player.update(dt)

        super().update()

    def draw(self):
        screen = self.manager.screen
        screen.fill((30, 30, 30))

        HorizontalGridline.draw_all(screen)
        VerticalGridline.draw_all(screen)
        Barrier.draw_all(screen)
        Points.draw_all(screen)
        Particle.draw_all(screen)
        Shockwave.draw_all(screen)
        self.player.draw(screen)

        super().draw()

class EndMenu(Scene):
    def __init__(self, manager, previous_scene):
        super().__init__(manager, previous_scene)

    def setup(self):
        pygame.image.save(self.manager.screen, "scene_blur_tmp.png")
        self.bg_image = open_image(r"scene_blur_tmp.png").filter(BoxBlur(6))
        self.bg_image = pygame.image.fromstring(self.bg_image.tobytes(), self.bg_image.size, self.bg_image.mode).convert_alpha()
        self.bg_image = Image(self.manager, (0, 0), self.bg_image, anchor=Anchors.TOPLEFT)
        os.remove("scene_blur_tmp.png")

        try:
            with open(HIGHSCORE_FILE, "r") as f:
                self.highscore = int(f.read())
        except FileNotFoundError:
            open(HIGHSCORE_FILE, "x")
            self.highscore = 0
        except ValueError:
            self.highscore = 0
        if self.previous_scene.player.score > self.highscore:
            Label(self.manager, CENTER, "New Highscore!", BOLD_FONTS[64], (230, 230, 230))
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.previous_scene.player.score))
        else:
            Label(self.manager, CENTER, f"Highscore: {self.highscore}", BOLD_FONTS[64], (230, 230, 230))

        Label(self.manager, CENTER - (0, 100), f"Score: {self.previous_scene.player.score}", BOLD_FONTS[64], (230, 230, 230))
        Label(self.manager, CENTER + (0, 100), "Press space to restart", BOLD_FONTS[18], (230, 230, 230))

        self.running = True

    def update(self):
        super().update()

        for event in self.manager.events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.running = False
                    self.manager.new_scene("MainGame")
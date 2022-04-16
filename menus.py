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

class Menu:
    def __init__(self, manager, previous_menu):
        self.manager = manager
        self.previous_menu = previous_menu
        self.elements = []

    def update(self):
        for element in self.elements:
            element.update(self.manager.dt)

    def draw(self):
        for element in self.elements:
            element.draw(self.manager.screen)

class MainGame(Menu):
    def __init__(self, manager, previous_menu):
        super().__init__(manager, previous_menu)

        MainGameTimer(self)
        self.player = Player()
        Points.instances.clear()
        VerticalGridline.instances.clear()
        HorizontalGridline.instances.clear()

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

class EndMenu(Menu):
    def __init__(self, manager, previous_menu):
        super().__init__(manager, previous_menu)

        pygame.image.save(manager.screen, "menu_blur_tmp.png")
        self.bg_image = open_image(r"menu_blur_tmp.png").filter(BoxBlur(6))
        self.bg_image = pygame.image.fromstring(self.bg_image.tobytes(), self.bg_image.size, self.bg_image.mode).convert_alpha()
        self.bg_image = Image(self, (0, 0), self.bg_image, anchor=Anchors.TOPLEFT)
        os.remove("menu_blur_tmp.png")

        try:
            with open(HIGHSCORE_FILE, "r") as f:
                self.highscore = int(f.read())
        except FileNotFoundError:
            open(HIGHSCORE_FILE, "x")
            self.highscore = 0
        except ValueError:
            self.highscore = 0
        if previous_menu.player.score > self.highscore:
            Label(self, CENTER, "New Highscore!", BOLD_FONTS[64], (230, 230, 230))
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(previous_menu.player.score))
        else:
            Label(self, CENTER, f"Highscore: {self.highscore}", BOLD_FONTS[64], (230, 230, 230))

        Label(self, CENTER - (0, 100), f"Score: {previous_menu.player.score}", BOLD_FONTS[64], (230, 230, 230))
        Label(self, CENTER + (0, 100), "Press space to restart", BOLD_FONTS[18], (230, 230, 230))

        self.running = True

    def update(self):
        super().update()

        for event in self.manager.events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.running = False
                    self.manager.new_menu("MainGame")
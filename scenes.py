from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from manager import GameManager

from PIL.Image import open as open_image
from PIL.ImageFilter import GaussianBlur
import PIL
import pygame
import os

from pygame.locals import KEYDOWN, K_SPACE, K_ESCAPE

from constants import HEIGHT, HIGHSCORE_FILE, CENTER, BOLD_FONTS, TMP_BG_FILE, WIDTH, Anchors
from gridlines import VerticalGridline, HorizontalGridline, Barrier
from elements import Image, Label, MainGameTimer, Timer
from barrier_powers import barrier_powers
from effects import Particle, Shockwave
from player import Player
from points import Points

from images import title_1, title_2

def blur_surf(surf: pygame.Surface) -> pygame.Surface:
    """
    - Convert the surface to bytestring
    - Convert bytestring to parsable PIL image
    - Blur image with GaussianBlur
    - Convert PIL image to pygame surface
    - Return pygame surface
    """
    surf_str = pygame.image.tostring(surf, "RGB")
    surf_img = PIL.Image.frombytes("RGB", surf.get_size(), surf_str)
    blurred_img = surf_img.filter(GaussianBlur(3))
    blurred_img_surf = pygame.image.fromstring(blurred_img.tobytes(), blurred_img.size, blurred_img.mode).convert_alpha()
    return blurred_img_surf

def create_blurred_bg(manager: GameManager) -> Image:
    """
    - Blur screen as surface
    - Create a custom Image object that will be displayed
    - Also return the object for accessibility
    """

    blurred_img_surf = blur_surf(manager.screen)
    blurred_img_obj = Image(manager, (0, 0), blurred_img_surf, anchor=Anchors.TOPLEFT)
    return blurred_img_obj

class Scene:
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        self.manager = manager
        self.previous_scene = previous_scene
        self.elements = []

    def setup(self) -> None:
        self.running = True

    def update(self) -> None:
        for element in self.elements:
            element.update()

    def draw(self) -> None:
        for element in self.elements:
            element.draw()

class MainMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)

    def setup(self) -> None:
        Image(self.manager, (WIDTH // 2, HEIGHT // 2 - 100), title_1)
        Image(self.manager, (WIDTH // 2, HEIGHT // 2 - 100), title_2)
        self.player = Player(self.manager)
        Points.instances.clear()
        VerticalGridline.instances.clear()
        HorizontalGridline.instances.clear()
        Barrier.instance = None
        Barrier.last_position = 0
        Particle.instances.clear()
        Shockwave.instances.clear()
        for power in barrier_powers:
            power.init = False

        super().setup()

    def update(self) -> None:
        HorizontalGridline.update_all(self.manager)
        VerticalGridline.update_all(self.manager)
        Barrier.update_all()
        Points.update_all()
        Particle.update_all()
        Shockwave.update_all()
        self.player.update()

        super().update()

        for event in self.manager.events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.manager.new_scene("MainGame")
                    break

    def draw(self) -> None:
        self.manager.screen.fill((30, 30, 30))

        HorizontalGridline.draw_all()
        VerticalGridline.draw_all()
        Barrier.draw_all()
        Points.draw_all()
        Particle.draw_all()
        Shockwave.draw_all()
        self.player.draw()

        self.manager.screen.blit(blur_surf(self.manager.screen), (0, 0))

        super().draw()

class MainGame(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)

    def setup(self) -> None:
        MainGameTimer(self.manager)

        self.player = Player(self.manager)
        Points.instances.clear()
        VerticalGridline.instances.clear()
        HorizontalGridline.instances.clear()
        Barrier.instance = None
        Barrier.last_position = 0
        Particle.instances.clear()
        Shockwave.instances.clear()
        for power in barrier_powers:
            power.init = False

        super().setup()

    def update(self) -> None:
        HorizontalGridline.update_all(self.manager)
        VerticalGridline.update_all(self.manager)
        Barrier.update_all()
        Points.update_all()
        Particle.update_all()
        Shockwave.update_all()
        self.player.update()

        super().update()

        for event in self.manager.events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.manager.new_scene("PauseMenu")
                    break

    def draw(self) -> None:
        self.manager.screen.fill((30, 30, 30))

        HorizontalGridline.draw_all()
        VerticalGridline.draw_all()
        Barrier.draw_all()
        Points.draw_all()
        Particle.draw_all()
        Shockwave.draw_all()
        self.player.draw()

        super().draw()

class PauseMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)

    def setup(self) -> None:
        Timer.pause_all()

        create_blurred_bg(self.manager)
        Label(self.manager, (WIDTH // 2, HEIGHT // 2), "Game Paused", BOLD_FONTS[80], (230, 230, 230))

        super().setup()

    def update(self) -> None:
        super().update()

        for event in self.manager.events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.manager.switch_scene(self.previous_scene)
                    break

class EndMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)

    def setup(self) -> None:
        create_blurred_bg(self.manager)

        try: # Try to open the highscore file and read the highscore
            with open(HIGHSCORE_FILE, "r") as f:
                self.highscore = int(f.read())
        except FileNotFoundError: # If the file isn't found, create the file
            f = open(HIGHSCORE_FILE, "x")
            f.close()
            self.highscore = 0
        except ValueError: # If file contains invalid format, set it to 0
            self.highscore = 0

        # If it is a new highscore, display "New Highscore!"
        if self.previous_scene.player.score > self.highscore:
            Label(self.manager, CENTER, "New Highscore!", BOLD_FONTS[64], (230, 230, 230))
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.previous_scene.player.score)) # Update the highscore in the file
        else: # If it is not a new highscore, display the current highscore
            Label(self.manager, CENTER, f"Highscore: {self.highscore}", BOLD_FONTS[64], (230, 230, 230))

        # Create labels to display the score and a prompt
        Label(self.manager, CENTER - (0, 100), f"Score: {self.previous_scene.player.score}", BOLD_FONTS[64], (230, 230, 230))
        Label(self.manager, CENTER + (0, 100), "Press space to restart", BOLD_FONTS[18], (230, 230, 230))

        super().setup()

    def update(self) -> None:
        super().update()

        for event in self.manager.events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    # Start new game
                    self.manager.new_scene("MainGame")
                    break
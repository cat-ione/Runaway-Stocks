from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from manager import GameManager

from PIL.Image import open as open_image
from PIL.ImageFilter import GaussianBlur
import PIL
import pygame
import os

from pygame.locals import KEYDOWN, K_SPACE, K_ESCAPE

from constants import GRID_SPACE, HEIGHT, HIGHSCORE_FILE, CENTER, BOLD_FONTS, TMP_BG_FILE, WIDTH, Anchors
from gridlines import VerticalGridline, HorizontalGridline, Barrier
from elements import Image, Label, MainGameTimer, Timer
from barrier_powers import barrier_powers
from effects import Particle, Shockwave
from player import Player
from points import Points

from images import title_1, title_2

def create_blurred_bg(manager):
    """
    - Saves the screen img as a tmp file
    - blur it
    - load it as string format
    - convert to a surface
    - remove the tmp file
    - return the surface
    """

    bg_str = pygame.image.tostring(manager.screen, "RGB")
    bg_img = PIL.Image.frombytes("RGB", (WIDTH, HEIGHT), bg_str)
    blurred_bg_img = bg_img.filter(GaussianBlur(4))
    blurred_bg_img = pygame.image.fromstring(blurred_bg_img.tobytes(), blurred_bg_img.size, blurred_bg_img.mode).convert_alpha()
    blurred_bg_img = Image(manager, (0, 0), blurred_bg_img, anchor=Anchors.TOPLEFT)
    # os.remove(TMP_BG_FILE)
    return blurred_bg_img

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
        # Label(self.manager, (WIDTH // 2, HEIGHT // 2 + 100), "Press space to start the game!", BOLD_FONTS[18], (230, 230, 230))
        Image(self.manager, (WIDTH // 2, HEIGHT // 2 - 100), title_1)
        Image(self.manager, (WIDTH // 2, HEIGHT // 2 - 100), title_2)
        self.player = Player(self.manager)

        super().setup()

    def update(self) -> None:
        self.player.update()

        super().update()

        for event in self.manager.events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.manager.new_scene("MainGame")
                    break

    def draw(self) -> None:
        self.manager.screen.fill((30, 30, 30))

        for x in range(0, WIDTH, int(GRID_SPACE.x)):
            pygame.draw.line(self.manager.screen, (150, 150, 150), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, int(GRID_SPACE.y)):
            pygame.draw.line(self.manager.screen, (150, 150, 150), (0, y), (WIDTH, y))

        self.player.draw()

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
from pygame.locals import KEYDOWN, K_SPACE
import pygame

from src.game.gridlines import GridManager, Barrier
from src.common.constants import BOLD_FONTS, WIDTH
from src.game.background import BGGridManager
from src.gui.elements import Label, Button
from src.management.scene import Scene
from src.common.utils import blur_surf
from src.game.player import Player

class MainMenuBG(Scene):
    def setup(self) -> None:
        super().setup()

        self.grid_manager = GridManager(self)
        self.bg_grid_manager = BGGridManager(self)
        self.player = Player(self)
        Barrier.reset()

    def update(self) -> None:
        super().update()

        self.grid_manager.update()
        self.bg_grid_manager.update()

    def pre_sprite(self) -> None:
        self.surface.fill((30, 30, 30))

    def post_sprite(self) -> None:
        self.surface.blit(blur_surf(self.surface), (0, 0))

class MainMenuGUI(Scene):
    def setup(self) -> None:
        super().setup()
        self.surface.set_colorkey((0, 0, 0))

        self.ending = False

        Label(self, (WIDTH // 2, 140), "Runaway Stocks", BOLD_FONTS[90], (230, 230, 230)),
        Button(self, (WIDTH // 2, 360), "Start Game", BOLD_FONTS[20], (230, 230, 230), self.end)

    def pre_sprite(self) -> None:
        self.surface.fill((0, 0, 0))

    def end(self) -> None:
        self.ending = True
        self.manager.new_scene("MainGame")

class MainMenu(Scene):
    def setup(self) -> None:
        super().setup()

        self.background = MainMenuBG(self.manager, self.previous_scene, self)
        self.background.setup()
        self.gui = MainMenuGUI(self.manager, self.previous_scene, self)
        self.gui.setup()

        self.ending = False

    def update(self) -> None:
        super().update()

        self.background.update()
        self.gui.update()

    def pre_sprite(self) -> None:
        self.background.draw()
        self.gui.draw()
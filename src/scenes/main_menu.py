from pygame.locals import KEYDOWN, K_SPACE
import pygame

from src.gui.elements import Label, Button, Element
from src.game.gridlines import GridManager, Barrier
from src.common.constants import BOLD_FONTS, WIDTH
from src.game.background import BGGridManager
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

    def draw(self) -> None:
        self.manager.screen.fill((30, 30, 30))

        super().draw()
        self.manager.screen.blit(blur_surf(self.manager.screen), (0, 0))

class MainMenu(Scene):
    def setup(self) -> None:
        super().setup()

        self.background = MainMenuBG(self.manager, self.previous_scene)
        self.background.setup()

        self.ending = False

        Label(self, (WIDTH // 2, 140), "Runaway Stocks", BOLD_FONTS[90], (230, 230, 230)),
        Button(self, (WIDTH // 2, 360), "Start Game", BOLD_FONTS[20], (230, 230, 230), self.end)

    def update(self) -> None:
        super().update()

        self.background.update()

        if self.ending:
            pass

    def draw(self) -> None:
        self.background.draw()

        super().draw()

    def end(self) -> None:
        self.ending = True
        self.manager.new_scene("MainGame")
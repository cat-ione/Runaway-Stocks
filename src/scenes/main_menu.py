from pygame.locals import KEYDOWN, K_SPACE
import pygame

from src.common.constants import HEIGHT, BOLD_FONTS, WIDTH
from src.game.gridlines import GridManager, Barrier
from src.game.background import BGGridManager
from src.management.scene import Scene
from src.common.utils import blur_surf
from src.game.player import Player
from src.gui.elements import Label

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

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_SPACE:
            self.manager.new_scene("MainGame")

    def draw(self) -> None:
        self.manager.screen.fill((30, 30, 30))

        super().draw()
        self.manager.screen.blit(blur_surf(self.manager.screen), (0, 0))

class MainMenu(Scene):
    def setup(self) -> None:
        super().setup()
        self.background = MainMenuBG(self.manager, self.previous_scene)
        self.background.setup()

        Label(self, (WIDTH // 2, HEIGHT // 2), "Runaway Stocks", BOLD_FONTS[90], (230, 230, 230))

    def update(self) -> None:
        super().update()

        self.background.update()

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_SPACE:
            self.manager.new_scene("MainGame")

    def draw(self) -> None:
        self.background.draw()

        super().draw()
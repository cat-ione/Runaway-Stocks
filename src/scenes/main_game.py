from pygame.locals import KEYDOWN, K_ESCAPE
import pygame

from src.game.gridlines import GridManager, Barrier
from src.game.background import BGGridManager
from src.management.scene import Scene
from src.game.player import Player
from src.gui.hud import MainGameTimer

class MainGame(Scene):
    def setup(self) -> None:
        super().setup()

        pygame.mixer.music.load("res/audio/music.wav")
        pygame.mixer.music.set_volume(0.08)
        pygame.mixer.music.play(-1)

        self.grid_manager = GridManager(self)
        self.bg_grid_manager = BGGridManager(self)

        MainGameTimer(self)

        self.player = Player(self)
        Barrier.reset()

    def update(self) -> None:
        super().update()

        self.grid_manager.update()
        self.bg_grid_manager.update()

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_ESCAPE:
            self.manager.new_scene("PauseMenu")

    def draw(self) -> None:
        self.manager.screen.fill((30, 30, 30))

        super().draw()
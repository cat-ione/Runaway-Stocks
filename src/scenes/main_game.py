from pygame.locals import KEYDOWN, K_ESCAPE
import pytweening as tween
import pygame

from src.game.gridlines import GridManager, Barrier
from src.common.constants import MUSIC_VOLUME
from src.game.background import BGGridManager
from src.common.utils import blur_surf
from src.management.scene import Scene
from src.gui.hud import MainGameTimer
from src.common.tween import Tween
from src.game.player import Player
from src.common.exe import pathof

class MainGame(Scene):
    def setup(self) -> None:
        super().setup()

        pygame.mixer.music.load(pathof("res/audio/music.wav"))
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)

        self.grid_manager = GridManager(self)
        self.bg_grid_manager = BGGridManager(self)

        MainGameTimer(self)

        self.player = Player(self)
        Barrier.reset()

        self.slowdown = 0
        self.blur_tween = Tween(self.manager, 0.03, 1, 0.5, tween.easeOutSine)
        self.blur_tween.reset()

    def update(self) -> None:
        self.slowdown += 0.6 * self.manager.dt
        if self.slowdown > 1:
            self.slowdown = 1
        self.manager.dt *= self.slowdown

        super().update()

        self.grid_manager.update()
        self.bg_grid_manager.update()

        if self.blur_tween.value < 0.3:
            self.blur_tween()
        else:
            self.blur_tween.value = 1

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_ESCAPE:
            self.manager.new_scene("PauseMenu")

    def pre_sprite(self) -> None:
        self.surface.fill((30, 30, 30))

    def post_sprite(self) -> None:
        self.surface.blit(blur_surf(self.surface, self.blur_tween.value), (0, 0))
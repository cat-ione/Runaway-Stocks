from pygame.locals import KEYDOWN, K_ESCAPE
import pytweening as tween
import pygame

from src.common.constants import MUSIC_VOLUME, MIN_BLUR_THRESHOLD, HEIGHT, BOLD_FONTS, Anchors
from src.game.gridlines import GridManager, Barrier
from src.game.background import BGGridManager
from src.gui.elements import RectButton
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
        RectButton(self, (10, HEIGHT - 10), "Pause", BOLD_FONTS[24], (230, 230, 230), lambda: self.manager.new_scene("PauseMenu"), K_ESCAPE, Anchors.BOTTOMLEFT)

        self.player = Player(self)
        Barrier.reset()

        self.slowdown_tween = Tween(self, 0, 1, 0.5, tween.easeInQuad)
        # Cursed solution to make it use the manager dt instead of the scene dt
        self.blur_tween = Tween(self.manager, 0.03, 1, 0.1, tween.easeOutQuart, cutoff=MIN_BLUR_THRESHOLD - 0.1)

    def update(self) -> None:
        super().update()

        self.slowdown_tween()
        self.blur_tween()

        self.dt *= self.slowdown_tween.value

        self.grid_manager.update()
        self.bg_grid_manager.update()

    def pre_sprite(self) -> None:
        self.surface.fill((30, 30, 30))

    def post_sprite(self) -> None:
        self.surface.blit(blur_surf(self.surface, self.blur_tween.value), (0, 0))
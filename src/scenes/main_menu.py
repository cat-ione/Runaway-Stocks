from pygame.locals import K_SPACE
import pytweening as tween
import pygame

from src.game.gridlines import GridManager, Barrier
from src.common.constants import BOLD_FONTS, WIDTH
from src.game.background import BGGridManager
from src.management.scene import MenuScene
from src.gui.elements import Label, Button
from src.common.utils import blur_surf
from src.common.tween import Tween
from src.game.player import Player

class MainMenu(MenuScene):
    class BG(MenuScene.BG):
        def setup(self) -> None:
            start_tween = Tween(self, 0.03, 0.25, 0.2, tween.easeInExpo)
            end_tween = Tween(self, 0.03, 0.25, -0.2, tween.easeInExpo, cutoff=0.031)
            super().setup(start_tween, end_tween)

            self.grid_manager = GridManager(self)
            self.bg_grid_manager = BGGridManager(self)
            self.player = Player(self)
            Barrier.reset()

            self.slowdown_tween = Tween(self, 0, 1, 0.5, tween.easeOutCirc)
            self.slowdown_tween.reset()

        def update(self) -> None:
            super().update()

            self.slowdown_tween()
            self.dt *= self.slowdown_tween.value

            self.grid_manager.update()
            self.bg_grid_manager.update()

        def pre_sprite(self) -> None:
            self.surface.fill((30, 30, 30))

        def post_sprite(self) -> None:
            self.surface.blit(blur_surf(self.surface, self.tween.value), (0, 0))

    class GUI(MenuScene.GUI):
        def setup(self) -> None:
            start_tween = Tween(self, 0, 255, 300, tween.easeInSine)
            end_tween = Tween(self, 0, 255, -300, tween.easeInSine)
            super().setup(start_tween, end_tween)

            Label(self, (WIDTH // 2, 140), "Runaway Stocks", BOLD_FONTS[90], (230, 230, 230)),
            Button(self, (WIDTH // 2, 360), "Start Game", BOLD_FONTS[20], (230, 230, 230), self.super_scene.end, K_SPACE)

        def update(self) -> None:
            super().update()
            if self.tween.ended: return
            self.surface.set_alpha(self.tween.value)

    def setup(self) -> None:
        super().setup()
        self.next_scene = "MainGame"
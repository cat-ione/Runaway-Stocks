from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.manager import GameManager

import pygame

from src.common.constants import WIDTH, HEIGHT, VEC, Anchors
from src.management.sprite import SpriteManager
from src.management.scene import Scene
from src.common.utils import anchored
from src.common.tween import Tween

class MenuScene(Scene):
    class BG(Scene):
        def setup(self, start_tween: Tween, end_tween: Tween) -> None:
            super().setup()
            self.surface = self.surface.convert_alpha()

            self.start_tween = start_tween
            self.start_tween.reset()
            self.end_tween = end_tween
            self.end_tween.reset()
            self.tween = self.start_tween

        def update(self) -> None:
            super().update()

            self.tween()

        def end(self) -> None:
            self.tween = self.end_tween

    class GUI(Scene):
        def setup(self, start_tween: Tween, end_tween: Tween) -> None:
            super().setup()
            self.surface = self.surface.convert_alpha()

            self.start_tween = start_tween
            self.start_tween.reset()
            self.end_tween = end_tween
            self.end_tween.reset()
            self.tween = self.start_tween

        def update(self) -> None:
            super().update()

            self.tween()

        def pre_sprite(self) -> None:
            self.surface.fill((0, 0, 0, 0))

        def end(self) -> None:
            self.tween = self.end_tween

    def setup(self) -> None:
        super().setup()

        self.bg = self.BG(self.manager, self.previous_scene, self)
        self.bg.setup()
        self.gui = self.GUI(self.manager, self.previous_scene, self)
        self.gui.setup()

        self.ending = False

    def update(self) -> None:
        super().update()

        self.bg.update()
        self.gui.update()

        if self.ending and self.gui.tween.ended and self.bg.tween.ended:
            self.kill()

    def pre_sprite(self) -> None:
        self.surface.fill((0, 0, 0, 0))

    def post_sprite(self) -> None:
        self.bg.draw()
        self.gui.draw()

    # When the scene wants to end, maybe play an ending animation
    def end(self) -> None:
        self.ending = True
        self.bg.end()
        self.gui.end()

    # This method gets when the scene actually ends
    def kill(self) -> None:
        if self.next_scene == -1:
            self.manager.switch_scene(self.previous_scene)
        else:
            self.manager.new_scene(self.next_scene)
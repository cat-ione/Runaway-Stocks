from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.manager import GameManager

import pygame

from src.common.constants import WIDTH, HEIGHT, VEC, Anchors
from src.management.sprite import SpriteManager
from src.common.utils import anchored
from src.common.tween import Tween

class Scene:
    def __init__(self, manager: GameManager, previous_scene: Scene, super_scene: Scene = None) -> None:
        self.manager = manager
        self.super_scene = super_scene
        self.super_surface = super_scene.surface if super_scene else manager.screen
        self.previous_scene = previous_scene

    def setup(self, size: tuple[int, int] = (WIDTH, HEIGHT), pos: tuple[int, int] = (WIDTH // 2, HEIGHT // 2), anchor: Anchors = Anchors.CENTER) -> None:
        self.size = VEC(size)
        self.anchor = anchor
        self.anchor_pos = VEC(pos)
        self.pos = anchored(self.anchor_pos, self.size, self.anchor)
        self.surface = pygame.Surface(self.size)
        self.sprite_manager = SpriteManager(self)
        self.running = True
        self.dt = self.manager.dt

    def update(self) -> None:
        self.size = VEC(self.surface.get_size())
        self.pos = anchored(self.anchor_pos, self.size, self.anchor)

        self.sprite_manager.update()

        self.dt = self.manager.dt

    def draw(self) -> None:
        self.pre_sprite()
        self.sprite_manager.draw()
        self.post_sprite()

        self.super_surface.blit(self.surface, self.pos)

    def pre_sprite(self) -> None: ...

    def post_sprite(self) -> None: ...

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
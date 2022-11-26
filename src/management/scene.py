from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.manager import GameManager

import pygame

from src.common.constants import WIDTH, HEIGHT, VEC, Anchors
from src.management.sprite import SpriteManager
from src.common.utils import anchored

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

    def update(self) -> None:
        self.size = VEC(self.surface.get_size())
        self.pos = anchored(self.anchor_pos, self.size, self.anchor)

        self.sprite_manager.update()

    def draw(self) -> None:
        self.pre_sprite()
        self.sprite_manager.draw()
        self.post_sprite()

        self.super_surface.blit(self.surface, self.pos)

    def pre_sprite(self) -> None: ...

    def post_sprite(self) -> None: ...
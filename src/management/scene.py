from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.manager import GameManager

import pygame

from src.management.sprite import SpriteManager
from src.common.constants import WIDTH, HEIGHT

class Scene:
    def __init__(self, manager: GameManager, previous_scene: Scene, super_scene: Scene = None) -> None:
        self.manager = manager
        self.super_scene = super_scene
        self.super_surface = super_scene.surface if super_scene else manager.screen
        self.previous_scene = previous_scene

    def setup(self) -> None:
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.sprite_manager = SpriteManager(self)
        self.running = True

    def update(self) -> None:
        self.sprite_manager.update()

    def draw(self) -> None:
        self.pre_sprite()

        self.sprite_manager.draw()

        self.post_sprite()

        self.super_surface.blit(self.surface, (0, 0))

    def pre_sprite(self) -> None: ...

    def post_sprite(self) -> None: ...

    def post_process(self) -> None: ...
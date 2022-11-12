from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

import pygame

from src.common.constants import VEC, Anchors, _pos, _color
from src.management.sprite import VisibleSprite, Layers

class Label(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pos, text: str, font: pygame.font.Font, color: _color, anchor: Anchors = Anchors.CENTER) -> None:
        super().__init__(scene, Layers.HUD)
        self.surface = font.render(text, True, color)
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self) -> None:
        # ...
        pass

    def draw(self) -> None:
        self.manager.screen.blit(self.surface, self.pos)

class Image(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pos, surface: pygame.Surface, anchor: Anchors = Anchors.CENTER) -> None:
        super().__init__(scene, Layers.HUD)
        self.surface = surface
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self) -> None:
        # ...
        pass

    def draw(self) -> None:
        self.manager.screen.blit(self.surface, self.pos)
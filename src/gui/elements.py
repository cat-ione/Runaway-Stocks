from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

from pygame.locals import SRCALPHA
from typing import Callable
import pygame.gfxdraw
import pygame

from src.common.constants import VEC, Anchors, _pair, _color, _font, BEAR_COLOR, BULL_COLOR
from src.management.sprite import VisibleSprite, Layers
from src.common.utils import aaline

class Element(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pair, anchor: Anchors = Anchors.CENTER) -> None:
        super().__init__(scene, Layers.HUD)
        self.pos = VEC(pos)
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.manager.screen.blit(self.surface, self.pos)

class Label(Element):
    def __init__(self, scene: Scene, pos: _pair, text: str, font: _font, color: _color, anchor: Anchors = Anchors.CENTER) -> None:
        self.surface = font.render(text, True, color)
        super().__init__(scene, pos, anchor)

class Image(Element):
    def __init__(self, scene: Scene, pos: _pair, surface: pygame.Surface, anchor: Anchors = Anchors.CENTER) -> None:
        self.surface = surface
        super().__init__(scene, pos, anchor)

class Button(Element):
    def __init__(self, scene: Scene, pos: _pair, text: str, font: _font, color: _color, command: Callable, anchor: Anchors = Anchors.CENTER) -> None:
        self.command = command

        text_surf = font.render(text, True, color)
        text_size = VEC(text_surf.get_size())
        size = text_size * 2.5
        self.surface = pygame.Surface(size, SRCALPHA)

        p1, p2, p3, p4 = VEC(size.x // 2, 0 + 2), VEC(size.x + 1, size.y // 2), VEC(size.x // 2, size.y - 1), VEC(0 - 2, size.y // 2)
        pygame.gfxdraw.filled_polygon(self.surface, [p1, p2, p3, p4], (10, 10, 10))
        aaline(self.surface, BEAR_COLOR, p1, p2, 6)
        aaline(self.surface, BULL_COLOR, p2, p3, 6)
        aaline(self.surface, BEAR_COLOR, p3, p4, 6)
        aaline(self.surface, BULL_COLOR, p4, p1, 6)
        self.surface.blit(text_surf, (size - text_size) // 2 - (0, 2))

        self.mask = pygame.mask.from_surface(self.surface)
        super().__init__(scene, pos, anchor)

    def update(self) -> None:
        try:
            if self.mask.get_at(pygame.mouse.get_pos() - self.pos) and pygame.mouse.get_pressed()[0]:
                self.command()
        except IndexError:
            pass
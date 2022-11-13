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
from src.common.utils import aaline, inttup

class Element(VisibleSprite):
    def __init__(self, scene: Scene, pos: _pair, anchor: Anchors = Anchors.CENTER) -> None:
        super().__init__(scene, Layers.HUD)
        self.orig_pos = VEC(pos)
        self.orig_pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2
        self.pos = self.orig_pos.copy()

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
        self.font = font
        self.text = text
        self.color = color

        self.default_factor, self.hover_factor = 2.5, 2.8
        self.factor = self.default_factor
        self.surface, self.mask = self.default_surf, self.default_mask = self.generate_image(self.factor)
        self.hover_surf, self.hover_mask = self.generate_image(self.hover_factor)

        super().__init__(scene, pos, anchor)

    def update(self) -> None:
        try:
            if self.mask.get_at(inttup(pygame.mouse.get_pos() - self.pos)): # If the position of the cursor is part of the mask
                self.hover()
                if pygame.mouse.get_pressed()[0]:
                    self.command()
            else:
                self.default()
        except IndexError: # An index error means "get_at" failed, the cursor is outside the rect of the mask
            self.default()

    def default(self) -> None:
        self.factor -= 5 * self.manager.dt
        if self.factor < self.default_factor:
            self.factor = self.default_factor
            self.surface, self.mask = self.default_surf, self.default_mask
        else:
            self.surface, self.mask = self.generate_image(self.factor)
        self.pos = self.orig_pos - (VEC(self.surface.get_size()) - VEC(self.default_surf.get_size())) // 2

    def hover(self) -> None:
        self.factor += 5 * self.manager.dt
        if self.factor > self.hover_factor:
            self.factor = self.hover_factor
            self.surface, self.mask = self.hover_surf, self.hover_mask
        else:
            self.surface, self.mask = self.generate_image(self.factor)
        self.pos = self.orig_pos - (VEC(self.surface.get_size()) - VEC(self.default_surf.get_size())) // 2

    def generate_image(self, factor: float) -> tuple[pygame.Surface, pygame.Mask]:
        self.text_surf = self.font.render(self.text, True, self.color)
        text_size = VEC(self.text_surf.get_size())
        size = text_size * factor

        surf = pygame.Surface(size, SRCALPHA)

        # Create the top, right, bottom and left points (respectively) of the rhombus shaped button
        # +/- 2 for p1 and p3 (top and bottom) are to move the points inwards to avoid cutoff
        # +/- 2 for p2 and p4 (left and right) are to move the points outwards to cut off extra pixels
        p1, p2, p3, p4 = (size.x // 2, 0 + 2), (size.x + 2, size.y // 2), (size.x // 2, size.y - 2), (0 - 2, size.y // 2)
        pygame.gfxdraw.filled_polygon(surf, [p1, p2, p3, p4], (10, 10, 10))
        aaline(surf, BEAR_COLOR, p1, p2, 6)
        aaline(surf, BULL_COLOR, p2, p3, 6)
        aaline(surf, BEAR_COLOR, p3, p4, 6)
        aaline(surf, BULL_COLOR, p4, p1, 6)
        surf.blit(self.text_surf, (size - text_size) // 2 - (0, 2))

        return surf, pygame.mask.from_surface(surf)
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

from pygame.locals import SRCALPHA
from typing import Callable
import pytweening as tween
import pygame.gfxdraw
import pygame

from src.common.constants import VEC, Anchors, _pair, _color, _font, BEAR_COLOR, BULL_COLOR
from src.management.sprite import VisibleSprite, Layers
from src.common.utils import aaline, inttup
from src.common.audio import button_hover
from src.common.tween import Tween

class Element(VisibleSprite):
    """All subclasses of Element must implement surface"""
    def __init__(self, scene: Scene, pos: _pair, anchor: Anchors = Anchors.CENTER) -> None:
        super().__init__(scene, Layers.HUD)
        self.anchor = anchor
        self.center_pos = VEC(pos)
        self.pos = self.center_pos - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self) -> None:
        self.pos = self.center_pos - VEC((self.anchor.value.x + 1) * self.surface.get_width(), (self.anchor.value.y + 1) * self.surface.get_height()) // 2

    def draw(self) -> None:
        self.scene.surface.blit(self.surface, self.pos)

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
        self.factor = self.line_factor = self.default_factor
        self.surface, self.mask = self.default_surf, self.default_mask = self.generate_image(self.factor, False)
        self.hover_surf, self.hover_mask = self.generate_image(self.hover_factor, True)

        self.first_hover = True
        self.locked = False

        self.tween_expand = Tween(scene.manager, self.default_factor, self.hover_factor, 0.7, tween.easeInOutBack, s=12)
        self.tween_shrink = Tween(scene.manager, self.default_factor, self.hover_factor, -0.3, tween.easeInOutExpo)
        self.tween_line_expand = Tween(scene.manager, self.default_factor, self.hover_factor, 0.9, tween.easeInOutQuint)
        self.tween_line_shrink = Tween(scene.manager, self.default_factor, self.hover_factor, -0.3, tween.easeInOutExpo)

        super().__init__(scene, pos, anchor)

    def update(self) -> None:
        if not self.locked:
            try:
                # "- (self.center_pos - VEC(self.mask.get_size()) // 2)" to offset the detection to the proper place of the mask
                # simply subtracting self.pos will not work properly as self.pos is dynamic to the easing, while the mask is not
                if self.mask.get_at(inttup(pygame.mouse.get_pos() - (self.center_pos - VEC(self.mask.get_size()) // 2))): # If the position of the cursor is part of the mask
                    self.hover()
                    if pygame.mouse.get_pressed()[0]:
                        self.command()
                else:
                    self.default()
            except IndexError: # An index error means "get_at" failed, the cursor is outside the rect of the mask
                self.default()

        super().update()

    def default(self) -> None:
        self.tween_line_expand.reset()
        self.tween_expand.reset()
        self.tween_shrink()
        self.tween_line_shrink()

        self.factor = self.tween_shrink.value
        self.line_factor = self.tween_line_shrink.value
        if self.factor == self.default_factor:
            self.surface = self.default_surf
        else:
            self.surface, _ = self.generate_image(self.factor, False)
        self.mask = self.default_mask

        self.first_hover = True

    def hover(self) -> None:
        if self.first_hover:
            button_hover.play()
            self.first_hover = False

        self.tween_shrink.reset()
        self.tween_line_shrink.reset()
        self.tween_expand()
        self.tween_line_expand()

        self.factor = self.tween_expand.value
        self.line_factor = self.tween_line_expand.value
        if self.tween_expand == self.hover_factor:
            self.surface = self.hover_surf
        else:
            self.surface, _ = self.generate_image(self.factor, False)
        self.mask = self.hover_mask

    def generate_image(self, factor: float, swapped: bool) -> tuple[pygame.Surface, pygame.Mask]:
        self.text_surf = self.font.render(self.text, True, self.color)
        text_size = VEC(self.text_surf.get_size())
        size = text_size * factor
        factor_diff = self.hover_factor - self.default_factor
        perc = (self.line_factor - self.default_factor) / factor_diff

        surf = pygame.Surface(size, SRCALPHA)

        # Create the top, right, bottom and left points (respectively) of the rhombus shaped button
        # +/- 2 for p1 and p3 (top and bottom) are to move the points inwards to avoid cutoff
        # +/- 2 for p2 and p4 (left and right) are to move the points outwards to cut off extra pixels
        p1, p2, p3, p4 = VEC(size.x // 2, 0 + 2), VEC(size.x + 2, size.y // 2), VEC(size.x // 2, size.y - 2), VEC(0 - 2, size.y // 2)

        pygame.gfxdraw.filled_polygon(surf, [p1, p2, p3, p4], (10, 10, 10))

        if perc < 0: perc = 0
        if perc > 1: perc = 1
        # Draw the lines on the clockwise direction of each side
        # +/- (1, 0) to patch up the slight gap on point 1
        aaline(surf, BULL_COLOR if swapped else BEAR_COLOR, p1 - (1, 0) + (p2 - p1) * perc, p2, 6)
        aaline(surf, BEAR_COLOR if swapped else BULL_COLOR, p2 + (p3 - p2) * perc, p3, 6)
        aaline(surf, BULL_COLOR if swapped else BEAR_COLOR, p3 + (p4 - p3) * perc, p4, 6)
        aaline(surf, BEAR_COLOR if swapped else BULL_COLOR, p4 + (p1 - p4) * perc, p1 + (1, 0), 6)

        # Draw the lines on the counterclockwise direction of each side
        aaline(surf, BEAR_COLOR if swapped else BULL_COLOR, p1, p1 + (p2 - p1) * perc, 6)
        aaline(surf, BULL_COLOR if swapped else BEAR_COLOR, p2, p2 + (p3 - p2) * perc, 6)
        aaline(surf, BEAR_COLOR if swapped else BULL_COLOR, p3, p3 + (p4 - p3) * perc, 6)
        aaline(surf, BULL_COLOR if swapped else BEAR_COLOR, p4, p4 + (p1 - p4) * perc, 6)
        surf.blit(self.text_surf, (size - text_size) // 2 - (0, 2))

        return surf, pygame.mask.from_surface(surf)
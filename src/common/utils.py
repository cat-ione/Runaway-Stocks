from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene
    from src.gui.hud import Image

from numpy import sin, cos, radians
import pygame.gfxdraw
import pygame

from src.common.constants import VEC, _pos, _color, Anchors

inttup = lambda tup: tuple(map(int, tuple(tup)))
intvec = lambda vec: VEC(int(vec.x), int(vec.y))

def pygame_draw_pie(screen: pygame.Surface, color: _color, center: _pos, rad: int, start_ang: int, end_ang: int, step: int = 10):
    if end_ang <= start_ang:
        return
    vertices = [center]
    for angle in range(start_ang, end_ang + 1, step):
        vertices.append(center + VEC(sin(radians(angle)), -cos(radians(angle))) * rad)
    last_angle = radians(angle + end_ang % step)
    vertices.append(center + VEC(sin(last_angle), -cos(last_angle)) * rad)
    pygame.gfxdraw.filled_polygon(screen, vertices, color)

def blur_surf(surf: pygame.Surface) -> pygame.Surface:
    """Smooth scale it down and up, then normal scale it down and up, to create a blur effect plus a pixelated effect"""
    surf = pygame.transform.smoothscale_by(surf, 0.25)
    surf = pygame.transform.smoothscale_by(surf, 4)
    surf = pygame.transform.scale_by(surf, 0.25)
    surf = pygame.transform.scale_by(surf, 4)
    return surf

def create_blurred_bg(scene: Scene) -> Image:
    """
    - Blur screen as surface
    - Create a custom Image object that will be displayed
    - Also return the object for accessibility
    """

    blurred_img_surf = blur_surf(scene.manager.screen)
    blurred_img_obj = Image(scene, (0, 0), blurred_img_surf, anchor=Anchors.TOPLEFT)
    return blurred_img_obj
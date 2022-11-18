from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene
    from src.gui.hud import Image

from numpy import sin, cos, radians, floor
from pygame.locals import SRCALPHA
from typing import Callable
import pygame.gfxdraw
import pygame
import math

from src.common.constants import VEC, _pair, _color, Anchors

inttup = lambda tup: tuple(map(floor, tuple(tup)))
intvec = lambda vec: VEC(floor(vec.x), floor(vec.y))

def pygame_draw_pie(screen: pygame.Surface, color: _color, center: _pair, rad: int, start_ang: int, end_ang: int, step: int = 10):
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

def aapolygon(surface, points, color, scale=2):
    """
    Draw antialiased polygon using supersampling.
    https://stackoverflow.com/a/73805642/14692430
    """
    # Calculate minimum x and y values.
    x_coords = tuple(x for x, _ in points)
    x_min, x_max = min(x_coords), max(x_coords)
    y_coords = tuple(y for _, y in points)
    y_min, y_max = min(y_coords), max(y_coords)
    # Calculate width and height of target area.
    w = x_max - x_min + 1
    h = y_max - y_min + 1
    # Create scaled surface with properties of target surface.
    s = pygame.Surface((w * scale, h * scale), SRCALPHA, surface)
    s_points = [((x - x_min) * scale, (y - y_min) * scale)
                for x, y in points]
    pygame.draw.polygon(s, color, s_points)
    # Scale down surface to target size for supersampling effect.
    s2 = pygame.transform.smoothscale(s, (w, h))
    # Paint smooth polygon on target surface.
    surface.blit(s2, (x_min, y_min))

def aaline(surf: pygame.Surface, color: _color, p1: _pair, p2: _pair, width: int) -> None:
    """
    Slower but more consistent, better looking, and less buggy way of drawing an aaline
    https://stackoverflow.com/a/73325603/14692430
    """
    d = (p2[0] - p1[0], p2[1] - p1[1])
    dis = math.hypot(*d)
    if not dis: return
    sp = (-d[1] * width / (2 * dis), d[0] * width / (2 * dis))

    p1_1 = (p1[0] - sp[0], p1[1] - sp[1])
    p1_2 = (p1[0] + sp[0], p1[1] + sp[1])
    p2_1 = (p2[0] - sp[0], p2[1] - sp[1])
    p2_2 = (p2[0] + sp[0], p2[1] + sp[1])

    aapolygon(surf, (p1_1, p1_2, p2_2, p2_1), color)
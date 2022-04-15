from enum import Enum
import pygame

VEC = pygame.math.Vector2
WIDTH, HEIGHT = 828, 512
CENTER = VEC(WIDTH // 2, HEIGHT // 2)
GRID_SPACE = VEC(48, 30)
HIGHSCORE_FILE = "highscore.txt"

# Directions
class Dir(Enum):
    UP = -1
    DOWN = 1
    
class Anchors(Enum):
    TOP = VEC(0, -1)
    BOTTOM = VEC(0, 1)
    LEFT = VEC(-1, 0)
    RIGHT = VEC(1, 0)
    CENTER = VEC(0, 0)
    TOPLEFT = VEC(-1, -1)
    TOPRIGHT = VEC(1, -1)
    BOTTOMLEFT = VEC(-1, 1)
    BOTTOMRIGHT = VEC(1, 1)

pygame.font.init()
FONTS = [pygame.font.SysFont("arial", size) for size in range(1, 121)]
BOLD_FONTS = [pygame.font.SysFont("arial", size, True) for size in range(1, 121)]
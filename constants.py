from enum import Enum

import pygame
from pygame.locals import *

VEC = pygame.math.Vector2
WIDTH, HEIGHT = 828, 512
GRID_SPACE = VEC(48, 30)
HIGHSCORE_FILE = "highscore.txt"

# Directions
class Dir(Enum):
    UP = -1
    DOWN = 1

pygame.font.init()
FONT1 = pygame.font.SysFont("arial", 16)
FONT2 = pygame.font.SysFont("arial", 18, True)
FONT3 = pygame.font.SysFont("arial", 40, True)
FONT4 = pygame.font.SysFont("arial", 64, True)
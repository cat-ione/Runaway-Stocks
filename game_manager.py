from enum import Enum
import pygame
import sys

from pygame.locals import QUIT, HWSURFACE, DOUBLEBUF

from constants import WIDTH, HEIGHT
from menus import MainGame, EndMenu

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop() / 1000
        self.events = []
        self.menu = MainGame(self, None)

    def run(self):
        while self.menu.running:
            self.update()
            self.menu.update()
            self.menu.draw()

    def update(self):
        self.dt = self.clock.tick_busy_loop() / 1000
        pygame.display.set_caption(f"游走股票 | FPS: {round(self.clock.get_fps())}")

        self.events = pygame.event.get()
        for event in self.events:
            if event.type == QUIT:
                self.quit()

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()
        
    def new_menu(self, menu_class):
        self.menu = self.Menus[menu_class].value(self, self.menu)
        
    class Menus(Enum):
        MainGame = MainGame
        EndMenu = EndMenu
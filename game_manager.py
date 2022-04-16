from enum import Enum
import pygame
import sys

from pygame.locals import QUIT, HWSURFACE, DOUBLEBUF

from constants import WIDTH, HEIGHT
from scenes import MainGame, EndScene

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop() / 1000
        self.events = []
        self.scene = MainGame(self, None)

    def run(self):
        while self.scene.running:
            self.update()
            self.scene.update()
            self.scene.draw()

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
        
    def new_scene(self, scene_class):
        self.scene = self.Scenes[scene_class].value(self, self.scene)
        
    class Scenes(Enum):
        MainGame = MainGame
        EndScene = EndScene
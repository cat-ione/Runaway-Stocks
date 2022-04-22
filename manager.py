from enum import Enum
import pygame
import sys

from pygame.locals import QUIT, HWSURFACE, DOUBLEBUF, RESIZABLE, WINDOWRESIZED, WINDOWMOVED

from constants import VEC, WIDTH, HEIGHT, FPS
from scenes import MainGame, EndMenu
from utils import inttup

class GameManager:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        self.resized_screen = self.screen.copy()
        self.display = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        self.window_changing = False
        self.events = []
        self.scene = MainGame(self, None)
        self.scene.setup()

    def run(self) -> None:
        while self.scene.running:
            self.update()
            self.scene.update()
            self.scene.draw()

    def update(self) -> None:
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        if self.window_changing:
            self.dt = 0
            self.window_changing = False

        pygame.display.set_caption(f"游走股票 | FPS: {round(self.clock.get_fps())}")

        self.events = pygame.event.get()
        for event in self.events:
            if event.type == QUIT:
                self.quit()
            elif event.type == WINDOWRESIZED or event.type == WINDOWMOVED:
                self.window_changing = True

        if (display_size := pygame.display.get_surface().get_size()) != (WIDTH, HEIGHT):
            smallest_ratio = min(display_size[0] / WIDTH, display_size[1] / HEIGHT)
            new_size = inttup(VEC(WIDTH, HEIGHT) * smallest_ratio)
            self.resized_screen = pygame.transform.smoothscale(self.screen, new_size)
            self.display.blit(self.resized_screen, (display_size[0] // 2 - new_size[0] // 2, display_size[1] // 2 - new_size[1] // 2))
        else:
            self.display.blit(self.screen, (0, 0))

        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()
        sys.exit()

    def new_scene(self, scene_class: type) -> None:
        self.scene = self.Scenes[scene_class].value(self, self.scene)
        self.scene.setup()

    class Scenes(Enum):
        MainGame = MainGame
        EndMenu = EndMenu
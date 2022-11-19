from enum import Enum
import pygame
import sys

from pygame.locals import QUIT, HWSURFACE, DOUBLEBUF, RESIZABLE, KEYDOWN, K_F9, SCALED, WINDOWRESIZED, WINDOWMOVED

from src.scenes import MainMenu, MainGame, PauseMenu, EndMenu
from src.common.constants import WIDTH, HEIGHT, FPS
from src.common.profiling import profile
from src.management.scene import Scene

class AbortScene(Exception):
    def __str__(self):
        return "Scene aborted but not catched with a try/except block."

class GameManager:
    def __init__(self) -> None:
        pygame.mixer.pre_init(buffer=32)
        pygame.init()
        pygame.mixer.init(buffer=32)

        self.screen = pygame.Surface((WIDTH, HEIGHT))
        self.resized_screen = self.screen.copy()
        self.flags = HWSURFACE | DOUBLEBUF | RESIZABLE | SCALED
        self.display = pygame.display.set_mode((WIDTH, HEIGHT), self.flags)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        self.window_changing = False
        self.events = []
        self.scene = MainMenu(self, None)
        self.scene.setup()

    def run(self) -> None:
        def tick():
            self.update()
            try:
                self.scene.update()
                self.scene.draw()
            except AbortScene:
                pass
        while self.scene.running:
            if KEYDOWN in self.events and self.events[KEYDOWN].key == K_F9:
                profile(tick)
            else:
                tick()

    def update(self) -> None:
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        # Window changing events only register to the DT the frame after the event
        # Thus the window changing variable is sustained to the next frame, and handled here
        if self.window_changing:
            self.dt = 0
            self.window_changing = False

        pygame.display.set_caption(f"Runaway Stocks | FPS: {round(self.clock.get_fps())}")
        
        self.events = {event.type: event for event in pygame.event.get()}

        if QUIT in self.events:
            self.quit()
        if WINDOWRESIZED in self.events or WINDOWMOVED in self.events:
            self.window_changing = True
            self.dt = 0

        self.display.blit(self.screen, (0, 0))

        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()
        sys.exit()

    def new_scene(self, scene_class: str) -> None:
        self.scene.running = False
        self.scene = self.Scenes[scene_class].value(self, self.scene)
        self.scene.setup()
        raise AbortScene

    def switch_scene(self, scene: Scene) -> None:
        self.scene.running = False
        self.scene = scene
        self.scene.running = True
        raise AbortScene

    class Scenes(Enum):
        MainMenu = MainMenu
        MainGame = MainGame
        PauseMenu = PauseMenu
        EndMenu = EndMenu
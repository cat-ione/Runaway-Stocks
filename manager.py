from enum import Enum
import pygame
import sys

from pygame.locals import QUIT, HWSURFACE, DOUBLEBUF, RESIZABLE, WINDOWRESIZED, WINDOWMOVED, KEYDOWN, K_F9, WINDOWRESTORED, WINDOWMAXIMIZED

from scene import Scene, MainMenu, MainGame, PauseMenu, EndMenu
from constants import WIDTH, HEIGHT, FPS
from profiling import profile

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
        self.flags = HWSURFACE | DOUBLEBUF | RESIZABLE
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
        self.display_size = pygame.display.get_surface().get_size()
        self.new_size = (WIDTH / HEIGHT * self.display_size[1], self.display_size[1])

        if QUIT in self.events:
            self.quit()
        if WINDOWRESIZED in self.events or WINDOWMOVED in self.events:
            self.dt = 0
            self.window_changing = True
            if WINDOWRESIZED in self.events:
                pygame.display.set_mode(self.new_size, self.flags)
        if WINDOWRESTORED in self.events and WINDOWMAXIMIZED not in self.events:
            self.new_size = (WIDTH, HEIGHT)
            pygame.display.set_mode(self.new_size, self.flags)

        if self.new_size != (WIDTH, HEIGHT):
            self.resized_screen = pygame.transform.smoothscale(self.screen, self.new_size)
            self.display.blit(self.resized_screen, (0, 0))
        else:
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
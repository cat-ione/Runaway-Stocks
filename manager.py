from enum import Enum
import pygame
import sys

from pygame.locals import QUIT, HWSURFACE, DOUBLEBUF, RESIZABLE, WINDOWRESIZED, WINDOWMOVED, KEYDOWN, K_F9

from scene import Scene, MainMenu, MainGame, PauseMenu, EndMenu, MainMenuBG
from constants import VEC, WIDTH, HEIGHT, FPS
from profiling import profile
from utils import inttup

class AbortScene(Exception):
    def __str__(self):
        return "Scene aborted but not catched with a try/except block."

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
        self.scene = MainMenu(self, None)
        self.scene.setup()

    def run(self) -> None:
        def tick():
            try:
                self.update()
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
        elif WINDOWRESIZED in self.events or WINDOWMOVED in self.events:
            self.window_changing = True

        # If the display size is not the default
        if (display_size := pygame.display.get_surface().get_size()) != (WIDTH, HEIGHT):
            # Get the smallest ratio to resize the screen by in order to fit the entire thing on the current display
            smallest_ratio = min(display_size[0] / WIDTH, display_size[1] / HEIGHT)
            new_size = inttup(VEC(WIDTH, HEIGHT) * smallest_ratio)
            # Scale the screen to the biggest fitting dimensions
            self.resized_screen = pygame.transform.smoothscale(self.screen, new_size)
            # Blit the new screen in the center of the display
            self.display.blit(self.resized_screen, (display_size[0] // 2 - new_size[0] // 2, display_size[1] // 2 - new_size[1] // 2))
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

    class Scenes(Enum):
        MainMenu = MainMenu
        MainGame = MainGame
        PauseMenu = PauseMenu
        EndMenu = EndMenu
from pygame.locals import KEYDOWN, K_ESCAPE
import pygame

from src.common.constants import HEIGHT, BOLD_FONTS, WIDTH, Anchors
from src.gui.elements import Label, Image
from src.management.scene import Scene
from src.common.utils import blur_surf
from src.gui.hud import ComplexTimer

class PauseMenu(Scene):
    def setup(self) -> None:
        super().setup()

        pygame.mixer.fadeout(500)
        pygame.mixer.music.pause()

        ComplexTimer.pause_all()

        Image(self, (0, 0), blur_surf(self.manager.screen), anchor=Anchors.TOPLEFT)
        Label(self, (WIDTH // 2, HEIGHT // 2), "Game Paused", BOLD_FONTS[80], (230, 230, 230))

    def update(self) -> None:
        super().update()

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_ESCAPE:
            pygame.mixer.music.unpause()
            self.manager.switch_scene(self.previous_scene)

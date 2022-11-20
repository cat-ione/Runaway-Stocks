from pygame.locals import KEYDOWN, K_ESCAPE
import pygame

from src.common.constants import HEIGHT, BOLD_FONTS, WIDTH, Anchors, MUSIC_VOLUME
from src.gui.elements import Label, Image
from src.management.scene import Scene
from src.common.utils import blur_surf
from src.gui.hud import ComplexTimer

class PauseMenu(Scene):
    def setup(self) -> None:
        super().setup()

        self.volume = pygame.mixer.music.get_volume()
        pygame.mixer.fadeout(500)

        ComplexTimer.pause_all()

        Image(self, (0, 0), blur_surf(self.previous_scene.surface), anchor=Anchors.TOPLEFT)
        Label(self, (WIDTH // 2, HEIGHT // 2), "Game Paused", BOLD_FONTS[80], (230, 230, 230))

    def update(self) -> None:
        super().update()

        if self.volume > 0:
            self.volume -= 0.1 * self.manager.dt
            pygame.mixer.music.set_volume(self.volume)
        else:
            self.volume = 0
            pygame.mixer.music.pause()

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_ESCAPE:
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.unpause()
            self.manager.switch_scene(self.previous_scene)
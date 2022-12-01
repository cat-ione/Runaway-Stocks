from pygame.locals import KEYDOWN, K_ESCAPE
import pytweening as tween
import pygame

from src.common.constants import HEIGHT, BOLD_FONTS, WIDTH, Anchors, MUSIC_VOLUME, MIN_BLUR_THRESHOLD
from src.management.menu_scene import MenuScene
from src.gui.elements import Label, Image
from src.common.utils import blur_surf
from src.gui.hud import ComplexTimer
from src.common.tween import Tween

# class PauseMenu(Scene):
#     def setup(self) -> None:
#         super().setup()

#         self.volume = pygame.mixer.music.get_volume()
#         pygame.mixer.fadeout(500)

#         ComplexTimer.pause_all()

#         self.bg_img = Image(self, (0, 0), self.previous_scene.surface, anchor=Anchors.TOPLEFT)
#         self.text = Label(self, (WIDTH // 2, HEIGHT // 2), "Game Paused", BOLD_FONTS[80], (230, 230, 230))

#         self.alpha_tween = Tween(self, 0, 255, 500, tween.easeInSine)
#         self.blur_tween = Tween(self, 0.25, MIN_BLUR_THRESHOLD, -0.8, tween.easeInOutQuad)
#         self.blur_tween.reset()
#         self.ending = False

#     def update(self) -> None:
#         super().update()

#         if self.volume > 0:
#             self.volume -= 0.1 * self.dt
#             pygame.mixer.music.set_volume(self.volume)
#         else:
#             self.volume = 0
#             pygame.mixer.music.pause()

#         self.alpha_tween()
#         self.text.surface.set_alpha(self.alpha_tween.value)
#         self.blur_tween()
#         if not self.blur_tween.ended:
#             self.bg_img.surface = blur_surf(self.previous_scene.surface, self.blur_tween.value)

#         if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_ESCAPE:
#             self.alpha_tween = Tween(self, 0, 255, -500, tween.easeInSine)
#             self.alpha_tween.reset()
#             self.blur_tween = Tween(self, 0.25, MIN_BLUR_THRESHOLD, 0.8, tween.easeInOutQuad)
#             self.ending = True

#         if self.ending and self.blur_tween.ended:
#             pygame.mixer.music.set_volume(MUSIC_VOLUME)
#             pygame.mixer.music.unpause()
#             self.manager.switch_scene(self.previous_scene)

class PauseMenu(MenuScene):
    class BG(MenuScene.BG):
        def setup(self) -> None:
            start_tween = Tween(self, 0.25, MIN_BLUR_THRESHOLD, -0.8, tween.easeInOutQuad)
            end_tween = Tween(self, 0.25, MIN_BLUR_THRESHOLD, 0.8, tween.easeInOutQuad)
            super().setup(start_tween, end_tween)

            self.bg_img = Image(self, (0, 0), self.previous_scene.surface, anchor=Anchors.TOPLEFT)

        def update(self) -> None:
            super().update()

            if not self.tween.ended:
                self.bg_img.surface = blur_surf(self.previous_scene.surface, self.tween.value)

    class GUI(MenuScene.GUI):
        def setup(self) -> None:
            start_tween = Tween(self, 0, 255, 700, tween.easeInSine)
            end_tween = Tween(self, 0, 255, -700, tween.easeInSine)
            super().setup(start_tween, end_tween)

            Label(self, (WIDTH // 2, HEIGHT // 2), "Game Paused", BOLD_FONTS[80], (230, 230, 230))

        def update(self) -> None:
            super().update()
            self.surface.set_alpha(self.tween.value)

    def setup(self) -> None:
        super().setup()

        self.volume = pygame.mixer.music.get_volume()
        pygame.mixer.fadeout(500)

        ComplexTimer.pause_all()

        self.next_scene = -1

    def update(self) -> None:
        super().update()

        if self.volume > 0:
            self.volume -= 0.1 * self.dt
            pygame.mixer.music.set_volume(self.volume)
        else:
            self.volume = 0
            pygame.mixer.music.pause()

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_ESCAPE:
            self.end()

    def kill(self) -> None:
        super().kill()

        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.unpause()
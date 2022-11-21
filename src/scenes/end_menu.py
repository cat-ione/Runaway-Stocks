from pygame.locals import KEYDOWN, K_SPACE
import pygame

from src.common.constants import HIGHSCORE_FILE, CENTER, BOLD_FONTS, Anchors
from src.gui.elements import Label, Image
from src.management.scene import Scene
from src.common.utils import blur_surf

class EndMenu(Scene):
    def setup(self) -> None:
        super().setup()

        self.volume = pygame.mixer.music.get_volume()
        pygame.mixer.fadeout(500)

        Image(self, (0, 0), blur_surf(self.previous_scene.surface), anchor=Anchors.TOPLEFT)

        try: # Try to open the highscore file and read the highscore
            with open(HIGHSCORE_FILE, "r") as f:
                self.highscore = int(f.read())
        except FileNotFoundError: # If the file isn't found, create the file
            f = open(HIGHSCORE_FILE, "x")
            f.close()
            self.highscore = 0
        except ValueError: # If file contains invalid format, set it to 0
            self.highscore = 0

        # If it is a new highscore, display "New Highscore!"
        if self.previous_scene.player.score > self.highscore:
            Label(self, CENTER, "New Highscore!", BOLD_FONTS[64], (230, 230, 230))
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.previous_scene.player.score)) # Update the highscore in the file
        else: # If it is not a new highscore, display the current highscore
            Label(self, CENTER, f"Highscore: {self.highscore}", BOLD_FONTS[64], (230, 230, 230))

        # Create labels to display the score and a prompt
        Label(self, CENTER - (0, 100), f"Score: {self.previous_scene.player.score}", BOLD_FONTS[64], (230, 230, 230))
        Label(self, CENTER + (0, 100), "Press space to restart", BOLD_FONTS[18], (230, 230, 230))

    def update(self) -> None:
        super().update()

        if self.volume > 0:
            self.volume -= 0.05 * self.manager.dt
            pygame.mixer.music.set_volume(self.volume)
        else:
            self.volume = 0
            pygame.mixer.music.pause()

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_SPACE:
            # Start new game
            self.manager.new_scene("MainGame")
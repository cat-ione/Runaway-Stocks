import time

from constants import BOLD_FONTS, VEC, Anchors
from utils import Sprite

class MainGameTimer(Sprite):
    def __init__(self, menu):
        menu.elements.append(self)
        self.menu = menu
        self.max_time = 60
        self.start_time = time.time()
        self.current_time = int(self.max_time - (time.time() - self.start_time))

    def update(self, dt):
        self.current_time = int(self.max_time - (time.time() - self.start_time))
        if self.current_time <= 0:
            self.menu.running = False
            self.menu.manager.new_menu("EndMenu")

    def draw(self, screen):
        screen.blit(BOLD_FONTS[40].render(" " + str(self.current_time) + " ", True, (230, 230, 230), (150, 150, 150)), (0, 0))

class Label(Sprite):
    def __init__(self, menu, pos, text, font, color, anchor=Anchors.CENTER):
        menu.elements.append(self)
        self.surface = font.render(text, True, color)
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self, dt):
        # ...
        pass

    def draw(self, screen):
        screen.blit(self.surface, self.pos)

class Image(Sprite):
    def __init__(self, menu, pos, surface, anchor=Anchors.CENTER):
        menu.elements.append(self)
        self.surface = surface
        self.pos = VEC(pos) - VEC((anchor.value.x + 1) * self.surface.get_width(), (anchor.value.y + 1) * self.surface.get_height()) // 2

    def update(self, dt):
        # ...
        pass

    def draw(self, screen):
        screen.blit(self.surface, self.pos)
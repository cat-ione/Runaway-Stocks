import sys
from pygame.locals import *
from random import randint, randrange, choices, choice, uniform
from enum import Enum, auto
from numpy import True_, cos, sin, radians, ceil, arctan, degrees
from math import pi
import pygame
import time
import os
from PIL import Image, ImageFilter

VEC = pygame.math.Vector2
WIDTH, HEIGHT = 828, 512
GRID_SPACE = VEC(48, 30)
HIGHSCORE_FILE = "highscore.txt"

inttup = lambda tup: tuple(map(int, tuple(tup)))
intvec = lambda vec: VEC(int(vec.x), int(vec.y))

# Directions
class Dir(Enum):
    UP = -1
    DOWN = 1

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
clock = pygame.time.Clock()

font1 = pygame.font.SysFont("arial", 16)
font2 = pygame.font.SysFont("arial", 18, True)
font3 = pygame.font.SysFont("arial", 40, True)
font4 = pygame.font.SysFont("arial", 64, True)

class Camera():
    def __init__(self, master):
        self.master = master
        self.actual_offset = self.master.pos - VEC(WIDTH, HEIGHT) / 2
        self.offset = intvec(self.actual_offset)

    def update(self, dt):
        tick_offset = self.master.pos - self.offset - VEC(WIDTH, HEIGHT) / 2
        if -1 < tick_offset.x < 1:
            tick_offset.x = 0
        if -1 < tick_offset.y < 1:
            tick_offset.y = 0
        self.actual_offset += tick_offset * 5 * dt
        self.offset = intvec(self.actual_offset)

class Arrow:
    class Segment:
        def __init__(self, arrow):
            arrow.segments.append(self)
            self.arrow = arrow
            self.speed = arrow.speed
            self.direction = arrow.direction
            self.color = arrow.color
            self.angle = arrow.angle
            self.start_pos = arrow.pos.copy()
            self.end_pos = self.start_pos.copy()

        def update(self, dt):
            if self.start_pos.x - self.arrow.camera.offset.x < 0:
                self.arrow.segments.remove(self)
                del self

        def draw(self, screen):
            pygame.draw.line(screen, self.color, self.start_pos - self.arrow.camera.offset, self.end_pos - self.arrow.camera.offset, 6)

    def __init__(self):
        self.speed = 200
        self.pos = VEC(0, 0)
        self.camera = Camera(self)
        self.direction = Dir.UP
        self.color = (232, 87, 87)
        self.angle = 40
        self.segments = []
        self.Segment(self)
        self.tip_offsets_upright = [VEC(0, 15), VEC(-6, -5), VEC(6, -5)]
        self.tip_offset_func = lambda c: inttup(self.pos + VEC(c) - self.camera.offset)
        self.tip_rotation_func = lambda c: c.rotate((90 - self.angle) * -self.direction.value) * self.direction.value
        self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
        self.score = 0
        self.start_time = time.time()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if not (keys[K_UP] and keys[K_DOWN]):
            if keys[K_UP] and self.direction != Dir.UP:
                self.start_time = time.time()
                self.direction = Dir.UP
                self.color = (232, 87, 87)
                self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
                self.Segment(self)
            elif keys[K_DOWN] and self.direction != Dir.DOWN:
                self.start_time = time.time()
                self.direction = Dir.DOWN
                self.color = (12, 120, 38)
                self.tip_offsets = list(map(self.tip_rotation_func, self.tip_offsets_upright))
                self.Segment(self)

        if time.time() - self.start_time > 1:
            self.score += -self.direction.value
            self.start_time = time.time()

        self.pos.x += cos(radians(self.angle * self.direction.value)) * self.speed * dt
        self.pos.y += sin(radians(self.angle * self.direction.value)) * self.speed * dt

        for segment in self.segments:
            segment.update(dt)
        self.segments[-1].start_pos = self.pos.copy()

        self.camera.update(dt)

    def draw(self, screen):
        for segment in self.segments:
            segment.draw(screen)
        pygame.draw.polygon(screen, self.color, list(map(self.tip_offset_func, self.tip_offsets)))
        text_surf = font2.render(str(self.score), True, (230, 230, 230))
        screen.blit(text_surf, (self.pos - self.camera.offset - VEC(text_surf.get_size()) // 2 - VEC(0, 20)))

class HorizontalGridline:
    instances = {}

    @staticmethod
    def tick(arrow, dt, screen):
        on_screen_lines = set()
        for y in range(int(arrow.pos.y / GRID_SPACE.y - WIDTH / GRID_SPACE.y / 2 - 1), int(arrow.pos.y / GRID_SPACE.y + WIDTH / GRID_SPACE.y / 2 + 2)):
            on_screen_lines.add(y)
            if y not in HorizontalGridline.instances:
                HorizontalGridline(arrow, y)
        for y, line in HorizontalGridline.instances.copy().items():
            if y in on_screen_lines:
                line.update(dt)
                line.draw(screen)
            else:
                del HorizontalGridline.instances[y]

    def __init__(self, arrow, y):
        __class__.instances[y] = self
        self.arrow = arrow
        self.y = y
        for _ in range(randint(1, 3)):
            Points(self.arrow, randint(-10, 10), (GRID_SPACE.x * randint(int(self.arrow.pos.x / GRID_SPACE.x - HEIGHT / GRID_SPACE.x - 10), int(self.arrow.pos.x / GRID_SPACE.x + HEIGHT / GRID_SPACE.x + 10)), GRID_SPACE.y * self.y))

    def update(self, dt):
        self.on_screen_start = VEC(0, self.y * GRID_SPACE.y - self.arrow.camera.offset.y)
        self.on_screen_end = VEC(WIDTH, self.y * GRID_SPACE.y - self.arrow.camera.offset.y)

    def draw(self, screen):
        pygame.draw.line(screen, (150, 150, 150), self.on_screen_start, self.on_screen_end)

class VerticalGridline:
    instances = {}

    @staticmethod
    def tick(arrow, dt, screen):
        on_screen_lines = set()
        for x in range(int(arrow.pos.x / GRID_SPACE.x - WIDTH / GRID_SPACE.x / 2 - 1), int(arrow.pos.x / GRID_SPACE.x + WIDTH / GRID_SPACE.x / 2 + 2)):
            on_screen_lines.add(x)
            if x not in VerticalGridline.instances:
                VerticalGridline(arrow, x)
        for x, line in VerticalGridline.instances.copy().items():
            if x in on_screen_lines:
                line.update(dt)
                line.draw(screen)
            else:
                del VerticalGridline.instances[x]

    def __init__(self, arrow, x):
        __class__.instances[x] = self
        self.arrow = arrow
        self.x = x
        for _ in range(randint(1, 4)):
            Points(self.arrow, randint(-10, 10), (GRID_SPACE.x * self.x, GRID_SPACE.y * randint(int(self.arrow.pos.y / GRID_SPACE.y - HEIGHT / GRID_SPACE.y / 2 - 10), int(self.arrow.pos.y / GRID_SPACE.y + HEIGHT / GRID_SPACE.y / 2 + 10))))

    def update(self, dt):
        self.on_screen_start = VEC(self.x * GRID_SPACE.x - self.arrow.camera.offset.x, 0)
        self.on_screen_end = VEC(self.x * GRID_SPACE.x - self.arrow.camera.offset.x, HEIGHT)
        if self.on_screen_start.x < -100:
            del __class__.instances[self.x]
            del self

    def draw(self, screen):
        pygame.draw.line(screen, (150, 150, 150), self.on_screen_start, self.on_screen_end)

class Points:
    instances = {}

    @staticmethod
    def tick(arrow, dt, screen):
        for points in Points.instances.copy().values():
            points.update(dt)
            points.draw(screen)

    def __init__(self, arrow: Arrow, val, pos):
        self.arrow = arrow
        __class__.instances[pos] = self
        self.val = val
        self.color = (232, 87, 87) if self.val > 0 else (12, 120, 38)
        self.pos = VEC(pos)

    def update(self, dt):
        if self.pos.distance_to(self.arrow.pos) < 10:
            self.arrow.score += self.val
            self.kill()
            return
        screen_pos = self.pos - self.arrow.camera.offset
        if screen_pos.x < -50:
            self.kill()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos - self.arrow.camera.offset, 4)
        screen.blit(font1.render(str(self.val), True, self.color), self.pos - self.arrow.camera.offset + VEC(3, 1))

    def kill(self):
        for _ in range(randint(30, 50)):
            Particle(self, self.arrow)
        del __class__.instances[inttup(self.pos)]
        del self

class Particle:
    instances = []

    def __init__(self, master, arrow):
        __class__.instances.append(self)
        self.arrow = arrow
        self.pos = VEC(master.pos)
        self.vel = VEC(uniform(-30, 30), uniform(-30, 30))
        while self.vel.x == 0 and self.vel.y == 0:
            self.vel = VEC(uniform(-30, 30), uniform(-30, 30))
        self.size = randint(1, 2)
        self.color = master.color

    def update(self, dt):
        if self.vel.x <= 2 and self.vel.y < 2:
            __class__.instances.remove(self)
            del self
            return
        self.vel -= self.vel.normalize() * 15 * dt
        self.pos += self.vel * dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, inttup(self.pos - self.arrow.camera.offset), self.size)

arrow = Arrow()

def game():
    arrow.__init__()
    start_time = time.time()
    Points.instances.clear()
    VerticalGridline.instances.clear()
    HorizontalGridline.instances.clear()

    force_exit = False
    running = True
    while running:
        dt = clock.tick_busy_loop() / 1000 # Used to calculate pixels per second

        screen.fill((30, 30, 30))
        pygame.display.set_caption(f"游走股票 | FPS: {round(clock.get_fps())}")

        HorizontalGridline.tick(arrow, dt, screen)
        VerticalGridline.tick(arrow, dt, screen)

        for particle in Particle.instances:
            particle.update(dt)
            particle.draw(screen)

        arrow.update(dt)
        arrow.draw(screen)

        Points.tick(arrow, dt, screen)

        current_time = int(60 - (time.time() - start_time))
        if current_time <= 0:
            running = False
        screen.blit(font3.render(" " + str(current_time) + " ", True, (230, 230, 230), (150, 150, 150)), (0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                force_exit = True

        pygame.display.flip()

    if force_exit:
        pygame.quit()
        sys.exit()

def menu():
    pygame.image.save(screen, "menu_blur_tmp.png")
    bg_image = Image.open(r"menu_blur_tmp.png").filter(ImageFilter.BoxBlur(6))
    bg_image = pygame.image.fromstring(bg_image.tobytes(), bg_image.size, bg_image.mode).convert_alpha()
    os.remove("menu_blur_tmp.png")

    try:
        with open(HIGHSCORE_FILE, "r") as f:
            highscore = int(f.read())
    except FileNotFoundError:
        open(HIGHSCORE_FILE, "x")
        highscore = 0
    except ValueError:
        highscore = 0
    if arrow.score > highscore:
        highscore_surf = font4.render("New highscore!", True, (230, 230, 230))
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(arrow.score))
    else:
        highscore_surf = font4.render("Highscore: " + str(highscore), True, (230, 230, 230))

    score_surf = font4.render("Score: " + str(arrow.score), True, (230, 230, 230))
    prompt_surf = font2.render("Press space to restart", True, (200, 200, 200))

    force_exit = False
    running = True
    while running:
        dt = clock.tick_busy_loop() / 1000 # Used to calculate pixels per second

        pygame.display.set_caption(f"游走股票 | FPS: {round(clock.get_fps())}")

        screen.blit(bg_image, (0, 0))
        screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(highscore_surf, (WIDTH // 2 - highscore_surf.get_width() // 2, HEIGHT // 2))
        screen.blit(prompt_surf, (WIDTH // 2 - prompt_surf.get_width() // 2, HEIGHT // 2 + 100))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                force_exit = True
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    running = False

        pygame.display.flip()

    if force_exit:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    while True:
        game()
        menu()
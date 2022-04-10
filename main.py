from numpy import True_, cos, sin, radians, ceil, arctan, degrees
from random import randint, randrange, choices, choice, uniform
from PIL import Image, ImageFilter
from enum import Enum, auto
from pygame.locals import *
from math import pi
import pygame
import time
import sys
import os

from constants import *
from utils import *
from player import Player
from gridlines import VerticalGridline, HorizontalGridline, Barrier
from effects import Particle, Shockwave
from points import Points

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
clock = pygame.time.Clock()

player = Player()

def game():
    player.__init__()
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

        HorizontalGridline.tick(player, dt, screen)
        VerticalGridline.tick(player, dt, screen)
        Barrier.tick(dt, screen)

        Points.tick(dt, screen)

        Particle.tick(dt, screen)
        Shockwave.tick(dt, screen)

        player.update(dt)
        player.draw(screen)

        current_time = int(60 - (time.time() - start_time))
        if current_time <= 0:
            running = False
        screen.blit(FONT3.render(" " + str(current_time) + " ", True, (230, 230, 230), (150, 150, 150)), (0, 0))

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
    if player.score > highscore:
        highscore_surf = FONT4.render("New highscore!", True, (230, 230, 230))
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(player.score))
    else:
        highscore_surf = FONT4.render("Highscore: " + str(highscore), True, (230, 230, 230))

    score_surf = FONT4.render("Score: " + str(player.score), True, (230, 230, 230))
    prompt_surf = FONT2.render("Press space to restart", True, (200, 200, 200))

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
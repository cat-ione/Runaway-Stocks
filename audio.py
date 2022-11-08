import pygame

break_barrier = pygame.mixer.Sound("res/audio/break_barrier.mp3")
break_barrier.set_volume(0.1)

point_pickup1 = pygame.mixer.Sound("res/audio/point1.mp3")
point_pickup1.set_volume(0.2)
point_pickup2 = pygame.mixer.Sound("res/audio/point2.mp3")
point_pickup2.set_volume(0.2)
point_pickup3 = pygame.mixer.Sound("res/audio/point3.mp3")
point_pickup3.set_volume(0.2)
point_pickup = [point_pickup1, point_pickup2, point_pickup3]

power_end = pygame.mixer.Sound("res/audio/power_end.mp3")
power_end.set_volume(0.1)
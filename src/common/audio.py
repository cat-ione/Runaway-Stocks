import pygame

pygame.mixer.pre_init(buffer=32)
pygame.mixer.init(buffer=32)

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

button_hover = pygame.mixer.Sound("res/audio/hover.mp3")
button_hover.set_volume(0.2)
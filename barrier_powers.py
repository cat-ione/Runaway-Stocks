from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING: from manager import GameManager

from random import randint

class Power:
    init = False

class Flip(Power):
    max_time = 5

class Angle(Power):
    max_time = 5
    angle = randint(20, 30) if randint(0, 1) else randint(50, 60)
    @staticmethod
    def reset():
        __class__.angle = randint(20, 30) if randint(0, 1) else randint(50, 60)
        
class Speed(Power):
    max_time = 10
    speed = randint(100, 150) if randint(0, 1) else randint(250, 300)
    @staticmethod
    def reset():
        __class__.speed = randint(100, 150) if randint(0, 1) else randint(250, 300)

barrier_powers = {
    Flip: 1,
    Angle: 1,
    Speed: 1
}
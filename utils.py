from abc import ABC as AbstractClass
from abc import abstractmethod

from constants import *

inttup = lambda tup: tuple(map(int, tuple(tup)))
intvec = lambda vec: VEC(int(vec.x), int(vec.y))

class Sprite(AbstractClass):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def update(self, dt) -> None:
        pass

    @abstractmethod
    def draw(self, screen) -> None:
        pass
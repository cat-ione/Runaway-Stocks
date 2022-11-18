from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.manager import GameManager

from typing import Callable

class Tween:
    def __init__(self, manager: GameManager, start: float, end: float, speed: float, tween_func: Callable, **kwargs) -> None:
        self.manager = manager
        self.start = start
        self.end = end
        self.range = self.end - self.start
        self.speed = speed
        self.tween_func = tween_func
        self.kwargs = kwargs

        self.linear_val = self.value = self.start
        self.perc = 0

    def reset(self) -> None:
        self.linear_val = self.value = self.start if self.speed > 0 else self.end

    def __call__(self) -> None:
        self.linear_val += self.speed * self.manager.dt
        if self.linear_val < self.start: self.linear_val = self.start
        if self.linear_val > self.end: self.linear_val = self.end
        self.perc = (self.linear_val - self.start) / self.range
        self.value = self.start + self.tween_func(self.perc, **self.kwargs) * self.range
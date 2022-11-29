from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

from typing import Callable

class Tween:
    def __init__(self, scene: Scene, start: float, end: float, speed: float, tween_func: Callable, cutoff: float = None, **kwargs) -> None:
        self.scene = scene
        self.start = start
        self.end = end
        self.range = self.end - self.start
        self.speed = speed
        self.tween_func = tween_func
        self.cutoff = cutoff
        self.kwargs = kwargs

        self.linear_val = self.value = self.start
        self.perc = 0
        self.ended = False

    def reset(self) -> None:
        self.linear_val = self.value = self.start if self.speed > 0 else self.end
        self.ended = False

    def __call__(self) -> None:
        self.linear_val += self.speed * self.scene.dt
        if self.linear_val < self.start:
            self.linear_val = self.start
            self.ended = True
        if self.linear_val > self.end:
            self.linear_val = self.end
            self.ended = True
        self.perc = (self.linear_val - self.start) / self.range
        self.value = self.start + self.tween_func(self.perc, **self.kwargs) * self.range

        if self.cutoff is None: return
        # If the value has reached the cutoff point, snap the linear value straight to the ending value
        if (self.value > self.cutoff) if self.speed > 0 else (self.value < self.cutoff):
            self.linear_val = self.end if self.speed > 0 else self.start
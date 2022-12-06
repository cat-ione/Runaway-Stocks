from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.management.scene import Scene

from typing import Callable

class Tween:
    def __init__(self, scene: Scene, low: float, high: float, speed: float, tween_func: Callable, cutoff: float = None, **kwargs) -> None:
        self.scene = scene
        self.start = low
        self.end = high
        self.range = self.end - self.start
        self.speed = speed
        self.tween_func = tween_func
        self.cutoff = cutoff
        self.kwargs = kwargs

        self.perc = 0
        self.reset()

    # Call reset after init if speed is negative
    # and if at the time of calling, the place where the value is used is supposed to be at the higher value
    # If the place where the value is used is supposed to be at the lower value, don't call reset
    # or else it would set the starting value to the higher value
    def reset(self) -> None:
        self.linear_val = self.value = self.start if self.speed > 0 else self.end
        self.ended = False

    def __call__(self) -> None:
        if self.ended: return

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
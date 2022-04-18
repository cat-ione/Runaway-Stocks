from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING: from manager import GameManager

class Power:
    init = False

class Flip(Power):
    max_time = 5

barrier_powers = {
    Flip: 1
}
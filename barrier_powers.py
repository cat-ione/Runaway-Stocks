from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING: from manager import GameManager

BarrierPower = Callable[[GameManager], None]

def flip(manager: GameManager):
    manager.scene.player.reverse = not manager.scene.player.reverse

barrier_powers = {
    flip: 1
}
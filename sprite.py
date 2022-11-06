from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager
    from scene import Scene

from abc import ABC as AbstractClass
from abc import abstractmethod
from enum import Enum, auto

class Layers(Enum):
    BACKGROUND_GRID = auto()
    BACKGROUND_POINTS = auto()
    GRID = auto()
    BARRIERS = auto()
    POINTS = auto()
    EFFECTS = auto()
    PLAYER_SHADOW = auto()
    PLAYER_TIMER = auto()
    PLAYER = auto()
    HUD = auto()

class Sprite(AbstractClass):
    def __init__(self, manager: GameManager, layer: int | Layers, scene: Scene = None) -> None:
        self._layer = Layers(layer)
        self.manager = manager
        self.scene = scene if scene else manager.scene

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    def kill(self) -> None:
        self.scene.sprite_manager.remove(self)

class VisibleSprite(Sprite):
    def __init__(self, manager: GameManager, layer: Layers, scene: Scene = None) -> None:
        super().__init__(manager, layer, scene)
        self.scene.sprite_manager.add(self)

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

class SpriteManager:
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager
        self.scene = self.manager.scene
        self.layers: dict[Layers, list[Sprite]] = {layer: [] for layer in Layers}

    def update(self) -> None:
        for layer in self.layers:
            for sprite in self.layers[layer]:
                sprite.update()

    def draw(self) -> None:
        for layer in self.layers:
            for sprite in self.layers[layer]:
                sprite.draw()

    def add(self, sprite: Sprite) -> None:
        self.layers[sprite._layer].append(sprite)

    def remove(self, sprite: Sprite) -> None:
        self.layers[sprite._layer].remove(sprite)
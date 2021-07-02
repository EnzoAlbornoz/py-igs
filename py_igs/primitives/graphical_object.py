from __future__ import annotations
from cairo import Matrix
from typing import TYPE_CHECKING, Tuple
from abc import ABC, abstractmethod
from objects.object_type import ObjectType
if TYPE_CHECKING:
    from primitives.vec2 import Vector2
    from cairo import Context

class GraphicalObject(ABC):
    # Define Interface
    @abstractmethod
    def get_type() -> ObjectType:
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def draw(self, cairo: Context, inherited_matrix: Matrix):
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def transform(self, transformation: Matrix):
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def get_center_coords(self) -> Vector2:
        raise NotImplementedError("GraphicalObject is an abstract class.")
    # Basic Color Implementation
    def set_color(self, color_rgba: Tuple[float, float, float, float]):
        self.color = color_rgba
    def get_color(self) -> Tuple[float, float, float, float]:
        return self.color
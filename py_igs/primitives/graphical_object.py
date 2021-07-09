from __future__ import annotations
from cairo import Matrix
from typing import TYPE_CHECKING, Tuple
from abc import ABC, abstractmethod
from objects.object_type import ObjectType
if TYPE_CHECKING:
    from primitives.vec2 import Vector2
    from cairo import Context

class GraphicalObject(ABC):
    # Define Constructor
    def __init__(self) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Pipeline Attributes
        self.in_pipeline = False
    # Define Interface
    @abstractmethod
    def get_type() -> ObjectType:
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def draw(self, cairo: Context):
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
    # Pipeline Methods
    @abstractmethod
    def pipeline(self) -> None:
        # Turn on the Pipeline
        self.in_pipeline = True
    @abstractmethod
    def pipeline_apply(self) -> None:
        # Turn off the Pipeline
        self.in_pipeline = False
    def pipeline_abort(self) -> None:
        # Turn off the Pipeline
        self.in_pipeline = False
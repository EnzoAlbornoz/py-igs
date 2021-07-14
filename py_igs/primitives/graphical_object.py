from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from abc import ABC, abstractmethod
from objects.object_type import ObjectType
from primitives.matrix import Matrix, Vector2
if TYPE_CHECKING:
    from cairo import Context

class GraphicalObject(ABC):
    # Define Constructor
    def __init__(self) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Color Attributes
        self.color = (1,1,1,1)
        # Define Pipeline Attributes
        self.in_pipeline = False
    # Define Interface
    @abstractmethod
    def get_type() -> ObjectType:
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def draw(self, cairo: Context) -> None:
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def transform(self, transformation: Matrix) -> GraphicalObject:
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
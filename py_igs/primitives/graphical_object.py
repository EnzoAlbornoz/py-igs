from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from abc import ABC, abstractmethod
from typing_extensions import TypeGuard

from primitives.matrix import Vector3
if TYPE_CHECKING:
    from primitives.clipping_method import EClippingMethod
    from objects.object_type import ObjectType
    from primitives.matrix import Matrix, Vector2
    from cairo import Context

class GraphicalObject(ABC):
    # Define Constructor
    def __init__(self) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Color Attributes
        self.color = (1,1,1,1)
        # Define Dimensions Attributes
        self.projected: bool = False
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
    # Clipping Methods
    @abstractmethod
    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        raise NotImplementedError("GraphicalObject is an abstract class.")

class Graphical3DObject(GraphicalObject):
    def __init__(self) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Dimensions Attributes
        self.projected: bool = True
    @abstractmethod
    def project(self, projection_matrix: Matrix) -> GraphicalObject:
        raise NotImplementedError("Graphical3DObject is an abstract class.")
    @abstractmethod
    def get_center_coords3(self) -> Vector3:
        raise NotImplementedError("Graphical3DObject is an abstract class.")
    def get_center_coords(self) -> Vector2:
        return self.get_center_coords3().try_into_vec2()
    # Cannot Render 3D Objects without projecting it
    def draw(self, cairo: Context) -> None:
        raise NotImplementedError("Cannot Render Graphical3DObject without projecting it")
    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        raise NotImplementedError("Cannot Render Graphical3DObject without projecting it")

def is_projected(val: GraphicalObject) -> TypeGuard[Graphical3DObject]:
    return val.projected
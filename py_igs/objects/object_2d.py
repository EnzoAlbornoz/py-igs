from __future__ import annotations
from typing import List, TYPE_CHECKING, Tuple
from objects.object_type import ObjectType
from objects.wireframe_2d import Wireframe2D
from primitives.clipping_method import EClippingMethod
from primitives.graphical_object import GraphicalObject
from primitives.matrix import Matrix, Vector2
if TYPE_CHECKING:
    from cairo import Context

class Object2D(GraphicalObject):
    # Define Constructor
    def __init__(self, *wireframes: Wireframe2D) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.wireframes: List[Tuple[bool, Wireframe2D]] = [(True, wireframe) for wireframe in wireframes]
    def __str__(self) -> str:
        desc = "Object2D\n"
        for wireframe in self.wireframes:
            desc += "\t" + wireframe.__str__() + "\n"
        return desc
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.OBJECT_2D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline wireframes
        for idx in range(len(self.wireframes)):
            _, wireframe = self.wireframes[idx]
            wireframe.pipeline()
            self.wireframes[idx] = (True, wireframe)
    def pipeline_apply(self):
        for _, wireframe in self.wireframes:
            wireframe.pipeline_apply()
    def pipeline_abort(self):
        for idx in range(len(self.wireframes)):
            _, wireframe = self.wireframes[idx]
            wireframe.pipeline_abort()
            self.wireframes[idx] = (True, wireframe)
    # Filled Methods
    def set_filled(self, fill: bool) -> None:
        for _, wireframe in self.wireframes:
            wireframe.set_filled(fill)
    # Define Methods
    def draw(self, cairo: Context):
        for clipped, wireframe in self.wireframes:
            if not clipped:
                wireframe.draw(cairo)
    
    def transform(self, transformation: Matrix):
        for _, wireframe in self.wireframes:
            wireframe.transform(transformation)
        # Return Chain
        return self

    def get_center_coords(self) -> Vector2:
        # Get wireframes
        wireframes_center_coords = [wireframe.get_center_coords() for _, wireframe in self.wireframes]
        wireframes_center = sum(wireframes_center_coords, Vector2(0, 0))
        # Compute Average
        return (wireframes_center * (1 / len(wireframes_center_coords))).try_into_vec2()

    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        self.wireframes = [(wireframe.clip(method) is None, wireframe) for _, wireframe in self.wireframes]
        return self
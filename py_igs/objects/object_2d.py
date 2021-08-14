from __future__ import annotations
from typing import TYPE_CHECKING, cast
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
        self.wireframes = list(wireframes)
        self.pipeline_wireframes = self.wireframes
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
    def __get_wireframes(self):
        return self.pipeline_wireframes if self.in_pipeline else self.wireframes

    def pipeline(self):
        # Reset Pipeline wireframes
        self.pipeline_wireframes = self.wireframes
    def pipeline_apply(self):
        self.wireframes = self.wireframes
    # Filled Methods
    def set_filled(self, fill: bool) -> None:
        for wireframe in self.__get_wireframes():
            wireframe.set_filled(fill)
    # Define Methods
    def draw(self, cairo: Context):
        for wireframe in self.__get_wireframes():
            wireframe.draw(cairo)
    
    def transform(self, transformation: Matrix):
        for wireframe in self.__get_wireframes():
            wireframe.transform(transformation)
        # Return Chain
        return self

    def get_center_coords(self) -> Vector2:
        # Get wireframes
        wireframes_center_coords = [wireframe.get_center_coords() for wireframe in self.__get_wireframes()]
        wireframes_center = sum(wireframes_center_coords, Vector2(0, 0))
        # Compute Average
        return (wireframes_center * (1 / len(wireframes_center_coords))).try_into_vec2()

    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        points = [cast(Wireframe2D, clipped_wf) for wf in self.wireframes if (clipped_wf := wf.clip(method)) is not None]
        if self.in_pipeline:
            self.pipeline_wireframes = points
        else:
            self.wireframes = points
        return self
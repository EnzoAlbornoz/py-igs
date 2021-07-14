from __future__ import annotations
from typing import TYPE_CHECKING
from primitives.graphical_object import GraphicalObject
from objects.object_type import ObjectType
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix, Vector2

class Line2D(GraphicalObject):
    # Define Constructor
    def __init__(self, point_a: Vector2, point_b: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.point_a = point_a
        self.point_b = point_b
        # Define Pipeline Attributes
        self.pipeline_point_a = point_a
        self.pipeline_point_b = point_b
    def __str__(self) -> str:
        if self.in_pipeline:
            return f"[({self.pipeline_point_a.get_x()}, {self.pipeline_point_a.get_y()}), ({self.pipeline_point_b.get_x()}, {self.pipeline_point_b.get_y()})]"
        else:
            return f"[({self.point_a.get_x()}, {self.point_a.get_y()}), ({self.point_b.get_x()}, {self.point_b.get_y()})]"
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.LINE_2D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_point_a = self.point_a
        self.pipeline_point_b = self.point_b
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.point_a = self.pipeline_point_a
            self.point_b = self.pipeline_point_b
            # Call Super
            super().pipeline_apply()
    # Define Methods
    def draw(self, cairo: Context):
        # Get Points
        point_a = self.pipeline_point_a if self.in_pipeline else self.point_a
        point_b = self.pipeline_point_b if self.in_pipeline else self.point_b
        # Cast points into homogeneus space
        homo2d_point_a = point_a.as_vec3(1)
        homo2d_point_b = point_b.as_vec3(1)
        # Cast to Vector2
        (x1, y1) = homo2d_point_a.try_into_vec2().as_tuple()
        (x2, y2) = homo2d_point_b.try_into_vec2().as_tuple()
        # Set Color
        cairo.set_source_rgba(*self.color)
        # Draw line in canvas
        cairo.move_to(x1, y1)
        cairo.line_to(x2, y2)
        cairo.stroke()
    
    def transform(self, transformation: Matrix):
        # Transform Points
        if self.in_pipeline:
            # Pipelines
            self.pipeline_point_a = (self.pipeline_point_a.as_vec3(1) * transformation).try_into_vec2()
            self.pipeline_point_b = (self.pipeline_point_b.as_vec3(1) * transformation).try_into_vec2()
        else:
            # Raw Transform
            self.point_a = (self.point_a.as_vec3(1) * transformation).try_into_vec2()
            self.point_b = (self.point_b.as_vec3(1) * transformation).try_into_vec2()
        # Return Chain
        return self

    def get_center_coords(self) -> Vector2:
        # Get Points
        point_a = self.pipeline_point_a if self.in_pipeline else self.point_a
        point_b = self.pipeline_point_b if self.in_pipeline else self.point_b
        # Return Center
        center_coord = (point_a.as_vec3(1) + point_b.as_vec3(1)) * 0.5
        return center_coord.try_into_vec2()
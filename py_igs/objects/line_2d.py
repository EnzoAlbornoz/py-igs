from __future__ import annotations
from typing import TYPE_CHECKING
from primitives.graphical_object import GraphicalObject
from objects.object_type import ObjectType
from primitives.vec2 import Vector2
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix

class Line2D(GraphicalObject):
    # Define Constructor
    def __init__(self, point_a: Vector2, point_b: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.point_a = point_a
        self.point_b = point_b
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.LINE_2D
    # Define Methods
    def draw(self, cairo: Context, inherited_matrix: Matrix):
        # Cast points into homogeneus space
        homo2d_point_a = self.point_a.as_vec3(1)
        homo2d_point_b = self.point_b.as_vec3(1)
        # Transform points to match screen coords
        homo2d_point_a *= inherited_matrix
        homo2d_point_b *= inherited_matrix
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
        # Transform points
        self.point_a = (self.point_a.as_vec3(1) * transformation).try_into_vec2()
        self.point_b = (self.point_b.as_vec3(1) * transformation).try_into_vec2()

    def get_center_coords(self) -> Vector2:
        center_coord_x = (self.point_a.get_x() + self.point_b.get_x()) / 2
        center_coord_y = (self.point_a.get_y() + self.point_b.get_y()) / 2
        return Vector2(center_coord_x, center_coord_y)
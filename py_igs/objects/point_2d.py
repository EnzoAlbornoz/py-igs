from __future__ import annotations
from typing import TYPE_CHECKING
from objects.object_type import ObjectType
from primitives.graphical_object import GraphicalObject
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix
    from primitives.vec2 import Vector2

class Point2D(GraphicalObject):
    # Define Constructor
    def __init__(self, point: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.point = point
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.POINT_2D
    # Define Methods
    def draw(self, cairo: Context, inherited_matrix: Matrix):
        # Cast points into homogeneus space
        homo2d_point = self.point.as_vec3(1)
        # Transform points to match screen coords
        homo2d_point *= inherited_matrix
        # Cast to Vector2
        (x1, y1) = homo2d_point.try_into_vec2().as_tuple()
        # Get Cairo Line Width
        line_width_half = cairo.get_line_width() / 2
        # Draw a line that mimic point in canvas (cairo has autoclip on line with same origin/destiny)
        cairo.move_to(x1 - line_width_half, y1)
        cairo.line_to(x1 + line_width_half, y1)
        cairo.stroke()
    
    def transform(self, transformation: Matrix):
        # Transform points
        self.point = (self.point.as_vec3(1) * transformation).try_into_vec2()
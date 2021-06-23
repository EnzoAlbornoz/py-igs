from __future__ import annotations
from typing import List, TYPE_CHECKING
from objects.object_type import ObjectType
from primitives.graphical_object import GraphicalObject
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix
    from primitives.vec2 import Vector2

class Wireframe2D(GraphicalObject):
    # Define Constructor
    def __init__(self, *points: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Check Points Length
        if len(points) < 3:
            raise ValueError("Wireframe2D need 3 or more points to be defined")
        # Define Attributes
        self.points: List[Vector2] = list(points)
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.WIREFRAME_2D
    # Define Methods
    def draw(self, cairo: Context, inherited_matrix: Matrix):
        # Cast points into homogeneus space and match them with screen coords
        xy_points = [
            (point.as_vec3(1) * inherited_matrix).try_into_vec2().as_tuple()
            for point in self.points
        ]
        xy_points_len = len(xy_points)
        # Draw segments in canvas
        for (x, y), idx in zip(xy_points, range(xy_points_len)):

            # Check non starting the drawing
            if idx != 0:
                 # Draw normal line
                cairo.line_to(x, y)
                # Check ending the drawing
                if idx == (xy_points_len - 1):
                    # Close drawing
                    (x_init, y_init) = xy_points[0]
                    cairo.line_to(x_init, y_init)
            else:
                # Move to polygon start
                cairo.move_to(x, y)
        # Show result
        cairo.stroke()
    
    def transform(self, transformation: Matrix):
        # Transform points
        self.points = [
            (point.as_vec3(1) * transformation).try_into_vec2()
            for point in self.points
        ]
from __future__ import annotations
from typing import TYPE_CHECKING
from objects.object_type import ObjectType
from primitives.clipping_method import EClippingMethod
from primitives.graphical_object import GraphicalObject
if TYPE_CHECKING:
    from cairo import Context
    from primitives.window import Window
    from primitives.matrix import Matrix, Vector2

class Wireframe2D(GraphicalObject):
    # Define Constructor
    def __init__(self, *points: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Check Points Length
        if len(points) < 3:
            raise ValueError("Wireframe2D need 3 or more points to be defined")
        # Define Attributes
        self.points = list(points)
        # Define Pipeline Attributes
        self.pipeline_points = list(points)
    def __str__(self) -> str:
        desc = "Wireframe2D\n"
        for point in (self.pipeline_points if self.in_pipeline else self.points):
            desc += "\t" + point.__str__() + "\n"
        return desc
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.WIREFRAME_2D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_points = list(self.points)
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.points = list(self.pipeline_points)
            # Call Super
            super().pipeline_apply()
    # Define Methods
    def draw(self, cairo: Context):
        # Get Points
        points = self.pipeline_points if self.in_pipeline else self.points
        # Set Color
        cairo.set_source_rgba(*self.color)
        # Cast points into homogeneus space and match them with screen coords
        xy_points = [ point.as_tuple() for point in points ]
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
        if self.in_pipeline:
            # Pipeline
            self.pipeline_points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.pipeline_points
            ]
        else:
            # Raw Transform
            self.points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.points
            ]
        # Return Chain
        return self

    def get_center_coords(self) -> Vector2:
        # Get Points
        points = self.pipeline_points if self.in_pipeline else self.points
        # Get Avg Point
        points_len_mult = 1 / len(points)
        avg_coords = Vector2(0, 0)
        for point in points:
            avg_coords += point
        avg_coords *= points_len_mult
        return avg_coords.try_into_vec2()

    def clip(self, window: Window, method: EClippingMethod) -> GraphicalObject | None:
        return self
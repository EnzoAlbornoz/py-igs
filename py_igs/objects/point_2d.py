from __future__ import annotations
from typing import TYPE_CHECKING
from objects.object_type import ObjectType
from primitives.clipping_method import EClippingMethod
from primitives.graphical_object import GraphicalObject
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix, Vector2

class Point2D(GraphicalObject):
    # Define Constructor
    def __init__(self, point: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.point = point
        # Define Pipeline Attributes
        self.pipeline_point = point
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.POINT_2D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_point = self.point
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.point = self.pipeline_point
            # Call Super
            super().pipeline_apply()
    def __get_current_point(self) -> Vector2:
        return self.pipeline_point if self.in_pipeline else self.point
    # Define Methods
    def draw(self, cairo: Context):
        # Get Point
        point = self.pipeline_point if self.in_pipeline else self.point
        # Cast points into homogeneus space
        homo2d_point = point.as_vec3(1)
        # Cast to Vector2
        (x1, y1) = homo2d_point.try_into_vec2().as_tuple()
        # Get Cairo Line Width
        old_width = cairo.get_line_width()
        new_width = 1
        line_width_half = new_width / 2
        cairo.set_line_width(new_width)
        # Set Color
        cairo.set_source_rgba(*self.color)
        # Draw a line that mimic point in canvas (cairo has autoclip on line with same origin/destiny)
        cairo.move_to(x1 - line_width_half, y1 - line_width_half)
        cairo.line_to(x1 + line_width_half, y1 - line_width_half)
        cairo.line_to(x1 + line_width_half, y1 + line_width_half)
        cairo.line_to(x1 - line_width_half, y1 + line_width_half)
        cairo.close_path()
        cairo.stroke()
        cairo.set_line_width(old_width)
    
    def transform(self, transformation: Matrix):
        # Transform Point
        if self.in_pipeline:
            # Pipelines
            self.pipeline_point = (self.pipeline_point.as_vec3(1) * transformation).try_into_vec2()
        else:
            # Raw Transform
            self.point = (self.point.as_vec3(1) * transformation).try_into_vec2()
        # Return Chain
        return self

    def get_center_coords(self) -> Vector2:
        return self.point        

    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        # Switch Method
        if method == EClippingMethod.POINT_CLIP:
            # Get Current Point
            point = self.__get_current_point()
            # Check Point in Window Domain
            if (
                point.get_x() >= -1 and point.get_x() <= 1 and
                point.get_y() >= -1 and point.get_y() <= 1 
            ):
                return self
            else:
                # If not in Domain -> Clip It
                return None
        else:
            # Default - Trait as None Clipping
            return self

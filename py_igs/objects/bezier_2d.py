from __future__ import annotations
# from itertools import chain
from typing import List, TYPE_CHECKING
from math import ceil, comb
from itertools import chain
from primitives.clipping_method import EClippingMethod, cohen_sutherland_clip_line, liang_barsky_clip_line
from primitives.graphical_object import GraphicalObject
from objects.object_type import ObjectType
from primitives.matrix import Vector2, Matrix
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix

def bezier_math_blending_function(step: float, *point_prs: float) -> float:
    n = len(point_prs) - 1
    return sum([pb * (comb(n, i) * (step ** i) * ((1 - step) ** (n - i))) for i, pb in enumerate(point_prs)], 0)

class Bezier2D(GraphicalObject):
    # Define Constructor
    def __init__(self, accuracy_step: float, *control_points: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.accuracy = accuracy_step
        self.control_points = list(control_points)
        self.render_points = self.__compute_poly_line_points(self.accuracy, self.control_points)
        # Define Pipeline Attributes
        self.pipeline_control_points = self.control_points
        self.pipeline_render_points = self.render_points
    # Private Methods
    def __compute_poly_line_points(self, accuracy: float, control_points: List[Vector2]) -> List[Vector2]:
        # Compute Number of Polygons 
        required_points_ammount = ceil(accuracy ** -1) - 1
        # Unzip Control Points List
        controls_x, controls_y = zip(*[p.as_tuple() for p in control_points])
        # Compute Render Points
        points = [
            Vector2(
                bezier_math_blending_function(it/(required_points_ammount - 1), *controls_x),
                bezier_math_blending_function(it/(required_points_ammount - 1), *controls_y)
            )
            for it in range(0, required_points_ammount)
        ]
        # Return Computed Points
        return points
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.BEZIER_2D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_control_points = self.control_points
        self.pipeline_render_points = self.__compute_poly_line_points(self.accuracy, self.control_points)
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.control_points = self.pipeline_control_points
            self.render_points = self.pipeline_render_points
            # Call Super
            super().pipeline_apply()

    def __get_controls_points(self) -> List[Vector2]:
        return self.pipeline_control_points if self.in_pipeline else self.control_points
    def __get_render_points(self) -> List[Vector2]:
        return self.pipeline_render_points if self.in_pipeline else self.render_points
    # Define Methods
    def draw(self, cairo: Context):
        # Get Points
        points = self.__get_render_points()
        # Cast points into homogeneus space
        homo2d_points = [point.as_tuple() for point in points]
        # Set Color
        cairo.set_source_rgba(*self.color)
        # Draw line in canvas
        for idx, (x, y) in  enumerate(homo2d_points):
            if idx == 0:
                cairo.move_to(x, y)
            else:
                cairo.line_to(x, y)
        cairo.stroke()
    
    def transform(self, transformation: Matrix):
        # Transform points
        if self.in_pipeline:
            # Pipeline
            self.pipeline_control_points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.pipeline_control_points
            ]
            self.pipeline_render_points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.pipeline_render_points
            ]
        else:
            # Raw Transform
            self.control_points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.control_points
            ]
            self.render_points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.render_points
            ]
        # Return Chain
        return self

    def get_center_coords(self) -> Vector2:
        # Get Points
        points = self.__get_controls_points()
        # Get Avg Point
        points_len_mult = 1 / len(points)
        avg_coords = Vector2(0, 0)
        for point in points:
            avg_coords += point
        avg_coords *= points_len_mult
        return avg_coords.try_into_vec2()

    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        # Get Control Points
        control_points = self.__get_controls_points()
        # Compute Dist Between 0 and 1
        # Get Render Points
        render_points = self.__compute_poly_line_points(self.accuracy, control_points)
        # Switch Method
        if method == EClippingMethod.LINE_COHEN_SUTHERLAND:
            # Clip Using Cohen Sutherland
            clipped_points = list(
                chain.from_iterable(
                    [
                        clipped_edge
                        for (idx, point) in enumerate(render_points[0:-1])
                        if (
                            clipped_edge := cohen_sutherland_clip_line(
                                point,
                                render_points[(idx + 1) % len(render_points)]
                            )
                        ) is not None
                    ]
                )
            )
            # print(len(render_points), len(clipped_points))
            # Check if needed to render
            if len(clipped_points) == 0:
                return None
            # Update Internal Data
            if self.in_pipeline:
                self.pipeline_render_points = clipped_points
            else:
                self.render_points = clipped_points
            # Process First Point
            return self
        elif method == EClippingMethod.LINE_LIANG_BARSKY:
            # Clip Using Cohen Sutherland
            clipped_points = list(
                chain.from_iterable(
                    [
                        clipped_edge
                        for (idx, point) in enumerate(render_points[0:-1])
                        if (
                            clipped_edge := liang_barsky_clip_line(
                                point,
                                render_points[(idx + 1) % len(render_points)]
                            )
                        ) is not None
                    ]
                )
            )
            # print(len(render_points), len(clipped_points))
            # Check if needed to render
            if len(clipped_points) == 0:
                return None
            # Update Internal Data
            if self.in_pipeline:
                self.pipeline_render_points = clipped_points
            else:
                self.render_points = clipped_points
            # Process First Point
            return self
        else:
            # Update Internal Data
            self.pipeline_render_points = render_points
            # Default - Trait as None Clipping
            return self
from __future__ import annotations
from math import ceil
# from itertools import chain
from typing import List, TYPE_CHECKING
from itertools import chain
from primitives.clipping_method import EClippingMethod, cohen_sutherland_clip_line, liang_barsky_clip_line
from primitives.graphical_object import GraphicalObject
from objects.object_type import ObjectType
from primitives.matrix import Vector2, Matrix
from numpy import array, float64
from numpy.typing import NDArray
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix

SPLINE_MATRIX = Matrix.from_list([
    [-1/6, 3/6,-3/6, 1/6],
    [ 3/6,-6/6, 3/6, 0/6],
    [-3/6, 0/6, 3/6, 0/6],
    [ 1/6, 4/6, 1/6, 0/6],
])
class BSpline2D(GraphicalObject):
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
        # Define Required Amount of Points
        required_points_ammount = ceil(accuracy ** -1) - 1
        # Define Step Matrix
        d1 = accuracy
        d2 = d1 * accuracy
        d3 = d2 * accuracy
        STEP_MATRIX = Matrix.from_list([
            [   0,   0,  0, 1],
            [  d3,  d2, d1, 0],
            [6*d3,2*d2,  0, 0],
            [6*d3,   0,  0, 0],
        ])
        STEP_SPLINE_MATRIX = STEP_MATRIX * SPLINE_MATRIX
        # Compute Points
        points: List[Vector2] = []
        for idx in range(len(control_points) - 3):
            # Get Points
            cpoints = control_points[idx:idx + 4]
            # Compute Component Parts
            get_x_mat_elements: NDArray[float64] = array([[cp.get_x() for cp in cpoints]], dtype=float64)
            get_y_mat_elements: NDArray[float64] = array([[cp.get_y() for cp in cpoints]], dtype=float64)
            geo_x_mat = Matrix(get_x_mat_elements).as_transposed()
            geo_y_mat = Matrix(get_y_mat_elements).as_transposed()
            # Define Initial Values
            x0, x1, x2, x3 = (STEP_SPLINE_MATRIX * geo_x_mat).columns()[0]
            y0, y1, y2, y3 = (STEP_SPLINE_MATRIX * geo_y_mat).columns()[0]
            # Define Segment Points
            points.append(Vector2(x0, y0))
            # Compute Iteration
            for _ in range(required_points_ammount):
                # Update Values
                x0 += x1; x1 += x2; x2 += x3
                y0 += y1; y1 += y2; y2 += y3
                # Append new segment
                points.append(Vector2(x0, y0))
        # Return Computed Points
        return points
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.BSPLINE_2D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_control_points = self.control_points
        self.pipeline_render_points = self.render_points
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
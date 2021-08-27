from __future__ import annotations
# from itertools import chain
from typing import List, TYPE_CHECKING, cast
from math import ceil
from itertools import chain

from numpy import array, float64
from numpy.typing import NDArray
from primitives.clipping_method import EClippingMethod, cohen_sutherland_clip_line, liang_barsky_clip_line
from primitives.graphical_object import Graphical3DObject, GraphicalObject
from objects.object_type import ObjectType
from primitives.matrix import Vector2, Matrix, Vector3, Vector4
from functools import reduce
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix

MATRIX_BEZIER_ARRAY: NDArray[float64] = array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 3, 0, 0], [1, 0, 0, 0]], dtype=float64)
MATRIX_BEZIER = Matrix(MATRIX_BEZIER_ARRAY)
class Bezier3D(Graphical3DObject):
    # Define Constructor
    def __init__(self, accuracy_step: float, *control_points: List[Vector3], accuracy_step_snd: float = 0) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.accuracy = accuracy_step
        self.accuracy_step_snd = self.accuracy if accuracy_step_snd == 0 else self.accuracy_step_snd
        self.control_points: List[List[Vector3]] = list(control_points)
        self.render_points = self.__compute_poly_line_points(self.accuracy, self.control_points)
        # Define Pipeline Attributes
        self.pipeline_control_points = self.control_points
        self.pipeline_render_points = self.render_points
        print(len(self.render_points))
        self.render_points_2d: List[List[Vector2]] = []
    # Private Methods
    def __compute_poly_line_points(self, accuracy: float, control_points: List[List[Vector3]]) -> List[List[Vector3]]:
        def ext(a: List[List[Vector3]], n: List[List[Vector3]]) -> List[List[Vector3]]:
            a.extend(n)
            return a
        return reduce(ext,[self.__compute_poly_line_points_section(accuracy, cpg) for cpg in control_points], cast(List[List[Vector3]],[]))
    def __compute_poly_line_points_section(self, accuracy: float, control_points: List[Vector3]) -> List[List[Vector3]]:
        # Compute Number of Polygons 
        required_points_ammount = ceil(accuracy ** -1) - 1
        controls_x, controls_y, controls_z = zip(*[p.as_tuple() for p in control_points])
        controls_x_e: NDArray[float64] = array(controls_x).reshape((4, 4))
        controls_y_e: NDArray[float64] = array(controls_y).reshape((4, 4))
        controls_z_e: NDArray[float64] = array(controls_z).reshape((4, 4))
        GX = Matrix(controls_x_e)
        GY = Matrix(controls_y_e)
        GZ = Matrix(controls_z_e)
        QM_X = MATRIX_BEZIER * GX * MATRIX_BEZIER
        QM_Y = MATRIX_BEZIER * GY * MATRIX_BEZIER
        QM_Z = MATRIX_BEZIER * GZ * MATRIX_BEZIER
        points: List[List[Vector3]] = []
        for si in range(required_points_ammount + 1):
            s = si / required_points_ammount
            S = Vector4(s**3, s**2, s, 1)
            points.append([])
            for ti in range(required_points_ammount + 1):
                t = ti / required_points_ammount
                T = Vector4(t**3, t**2, t, 1).as_transposed()

                qst_x = (S * QM_X * T).lines()[0][0]
                qst_y = (S * QM_Y * T).lines()[0][0]
                qst_z = (S * QM_Z * T).lines()[0][0]

                points[si].append(Vector3(qst_x, qst_y, qst_z))
        return points


    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.BEZIER_3D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_control_points = self.control_points
        self.pipeline_render_points = self.__compute_poly_line_points(self.accuracy, self.control_points)
        self.render_points_2d = []
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.control_points = self.pipeline_control_points
            self.render_points = self.pipeline_render_points
            # Call Super
            super().pipeline_apply()

    def __get_controls_points(self) -> List[List[Vector3]]:
        return self.pipeline_control_points if self.in_pipeline else self.control_points
    def __get_render_points(self) -> List[List[Vector3]]:
        return self.pipeline_render_points if self.in_pipeline else self.render_points
    def __get_2d_render_points(self) -> List[List[Vector2]]:
        return self.render_points_2d
    # Define Methods
    def project(self, projection_matrix: Matrix) -> GraphicalObject:
        # Get Lines
        lines = self.__get_render_points()
        # Transform Points
        self.render_points_2d = [[(point.as_vec4(1) * projection_matrix).try_into_vec3_homo().try_into_vec2() for point in line] for line in lines]
        # Return Chain
        return self

    def draw(self, cairo: Context):
        # Set Color
        cairo.set_source_rgba(*self.color)
        # Get Lines
        lines = self.__get_2d_render_points()
        columns = list(map(lambda x: list(x), zip(*lines)))
        for points in lines:
            # Cast points into homogeneus space
            homo2d_points = [point.as_tuple() for point in points]
            # Draw line in canvas
            for idx, (x, y) in  enumerate(homo2d_points):
                if idx == 0:
                    cairo.move_to(x, y)
                else:
                    cairo.line_to(x, y)
            cairo.stroke()
        for points in columns:
            # Cast points into homogeneus space
            homo2d_points = [point.as_tuple() for point in points]
            # Draw line in canvas
            for idx, (x, y) in  enumerate(homo2d_points):
                if idx == 0:
                    cairo.move_to(x, y)
                else:
                    cairo.line_to(x, y)
            cairo.stroke()
    
    def transform(self, transformation: Matrix):
        # Transform points
        if isinstance(transformation, Vector4):
            if self.in_pipeline:
                # Pipeline
                self.pipeline_control_points = [
                    [(point.as_vec4(1) * transformation).try_into_vec3() for point in line]
                    for line in self.pipeline_control_points
                ]
                self.pipeline_render_points = [
                    [(point.as_vec4(1) * transformation).try_into_vec3() for point in line]
                    for line in self.pipeline_render_points
                ]
            else:
                # Raw Transform
                self.control_points = [
                    [(point.as_vec4(1) * transformation).try_into_vec3() for point in line]
                    for line in self.control_points
                ]
                self.render_points = [
                    [(point.as_vec4(1) * transformation).try_into_vec3() for point in line]
                    for line in self.render_points
                ]
        else:
            self.render_points_2d = [
                    [(point.as_vec3(1) * transformation).try_into_vec2() for point in line]
                    for line in self.render_points_2d
                ]
        # Return Chain
        return self

    def get_center_coords3(self) -> Vector3:
        # Get Points
        points = list(chain.from_iterable(self.__get_controls_points()))
        # Get Avg Point
        points_len_mult = 1 / len(points)
        avg_coords = Vector3(0, 0, 0)
        for point in points:
            avg_coords += point
        avg_coords *= points_len_mult
        return avg_coords.try_into_vec3()

    def get_center_coords(self) -> Vector2:
        # Get Points
        points = list(chain.from_iterable(self.__get_2d_render_points()))
        # Get Avg Point
        points_len_mult = 1 / len(points)
        avg_coords = Vector2(0, 0)
        for point in points:
            avg_coords += point
        avg_coords *= points_len_mult
        return avg_coords.try_into_vec2()

    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        # Compute Dist Between 0 and 1
        # Get Render Points
        render_points = self.render_points_2d
        # Switch Method
        if method == EClippingMethod.LINE_COHEN_SUTHERLAND:
            # Clip Using Cohen Sutherland
            clipped_points = [data for render_points_lines in render_points if len((data := list(
                chain.from_iterable(
                    [
                        clipped_edge
                        for (idx, point) in enumerate(render_points_lines[0:-1])
                        if (
                            clipped_edge := cohen_sutherland_clip_line(
                                point,
                                render_points_lines[(idx + 1) % len(render_points_lines)]
                            )
                        ) is not None
                    ]
                )
            ))) != 0]
            # print(len(render_points), len(clipped_points))
            # Check if needed to render
            if len(clipped_points) == 0:
                return None
            # Update Internal Data
            self.render_points_2d = clipped_points
            # Process First Point
            return self
        elif method == EClippingMethod.LINE_LIANG_BARSKY:
            # Clip Using Liang Barsky
            clipped_points = [data for render_points_lines in render_points if len((data := list(
                chain.from_iterable(
                    [
                        clipped_edge
                        for (idx, point) in enumerate(render_points_lines[0:-1])
                        if (
                            clipped_edge := liang_barsky_clip_line(
                                point,
                                render_points_lines[(idx + 1) % len(render_points_lines)]
                            )
                        ) is not None
                    ]
                )
            ))) != 0]
            # print(len(render_points), len(clipped_points))
            # Check if needed to render
            if len(clipped_points) == 0:
                return None
             # Update Internal Data
            self.render_points_2d = clipped_points
            # Process First Point
            return self
        else:
            # Update Internal Data
            self.render_points_2d = render_points
            # Default - Trait as None Clipping
            return self
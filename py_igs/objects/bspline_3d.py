from __future__ import annotations
# from itertools import chain
from typing import List, TYPE_CHECKING
from math import ceil
from itertools import chain

from numpy import array, float64
from numpy.typing import NDArray
from primitives.clipping_method import EClippingMethod, cohen_sutherland_clip_line, liang_barsky_clip_line
from primitives.graphical_object import Graphical3DObject, GraphicalObject
from objects.object_type import ObjectType
from primitives.matrix import Vector2, Matrix, Vector3, Vector4
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix

SPLINE_MATRIX = Matrix.from_list([
    [-1/6, 3/6,-3/6, 1/6],
    [ 3/6,-6/6, 3/6, 0/6],
    [-3/6, 0/6, 3/6, 0/6],
    [ 1/6, 4/6, 1/6, 0/6],
])
SPLINE_MATRIX_TRANSPOSED = SPLINE_MATRIX.as_transposed()
class BSpline3D(Graphical3DObject):
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
        self.render_points_2d: List[List[Vector2]] = []
    # Private Methods
    def __compute_poly_line_points(self, accuracy: float, control_points: List[List[Vector3]]) -> List[List[Vector3]]:
        # Split in 4x4 chunks
        total_lines = len(control_points)
        total_columns = len(control_points[0])
        sub_mats: List[List[List[Vector3]]] = []
        for i in range(total_lines - 3):
            for j in range(total_columns - 3):
                sub_mats.append(
                    [[control_points[ix][jx] for jx in range(j, j+4)] for ix in range(i, i+4)]
                )
        return list(chain.from_iterable([self.__compute_poly_line_points_section(accuracy, sub_mat) for sub_mat in sub_mats]))

    def __compute_fwd_diff_curve(self, n: int, x_l: List[float], y_l: List[float], z_l: List[float]) -> List[Vector3]:
        x, x1, x2, x3 = x_l
        y, y1, y2, y3 = y_l
        z, z1, z2, z3 = z_l
        line_points = [Vector3(x, y, z)]
        for _ in range(1, n):
            # Update Values
                x += x1; x1 += x2; x2 += x3
                y += y1; y1 += y2; y2 += y3
                z += z1; z1 += z2; z2 += z3
                # Append new segment
                line_points.append(Vector3(x, y, z))
        return line_points
    def __compute_poly_line_points_section(self, accuracy: float, control_points: List[List[Vector3]]) -> List[List[Vector3]]:
        # Compute Number of Polygons 
        required_points_ammount_st = ceil(accuracy ** -1)
        required_points_ammount_nd = ceil(self.accuracy_step_snd ** -1)
        controls_x_e: NDArray[float64] = array([[cpe.get_x() for cpe in cpl] for cpl in control_points])
        controls_y_e: NDArray[float64] = array([[cpe.get_y() for cpe in cpl] for cpl in control_points])
        controls_z_e: NDArray[float64] = array([[cpe.get_z() for cpe in cpl] for cpl in control_points])
        GX = Matrix(controls_x_e)
        GY = Matrix(controls_y_e)
        GZ = Matrix(controls_z_e)
        # print("GX: ",GX)
        ES = Matrix.from_list([
            [0, 0, 0, 1],
            [accuracy**3, accuracy**2, accuracy, 0],
            [6*accuracy**3, 2*accuracy**2, 0, 0],
            [6*accuracy**3, 0, 0, 0],
        ])
        # print("ES: ", ES)
        ET = Matrix.from_list([
            [0, 0, 0, 1],
            [self.accuracy_step_snd**3, self.accuracy_step_snd**2, self.accuracy_step_snd, 0],
            [6*self.accuracy_step_snd**3, 2*self.accuracy_step_snd**2, 0, 0],
            [6*self.accuracy_step_snd**3, 0, 0, 0],
        ])

        ddx = ES * SPLINE_MATRIX * GX * SPLINE_MATRIX_TRANSPOSED * (ET.as_transposed())
        ddy = ES * SPLINE_MATRIX * GY * SPLINE_MATRIX_TRANSPOSED * (ET.as_transposed())
        ddz = ES * SPLINE_MATRIX * GZ * SPLINE_MATRIX_TRANSPOSED * (ET.as_transposed())
        # print("ddx: ", ddx)

        points: List[List[Vector3]] = []

        for _ in range(1, required_points_ammount_st):
            ddxl = ddx.lines()
            ddyl = ddy.lines()
            ddzl = ddz.lines()
            
            line = self.__compute_fwd_diff_curve(required_points_ammount_st - 1, ddxl[0], ddyl[0], ddzl[0])
            # print(line)
            points.append(line)

            ddx = ddx + Matrix.from_list([ddxl[li + 1] if li < 3 else ddxl[li] for li in range(4)])
            ddy = ddy + Matrix.from_list([ddyl[li + 1] if li < 3 else ddyl[li] for li in range(4)])
            ddz = ddz + Matrix.from_list([ddzl[li + 1] if li < 3 else ddzl[li] for li in range(4)])

        ddx = (ES * SPLINE_MATRIX * GX * SPLINE_MATRIX_TRANSPOSED * ET.as_transposed()).as_transposed()
        ddy = (ES * SPLINE_MATRIX * GY * SPLINE_MATRIX_TRANSPOSED * ET.as_transposed()).as_transposed()
        ddz = (ES * SPLINE_MATRIX * GZ * SPLINE_MATRIX_TRANSPOSED * ET.as_transposed()).as_transposed()

        for _ in range(1, required_points_ammount_nd):
            ddxl = ddx.lines()
            ddyl = ddy.lines()
            ddzl = ddz.lines()
            
            line = self.__compute_fwd_diff_curve(required_points_ammount_nd - 1, ddxl[0], ddyl[0], ddzl[0])
            points.append(line)

            ddx = ddx + Matrix.from_list([ddxl[li + 1] if li < 3 else ddxl[li] for li in range(4)])
            ddy = ddy + Matrix.from_list([ddyl[li + 1] if li < 3 else ddyl[li] for li in range(4)])
            ddz = ddz + Matrix.from_list([ddzl[li + 1] if li < 3 else ddzl[li] for li in range(4)])

        return points


    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.BSPLINE_3D
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
        render_points_cols = list(map(lambda x: list(x), zip(*self.render_points_2d)))
        render_points = self.render_points_2d
        render_points.extend(render_points_cols)
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
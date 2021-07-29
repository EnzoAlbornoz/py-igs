from __future__ import annotations
from time import perf_counter
from typing import List, TYPE_CHECKING
from math import acos

import cairo
from objects.object_type import ObjectType
from primitives.clipping_method import EClippingMethod
from primitives.graphical_object import GraphicalObject
from primitives.matrix import Matrix, Vector2, homo_coords2_matrix_rotate, homo_coords2_matrix_scale, homo_coords2_matrix_translate
if TYPE_CHECKING:
    from primitives.display_file import DisplayFile
class Window:
    # Initializes the Window
    def __init__(self, x_world_min: float, y_world_min: float, x_world_max: float, y_world_max: float) -> None:
        # Initialize Attributes
        self.x_min = x_world_min
        self.y_min = y_world_min
        self.x_max = x_world_max
        self.y_max = y_world_max
        self.vec_up_x = x_world_min + ((x_world_max - x_world_min) / 2)
        self.vec_up_y = y_world_max
        # Define Clip Methods
        self.cliping_methods = {
            ObjectType.POINT_2D: EClippingMethod.POINT_CLIP,
            ObjectType.LINE_2D: EClippingMethod.LINE_LIANG_BARSKY,
            ObjectType.WIREFRAME_2D: EClippingMethod.POLY_WEILER_ATHERTON_WITH_LB,
            ObjectType.BEZIER_2D: EClippingMethod.LINE_LIANG_BARSKY,
            ObjectType.BSPLINE_2D: EClippingMethod.LINE_LIANG_BARSKY
        }
    # Define Getters and Setters
    def get_width(self) -> float:
        current_theta = self.get_vec_up_theta()
        (center_x, center_y) = self.get_center().as_tuple()

        translate_center = homo_coords2_matrix_translate(-center_x, -center_y)
        remove_rotate = homo_coords2_matrix_rotate(-current_theta)
        translate_back = homo_coords2_matrix_translate(center_x, center_y)
        
        max_point = Vector2(self.x_max, self.y_max).as_vec3(1)
        max_point *= translate_center * remove_rotate * translate_back
        return abs(max_point.try_into_vec2().get_x() - center_x) * 2
    def get_inverse_width(self) -> float:
        return 1 / self.get_width()
    def set_width(self, width: float) -> None:
        scale_width = width / self.get_width()
        self.scale(scale_width, 1)

    def get_height(self) -> float:
        current_theta = self.get_vec_up_theta()
        (center_x, center_y) = self.get_center().as_tuple()

        translate_center = homo_coords2_matrix_translate(-center_x, -center_y)
        remove_rotate = homo_coords2_matrix_rotate(-current_theta)
        translate_back = homo_coords2_matrix_translate(center_x, center_y)
        
        max_point = Vector2(self.x_max, self.y_max).as_vec3(1)
        max_point *= translate_center * remove_rotate * translate_back
        return (max_point.try_into_vec2().get_y() - center_y) * 2

    def get_inverse_height(self) -> float:
        return 1 / self.get_height()
    def set_height(self, height: float) -> None:
        scale_height = height / self.get_height()
        self.scale(1, scale_height)

    def get_center(self) -> Vector2:
        # Compute Centers
        min_point = Vector2(self.x_min, self.y_min)
        max_point = Vector2(self.x_max, self.y_max)
        # Return as Vector
        return ((min_point + max_point) * 0.5).try_into_vec2()

    def get_vec_up(self) -> Vector2:
        return Vector2(self.vec_up_x, self.vec_up_y)

    def get_vec_up_theta(self) -> float:
        # Get Vectors
        (center_x, center_y) = self.get_center().as_tuple()
        # Get Abs Vup and Vup
        (vup_x, vup_y) = self.get_vec_up().as_tuple()
        # Translate to Center
        vector_up = Vector2(vup_x - center_x, vup_y - center_y)
        abs_vec_up = Vector2(0, vector_up.modulo())
        # Compute Triangles Sides
        is_negative_x = vector_up.get_x() > 0
        # Check 0 Degrees
        if vector_up == abs_vec_up:
            return 0
        # Compute Angle Between Vectors
        value = (vector_up.dot_product(abs_vec_up) / (vector_up.modulo() * abs_vec_up.modulo()))
        value = max(min(value, 1), -1)
        theta = acos(value)
        # Check Negative Value
        theta *= -1 if is_negative_x else 1
        # Return Angle
        return theta
    # Define Transformations
    def pan(self, dx: float = 0, dy: float = 0):
        # Compute Delta Vectors
        vector_delta = Vector2(dx, dy).as_vec3(1)
        # Get Window Theta
        vup_theta = self.get_vec_up_theta()
        # Rotate Delta Vector
        vector_delta *= homo_coords2_matrix_rotate(vup_theta)
        # Cast as Vector 2
        vector_delta = vector_delta.try_into_vec2()
        # Update Data
        self.x_min += vector_delta.get_x()
        self.x_max += vector_delta.get_x()
        self.y_min += vector_delta.get_y()
        self.y_max += vector_delta.get_y()
        self.vec_up_x += vector_delta.get_x()
        self.vec_up_y += vector_delta.get_y()

    def scale(self, scale_factor_x: float = 1, scale_factor_y: float = 1):
        # Compute Window point as vectors
        (center_x, center_y) = self.get_center().as_tuple()
        left_bottom = Vector2(self.x_min, self.y_min)
        right_upper = Vector2(self.x_max, self.y_max)
        vector_up = self.get_vec_up()
        # Translate into origin
        translate_origin = homo_coords2_matrix_translate(-center_x, -center_y)
        # Scale
        scale_by_factor = homo_coords2_matrix_scale(scale_factor_x, scale_factor_y)
        # Translate back
        translate_back = homo_coords2_matrix_translate(center_x, center_y)
        # Compute Transforms
        grouped_transform = translate_origin * scale_by_factor * translate_back

        left_bottom = left_bottom.as_vec3(1) * grouped_transform
        right_upper = right_upper.as_vec3(1) * grouped_transform
        vector_up = vector_up.as_vec3(1) * grouped_transform
        # Destructure Values
        (x_min, y_min) = left_bottom.try_into_vec2().as_tuple()
        (x_max, y_max) = right_upper.try_into_vec2().as_tuple()
        (x_vup, y_vup) = vector_up.try_into_vec2().as_tuple()
        # Update Data
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.vec_up_x = x_vup
        self.vec_up_y = y_vup

    def rotate(self, theta_in_radians: float = 0):
        # Compute Window Points as Vectors
        (center_x, center_y) = self.get_center().as_tuple()
        left_bottom = Vector2(self.x_min, self.y_min)
        right_upper = Vector2(self.x_max, self.y_max)
        vector_up = self.get_vec_up()
        # Translate into origin
        translate_origin = homo_coords2_matrix_translate(-center_x, -center_y)
        # Perform Rotation
        rotate_theta = homo_coords2_matrix_rotate(theta_in_radians)
        # Translate Back to Center
        translate_back = homo_coords2_matrix_translate(center_x, center_y)
        # Compute Transforms
        grouped_transform = translate_origin * rotate_theta * translate_back
        left_bottom = left_bottom.as_vec3(1) * grouped_transform
        right_upper = right_upper.as_vec3(1) * grouped_transform
        vector_up = vector_up.as_vec3(1) * grouped_transform
        # Destructure Values
        (x_min, y_min) = left_bottom.try_into_vec2().as_tuple()
        (x_max, y_max) = right_upper.try_into_vec2().as_tuple()
        (x_vup, y_vup) = vector_up.try_into_vec2().as_tuple()
        # Update Data
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.vec_up_x = x_vup
        self.vec_up_y = y_vup

    # Define Normalized World Coordinates System
    def as_normalized_coordinates_transform(self):
        # Define World Center
        world_center = self.get_center()
        (center_x, center_y) = world_center.as_tuple()
        # Translate World Center to Origin
        translate_origin = homo_coords2_matrix_translate(-center_x, -center_y)
        # Define theta
        vector_up_theta = self.get_vec_up_theta()
        # Rotate World
        rotate_minus_theta = homo_coords2_matrix_rotate(-vector_up_theta)
        # Normalize By Window Size
        normalize_scale = homo_coords2_matrix_scale((2 * self.get_inverse_width()), (2 * self.get_inverse_height()))
        # Return as Transform
        return translate_origin * rotate_minus_theta * normalize_scale

    # Define Rendering
    def draw(self, cairo: cairo.Context, display_file: DisplayFile, viewport_transform: Matrix) -> None:
        # Compute Normalized Coordinates for the Window
        normalize = self.as_normalized_coordinates_transform()
        # Normalize Drawable Objects
        for drawable_object in display_file.get_drawable_objects():
            # Draw Object - Start Pipeline
            drawable_object.pipeline()
        time_c = perf_counter()
        for drawable_object in display_file.get_drawable_objects():
            # Normalize - World -> Generic Window
            drawable_object.transform(normalize)
        print(f"Normalization Time: {(perf_counter() - time_c) * 1000}ms")
        # Clip Display File Objects
        clipped_objects: List[GraphicalObject] = []
        time_c = perf_counter()
        for drawable_object in display_file.get_drawable_objects():
            # Clip Objects
            clipping_method = self.cliping_methods[drawable_object.get_type()]
            clipped_object = drawable_object.clip(clipping_method)
            # Check if need render
            if clipped_object is not None:
                clipped_objects.append(clipped_object)
            else:
                drawable_object.pipeline_abort()
        print(f"Clip Time: {(perf_counter() - time_c) * 1000}ms")
        # Draw Display File Objects
        time_c = perf_counter()
        for clipped_object in clipped_objects:
            # Viewport - Generic Window -> Device Window
            clipped_object.transform(viewport_transform)
            # Draw in Device Window
            clipped_object.draw(cairo)
            # End Pipeline
            clipped_object.pipeline_abort()
        print(f"Render Time: {(perf_counter() - time_c) * 1000}ms")
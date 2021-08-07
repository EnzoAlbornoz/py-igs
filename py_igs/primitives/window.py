from __future__ import annotations
from typing import TYPE_CHECKING
from math import cos, sin

import cairo
from objects.object_type import ObjectType
from primitives.clipping_method import EClippingMethod
from time import perf_counter_ns
from primitives.matrix import Matrix, Vector2, homo_coords2_matrix_rotate, homo_coords2_matrix_scale, homo_coords2_matrix_translate
if TYPE_CHECKING:
    from primitives.display_file import DisplayFile
class Window:
    # Initializes the Window
    def __init__(self, x_world_min: float, y_world_min: float, x_world_max: float, y_world_max: float) -> None:
        # Initialize Attributes
        self.theta = 0
        self.width = x_world_max - x_world_min
        self.height = y_world_max - y_world_min
        self.center_x = x_world_min + (self.width / 2)
        self.center_y = y_world_min + (self.height / 2)
        # Define Clip Methods
        self.cliping_methods = {
            ObjectType.POINT_2D: EClippingMethod.POINT_CLIP,
            ObjectType.LINE_2D: EClippingMethod.LINE_LIANG_BARSKY,
            ObjectType.WIREFRAME_2D: EClippingMethod.POLY_WEILER_ATHERTON_WITH_LB,
            ObjectType.BEZIER_2D: EClippingMethod.LINE_LIANG_BARSKY,
            ObjectType.BSPLINE_2D: EClippingMethod.LINE_LIANG_BARSKY
        }
        # Define Statistics
        self.show_stats = False
    # Define Getters and Setters
    def get_width(self) -> float:
        return self.width
    def get_inverse_width(self) -> float:
        return 1 / self.get_width()
    def set_width(self, width: float) -> None:
        self.width = width
    def get_height(self) -> float:
        return self.height

    def get_inverse_height(self) -> float:
        return 1 / self.get_height()
    def set_height(self, height: float) -> None:
        self.height = height

    def get_center(self) -> Vector2:
        # Return as Vector
        return Vector2(self.center_x, self.center_y)

    def get_vec_up(self) -> Vector2:
        vec_up_x = self.center_x + (self.width  / 2) * sin(-self.theta)
        vec_up_y = self.center_y + (self.height / 2) * cos(self.theta)
        return Vector2(vec_up_x, vec_up_y)

    def get_vec_up_theta(self) -> float:
        # Return Angle
        return self.theta
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
        self.center_x += vector_delta.get_x()
        self.center_y += vector_delta.get_y()

    def scale(self, scale_factor_x: float = 1, scale_factor_y: float = 1):
        # Scale Width and Height
        self.width *= scale_factor_x
        self.height *= scale_factor_y

    def rotate(self, theta_in_radians: float = 0):
        # Compute Window Points as Vectors
        center = self.get_center()
        (center_x, center_y) = center.as_tuple()
        # Translate into origin
        translate_origin = homo_coords2_matrix_translate(-center_x, -center_y)
        # Perform Rotation
        rotate_theta = homo_coords2_matrix_rotate(theta_in_radians)
        # Translate Back to Center
        translate_back = homo_coords2_matrix_translate(center_x, center_y)
        # Compute Transforms
        grouped_transform = translate_origin * rotate_theta * translate_back
        center = center.as_vec3(1) * grouped_transform
        # Destructure Values
        (x_center, y_center) = center.try_into_vec2().as_tuple()
        # Update Data
        self.x_center = x_center
        self.y_center = y_center

    # Define Corners
    def get_corner_bottom_left(self) -> Vector2:
        rotation = homo_coords2_matrix_rotate(self.theta)
        corner_bl = Vector2(self.center_x - (self.width / 2), self.center_y - (self.height / 2))
        return (corner_bl * rotation).try_into_vec2()

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
        comp_norm_time = 0
        norm_time = 0
        clip_time = 0
        draw_time = 0
        # Compute Normalized Coordinates for the Window
        time = perf_counter_ns()
        normalize = self.as_normalized_coordinates_transform()
        comp_norm_time = perf_counter_ns() - time
        # Draw Display File Objects
        render_all = perf_counter_ns()
        for drawable_object in display_file.get_drawable_objects():
            # Draw Object - Start Pipeline
            time = perf_counter_ns()
            drawable_object.pipeline()
            # Normalize - World -> Generic Window
            drawable_object.transform(normalize)
            norm_time += perf_counter_ns() - time
            time = perf_counter_ns()
            # Future Feature - Clipping
            # print("Line: ", drawable_object)
            clipping_method = self.cliping_methods[drawable_object.get_type()]
            clipped_object = drawable_object.clip(clipping_method)
            clip_time += perf_counter_ns() - time
            # Check if need render
            if clipped_object is not None:
                time = perf_counter_ns()
                # Viewport - Generic Window -> Device Window
                clipped_object.transform(viewport_transform)
                # Draw in Device Window
                clipped_object.draw(cairo)
                draw_time += perf_counter_ns() - time
                # End Pipeline
                clipped_object.pipeline_abort()
            else:
                drawable_object.pipeline_abort()
            # Reset Color
            cairo.set_source_rgba(1, 1, 1, 1)
        render_all = perf_counter_ns() - render_all
        if self.show_stats:
            print("------------------------------")
            print(f"Normal Mat Time:   \t{(comp_norm_time/1000000):.3f} ms")
            print(f"Normalization Time:\t{(norm_time/1000000):.3f} ms")
            print(f"Clipping Time:     \t{(clip_time/1000000):.3f} ms")
            print(f"Draw Time:         \t{(draw_time/1000000):.3f} ms")
            print(f"Frame Time:        \t{(render_all/1000000):.3f} ms")
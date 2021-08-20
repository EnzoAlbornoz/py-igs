from __future__ import annotations
from typing import TYPE_CHECKING

import cairo
from numpy import array, float64
from objects.object_type import ObjectType
from primitives.clipping_method import EClippingMethod
from time import perf_counter_ns
from primitives.graphical_object import is_projected
from primitives.matrix import Matrix, Vector2, Vector3, Vector4, homo_coords2_matrix_rotate, homo_coords2_matrix_scale, homo_coords2_matrix_translate, homo_coords3_matrix_rotate_x, homo_coords3_matrix_rotate_xyz, homo_coords3_matrix_rotate_y, homo_coords3_matrix_rotate_z, homo_coords3_matrix_translate
from numpy import float64, array
from numpy.typing import NDArray
if TYPE_CHECKING:
    from primitives.display_file import DisplayFile
class Window:
    # Initializes the Window
    def __init__(self, x_world_min: float, y_world_min: float, x_world_max: float, y_world_max: float, z_pos: float = 0) -> None:
        # Initialize Attributes
        self.theta_x = 0
        self.theta_y = 0
        self.theta_z = 0
        self.width = x_world_max - x_world_min
        self.height = y_world_max - y_world_min
        self.center_x = x_world_min + (self.width / 2)
        self.center_y = y_world_min + (self.height / 2)
        self.center_z = z_pos
        self.perspective_distance = 0
        # Define Clip Methods
        self.cliping_methods = {
            ObjectType.POINT_2D: EClippingMethod.POINT_CLIP,
            ObjectType.LINE_2D: EClippingMethod.LINE_LIANG_BARSKY,
            ObjectType.WIREFRAME_2D: EClippingMethod.POLY_WEILER_ATHERTON_WITH_LB,
            ObjectType.BEZIER_2D: EClippingMethod.LINE_LIANG_BARSKY,
            ObjectType.BSPLINE_2D: EClippingMethod.LINE_LIANG_BARSKY,
            ObjectType.OBJECT_2D: EClippingMethod.POLY_WEILER_ATHERTON_WITH_LB,
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

    def get_center(self) -> Vector3:
        # Return as Vector
        return Vector3(self.center_x, self.center_y, self.center_z)
    
    def set_center(self, center: Vector3) -> None:
        self.center_x = center.get_x()
        self.center_y = center.get_y()
        self.center_z = center.get_z()

    def get_vec_up(self) -> Vector3:
        # Get Initial Vec Up Vector
        vec_up = Vector3(0, self.height / 2, 0)
        # Rotate Vector to Match Standard
        rotate = homo_coords3_matrix_rotate_xyz(self.theta_x, self.theta_y, self.theta_z)
        # Move to Window Center
        move_center = homo_coords3_matrix_translate(self.center_x, self.center_y, self.center_z)
        return (vec_up.as_vec4(1) * rotate * move_center).try_into_vec3()

    def get_vec_up_theta(self) -> float:
        # Return Angle
        return self.theta_z

    def get_vec_normal(self) -> Vector3:
        if (self.perspective_distance != 0):
            # Get Initial Normal Vector
            vec_normal = Vector3(0, 0, -1)
            # Rotate Vector to Match Standard
            rotate = homo_coords3_matrix_rotate_xyz(self.theta_x, self.theta_y, self.theta_z)
            # Move to Window Center
            move_center = homo_coords3_matrix_translate(self.center_x, self.center_y, self.center_z)
            return (vec_normal.as_vec4(1) * rotate * move_center).try_into_vec3()
        else:
            return (self.get_center() - self.get_projection_ref_center()).try_into_vec3()

    def get_projection_ref_center(self) -> Vector3:
        vec_cop = self.get_center()
        if (self.perspective_distance != 0):
            transform = Vector3(0, 0, -self.perspective_distance).as_vec4(1)
            transform *= homo_coords3_matrix_rotate_xyz(self.theta_x, self.theta_y, self.theta_z)
            vec_cop = (transform - vec_cop.as_vec4(1)).try_into_vec3()
            print(vec_cop)
        return vec_cop


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
        # Update Value
        self.theta_z += theta_in_radians

    def move(self, dx: float, dy: float, dz: float):
        # Compute Delta Vectors
        vector_delta = Vector3(dx, dy, dz).as_vec4(1)
        # Rotate Delta Vector
        vector_delta *= homo_coords3_matrix_rotate_xyz(self.theta_x, self.theta_y, self.theta_z)
        # Cast as Vector 2
        vector_delta = vector_delta.try_into_vec3()
        # Update Data
        self.center_x += vector_delta.get_x()
        self.center_y += vector_delta.get_y()
        self.center_z += vector_delta.get_z()
    
    def rotate_vertical(self, theta_in_radians: float = 0):
        # Update Value
        self.theta_x += theta_in_radians

    def rotate_horizontal(self,  theta_in_radians: float = 0):
        # Update Value
        self.theta_y += theta_in_radians

    def rotate_x(self, tx: float = 0):
        #  Define Desired Rotation
        rotation_vec = Vector4(tx, 0, 0, 1)
        # Move to Origin
        rotation_vec *= homo_coords3_matrix_translate(-self.center_x, -self.center_y, -self.center_z)
        # Rotate
        rotation_vec *= homo_coords3_matrix_rotate_x(-self.theta_x)
        rotation_vec *= homo_coords3_matrix_rotate_z(-self.theta_z)
        rotation_vec *= homo_coords3_matrix_rotate_y(self.theta_y)
        rotation_vec *= homo_coords3_matrix_rotate_x(self.theta_x)
        rotation_vec *= homo_coords3_matrix_rotate_z(self.theta_z)
        # Cast Vector
        (theta_x, theta_y, theta_z) = rotation_vec.try_into_vec3().as_tuple()
        # Update Values
        self.theta_x += theta_x
        self.theta_y += theta_y
        self.theta_z += theta_z

    # Define Corners
    def get_corner_bottom_left(self) -> Vector2:
        rotation = homo_coords2_matrix_rotate(self.theta_z)
        corner_bl = Vector2(self.center_x - (self.width / 2), self.center_y - (self.height / 2))
        return (corner_bl * rotation).try_into_vec2()

    # Define Normalized World Coordinates System
    def as_normalized_coordinates_transform(self):
        # Define World Center
        world_center = self.get_center()
        (center_x, center_y, _) = world_center.as_tuple()
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

    def as_parallel_projection_transform(self): 
        # Define VRP - View Reference Poin
        vrp_center = self.get_projection_ref_center()
        (center_x, center_y, center_z) = vrp_center.as_tuple()
        # Translate VRP to Origin
        translate_origin = homo_coords3_matrix_translate(-center_x, -center_y, -center_z)
        # Define Thetas
        theta_x = self.theta_x
        theta_y = self.theta_y
        # Rotate World
        rotate_minus_theta = homo_coords3_matrix_rotate_xyz(-theta_x, -theta_y, 0)
        # Return as Transform
        return translate_origin * rotate_minus_theta

    def as_perspective_projection_transform(self):
        # Define VRP - View Reference Poin
        vrp_center = self.get_projection_ref_center()
        (vrp_center_x, vrp_center_y, vrp_center_z) = vrp_center.as_tuple()
        # Translate VRP to Origin
        translate_origin = homo_coords3_matrix_translate(-vrp_center_x, -vrp_center_y, -vrp_center_z)
        # Define Thetas
        theta_x = self.theta_x
        theta_y = self.theta_y
        # Rotate World
        rotate_minus_theta = homo_coords3_matrix_rotate_xyz(-theta_x, -theta_y, 0)
        # Intersect Window
        intersection_array: NDArray[float64] = array([[1,0,0,0],[0,1,0,0], [0,0,1,0], [0,0,1/self.perspective_distance,0]], dtype=float64)
        intersection = Matrix(intersection_array).as_transposed()
        # Return as Transform
        return translate_origin * rotate_minus_theta * intersection

    # Define Rendering
    def draw(self, cairo: cairo.Context, display_file: DisplayFile, viewport_transform: Matrix) -> None:
        comp_norm_time = 0
        comp_proj_time = 0
        proj_time = 0
        norm_time = 0
        clip_time = 0
        draw_time = 0
        # Compute Normalized Coordinates for the Window
        time = perf_counter_ns()
        normalize = self.as_normalized_coordinates_transform()
        comp_norm_time = perf_counter_ns() - time
        # Compute 3D Porjection for the Window
        time = perf_counter_ns()
        project = self.as_parallel_projection_transform() if self.perspective_distance == 0 else self.as_perspective_projection_transform()
        comp_proj_time = perf_counter_ns() - time
        # Draw Display File Objects
        render_all = perf_counter_ns()
        for drawable_object in display_file.get_drawable_objects():
            # Draw Object - Start Pipeline
            time = perf_counter_ns()
            drawable_object.pipeline()
            # 3D Transform
            if is_projected(drawable_object): 
                drawable_object = drawable_object.project(project)
            proj_time += perf_counter_ns() - time
            # Normalize - World -> Generic Window
            time = perf_counter_ns()
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
            print(f"Normal Mat Time:   \t{(comp_norm_time/1000000):07.3f} ms")
            print(f"Project Mat Time:  \t{(comp_proj_time/1000000):07.3f} ms")
            print(f"Projection Time:   \t{(proj_time/1000000):07.3f} ms")
            print(f"Normalization Time:\t{(norm_time/1000000):07.3f} ms")
            print(f"Clipping Time:     \t{(clip_time/1000000):07.3f} ms")
            print(f"Draw Time:         \t{(draw_time/1000000):07.3f} ms")
            print(f"Frame Time:        \t{(render_all/1000000):07.3f} ms")
from __future__ import annotations
from typing import List, Tuple
import cairo
from objects.line_2d import Line2D
from primitives.matrix import Matrix, homo_coords2_matrix_scale, homo_coords2_matrix_translate
from primitives.vec2 import Vector2

class Window:
    # Initializes the Window
    def __init__(self, x_world_min: float, y_world_min: float, x_world_max: float, y_world_max: float) -> None:
        # Initialize Attributes
        self.x_min = x_world_min
        self.y_min = y_world_min
        self.x_max = x_world_max
        self.y_max = y_world_max
    # Define Getters and Setters
    def get_width(self) -> float:
        return self.x_max - self.x_min
    def set_width(self, width: float) -> None:
        self.x_max = self.x_min + width

    def get_height(self) -> float:
        return self.y_max - self.y_min
    def set_height(self, height: float) -> None:
        self.y_max = self.y_min + height

    def get_center(self) -> Vector2:
        # Compute Centers
        center_x = self.x_min + (self.get_width() / 2)
        center_y = self.y_min + (self.get_height() / 2)
        # Return as Vector
        return Vector2(center_x, center_y)
    # Define Transformations
    def pan(self, dx: float = 0, dy: float = 0):
        # Update Data
        self.x_min += dx
        self.x_max += dx
        self.y_min += dy
        self.y_max += dy
    def scale(self, scale_factor: float = 1):
        # Compute Window point as vectors
        (center_x, center_y) = self.get_center().as_tuple()
        left_bottom = Vector2(self.x_min, self.y_min)
        right_upper = Vector2(self.x_max, self.y_max)
        # Translate into origin
        translate_origin = homo_coords2_matrix_translate(-center_x, -center_y)
        # Scale
        scale_by_factor = homo_coords2_matrix_scale(scale_factor, scale_factor)
        # Translate back
        translate_back = homo_coords2_matrix_translate(center_x, center_y)
        # Compute Transforms
        left_bottom = left_bottom.as_vec3(1) * translate_origin * scale_by_factor * translate_back
        right_upper = right_upper.as_vec3(1) * translate_origin * scale_by_factor * translate_back
        # Destructure Values
        (x_min, y_min) = left_bottom.try_into_vec2().as_tuple()
        (x_max, y_max) = right_upper.try_into_vec2().as_tuple()
        # Update Data
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
    # Define Rendering
    def draw(self, cairo: cairo.Context, inherited_transform: Matrix) -> None:
        # Draw Square
        points = [(10, 10), (100, 10), (100, 100), (10, 100), (10,10)]
        points = [Vector2.from_tuple(point).as_vec3(1) * inherited_transform for point in points]
        for i in range(len(points)):
            (x, y) = points[i].try_into_vec2().as_tuple()
            if i == 0:
                cairo.move_to(x, y)
            cairo.line_to(x, y)
        cairo.stroke()

        line = Line2D(Vector2(10, 10), Vector2(100, 100))
        line.draw(cairo, inherited_transform)
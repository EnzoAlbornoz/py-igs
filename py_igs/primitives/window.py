from __future__ import annotations
from typing import List, Tuple
import cairo
from primitives.matrix import Matrix
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
    # Define Transformations
    def pan(self, dx: float, dy: float):
        # Update Data
        self.x_min += dx
        self.x_max += dx
        self.y_min += dy
        self.y_max += dy
    def scale(self, scale_factor: float):
        # Update Data
        self.x_min *= scale_factor
        self.x_max *= scale_factor
        self.y_min *= scale_factor
        self.y_max *= scale_factor
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
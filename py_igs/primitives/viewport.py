from __future__ import annotations
import cairo
from primitives.matrix import Matrix, homo_coords2_matrix_rotate, homo_coords2_matrix_scale, homo_coords2_matrix_translate
from primitives.vec2 import Vector2
from primitives.window import Window

class Viewport:
    # Initializes the Viewport
    def __init__(self, x_viewport_min: float, y_viewport_min: float, x_viewport_max: float, y_viewport_max: float) -> None:
        # Initialize Attributes
        self.x_min = x_viewport_min
        self.y_min = y_viewport_min
        self.x_max = x_viewport_max
        self.y_max = y_viewport_max
        self.window: Window = None
    # Define Getter and Setters
    def get_window(self) -> Window:
        return self.window
    def set_window(self, window: Window) -> None:
        self.window = window

    def get_width(self) -> float:
        return self.x_max - self.x_min
    def set_width(self, width: float, coerse_window: bool = False) -> None:
        # Check Value
        if width <= 0:
            raise ValueError("The width can only be positive")
        # Try to Coerse Window
        if coerse_window:
            # Compute Scale
            window_scale = self.window.get_width() / self.get_width()
            self.window.set_width(width * window_scale)
        # Change Viewport Width
        self.x_max = self.x_min + width

    def get_height(self) -> float:
        return self.y_max - self.y_min
    def set_height(self, height: float, coerse_window: bool = False) -> None:
        # Check Value
        if height <= 0:
            raise ValueError("The height can only be positive")
        # Try to Coerse Window
        if coerse_window:
            # Compute Scale
            window_scale = self.window.get_height() / self.get_height()
            self.window.set_height(height * window_scale)
        # Change Viewport Height
        self.y_max = self.y_min + height

    def get_scale(self) -> float:
        return self.get_width() / self.window.get_width()

    def get_inverse_scale(self) -> float:
        return self.window.get_width() / self.get_width()

    # Define Basic Matrix Transformations
    def viewport_transform(self, point: Vector2) -> Vector2:
        # Destructure Point
        x_world, y_world = point.as_tuple()
        # Compute Viewport Transformation
        x_viewport = ((x_world - self.window.x_min) / (self.window.x_max - self.window.x_min)) * (self.x_max - self.x_min)
        y_viewport = (1 - ((y_world - self.window.y_min) / (self.window.y_max - self.window.y_min))) * (self.y_max - self.y_min)
        # Return as Tuple
        return (x_viewport, y_viewport)

    def as_transform(self) -> Matrix:
        # Translate into Origin
        to_origin = homo_coords2_matrix_translate(-self.window.x_min, -self.window.y_min)
        # Scale to Match Desired Size
        scale_x = (self.x_max - self.x_min) / (self.window.x_max - self.window.x_min)
        scale_y = (self.y_max - self.y_min) / (self.window.y_max - self.window.y_min)
        scale_to_viewport_size = homo_coords2_matrix_scale(scale_x , -scale_y)
        # Translate Back to Viewport
        to_viewport = homo_coords2_matrix_translate(self.x_min, self.y_max)
        # Return Composed Operation
        return to_origin * scale_to_viewport_size * to_viewport

    # Defines Draw Function
    def draw(self, cairo: cairo.Context) -> None:
        inherited_transform = self.as_transform()
        # Call Draw on Window
        self.window.draw(cairo, inherited_transform)

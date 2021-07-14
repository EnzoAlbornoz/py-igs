from __future__ import annotations
from typing import TYPE_CHECKING
import cairo
from primitives.matrix import Matrix, homo_coords2_matrix_scale, homo_coords2_matrix_translate
from primitives.window import Window
if TYPE_CHECKING:
    from primitives.display_file import DisplayFile

class Viewport:
    # Initializes the Viewport
    def __init__(self, x_viewport_min: float, y_viewport_min: float, x_viewport_max: float, y_viewport_max: float) -> None:
        # Initialize Attributes
        self.x_min = x_viewport_min
        self.y_min = y_viewport_min
        self.x_max = x_viewport_max
        self.y_max = y_viewport_max
        self.window: Window | None = None
    # Define Getter and Setters
    def get_window(self) -> Window | None:
        return self.window
    def set_window(self, window: Window) -> None:
        self.window = window

    def get_width(self) -> float:
        return self.x_max - self.x_min
    def set_width(self, width: float, coerse_window: bool = False) -> None:
        # Check Value
        if width <= 0:
            raise ValueError("The width can only be positive")
        # Check Window
        if self.window is None:
            raise RuntimeError("Window is None")
        # Try to Coerse Window
        if coerse_window:
            # Compute Scale
            window_scale = width / self.get_width()
            self.window.scale(window_scale, 1)
        # Change Viewport Width
        self.x_max = self.x_min + width

    def get_height(self) -> float:
        return self.y_max - self.y_min
    def set_height(self, height: float, coerse_window: bool = False) -> None:
        # Check Value
        if height <= 0:
            raise ValueError("The height can only be positive")
        # Check Window
        if self.window is None:
            raise RuntimeError("Window is None")
        # Try to Coerse Window
        if coerse_window:
            # Compute Scale
            window_scale = height / self.get_height()
            self.window.scale(1, window_scale)
        # Change Viewport Height
        self.y_max = self.y_min + height

    def get_scale(self) -> float:
        # Check Window
        if self.window is None:
            raise RuntimeError("Window is None")
        # Return Scale
        return self.get_width() / self.window.get_width()

    def get_inverse_scale(self) -> float:
        # Check Window
        if self.window is None:
            raise RuntimeError("Window is None")
        # Return Scale
        return self.window.get_width() / self.get_width()

    # Define Basic Matrix Transformations
    def as_transform(self) -> Matrix:
        # Check Window
        if self.window is None:
            raise RuntimeError("Window is None")
        # Translate into Origin
        to_origin = homo_coords2_matrix_translate(-self.window.x_min, -self.window.y_min)
        # Denormalize 
        # Scale to Match Desired Size
        scale_x = self.get_width() / (self.window.get_width())
        scale_y = self.get_height() / (self.window.get_height())
        scale_to_viewport_size = homo_coords2_matrix_scale(scale_x , -scale_y)
        # Translate Back to Viewport
        to_viewport = homo_coords2_matrix_translate(self.x_min, self.y_max)
        # Return Composed Operation
        return to_origin * scale_to_viewport_size * to_viewport

    def as_normalized_transform(self) -> Matrix:
        # Translate into Origin
        to_origin = homo_coords2_matrix_translate(1, 1) 
        # Scale to Match Desired Size
        scale_x = self.get_width() / 2
        scale_y = self.get_height() / 2
        scale_to_viewport_size = homo_coords2_matrix_scale(scale_x , -scale_y)
        # Translate Back to Viewport
        to_viewport = homo_coords2_matrix_translate(self.x_min, self.y_max)
        # Return Composed Operation
        return to_origin * scale_to_viewport_size * to_viewport

    # Defines Draw Function
    def draw(self, cairo: cairo.Context, display_file: DisplayFile) -> None:
        # Compute Viewport Transform for a Normalized Window
        viewport_transform = self.as_normalized_transform()
        # Check Window
        if self.window is not None:
            # Call Draw on Window
            self.window.draw(cairo, display_file, viewport_transform)

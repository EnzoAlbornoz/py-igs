from __future__ import annotations
from typing import Tuple
from primitives.matrix import Matrix
from primitives.vec3 import Vector3

class Vector2(Matrix):
    # Define Factory
    @staticmethod
    def from_tuple(tuple: Tuple[float, float]) -> Vector2:
        # Destructure Tuple
        x, y = tuple
        # Create new Vector
        return Vector2(x, y)
    # Define Constructor
    def __init__(self, x: float, y: float) -> None:
        # Call Super Constructor
        super().__init__([[x, y]])
    # Getters
    def as_tuple(self) -> Tuple[float, float]:
        # Destructure Matrix
        x, y = self.lines()[0]
        # Return as Tuple
        return (x, y)
    def get_x(self) -> float:
        # Destructure Matrix
        x = self.lines()[0][0]
        # Return value
        return x
    def get_y(self) -> float:
        # Destructure Matrix
        y = self.lines()[0][1]
        # Return value
        return y
    # Conversions
    def as_vec3(self, z: float = 0) -> Vector3:
        # Destructure Matrix
        x, y = self.as_tuple()
        # Transform into Vector
        return Vector3(x, y, z)
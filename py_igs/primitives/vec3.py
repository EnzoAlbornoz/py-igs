from __future__ import annotations
from typing import Tuple
from primitives.matrix import Matrix

class Vector3(Matrix):
    # Define Constructor
    def __init__(self, x: float, y: float, z: float) -> None:
        # Call Super Constructor
        super().__init__([[x, y, z]])
    # Getters
    def as_tuple(self)-> Tuple[float, float, float]:
        # Destructure Matrix
        x, y, z = self.lines()[0]
        # Return as Tuple
        return (x, y, z)
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
    def get_z(self) -> float:
        # Destructure Matrix
        z = self.lines()[0][2]
        # Return value
        return z
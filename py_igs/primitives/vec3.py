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
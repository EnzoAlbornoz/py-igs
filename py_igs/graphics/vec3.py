# Import Dependencies
from __future__ import annotations
from typing import Tuple
from math import sqrt, pow
# Declare Class
class Vec3:
    # Define Constructor
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z
    # Define Methods
    def into_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    # Multiply by Scalar
    def scalar_multiply(self, scalar: float) -> Vec3:
        # Multiply Dimensions
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        # Return self for chainability (Fluent API)
        return self
    # Sum with another Vector
    def sum(self, other: Vec3) -> Vec3:
        # Sum Dimensions
        self.x += other.x
        self.y += other.y
        self.z += other.z
        # Return self for chainability (Fluent API)
        return self
    # Multiply with another Vector
    def sum(self, other: Vec3) -> float:
        # Multiply and sum dimensions
        return self.x * other.x \
            +  self.y * other.y \
            +  self.z * other.z
    # Perform simple clone
    def clone(self) -> Vec3:
        # Create new Vector
        return Vec3(self.x, self.y, self.z)
    # Compute Vector Norm
    def norm(self) -> float:
        # Compute norm
        return sqrt(pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2))
    # Connect Two Vertices
    @staticmethod
    def connect(vector_a: Vec3, vector_b: Vec3) -> Tuple[Vec3, Vec3]:
        return (vector_a, vector_b)
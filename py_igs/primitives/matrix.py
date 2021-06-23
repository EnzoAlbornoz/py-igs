# Static Imports
from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple
from functools import reduce
from math import cos, sin
# Import Types
if TYPE_CHECKING:
    from primitives.vec2 import Vector2
    from primitives.vec2 import Vector3

class Matrix:
    # Define Matrix Initialization
    def __init__(self, lines: List[List[float]]) -> None:
        # Force Complete Matrices
        max_line_length = max(map(lambda line: len(line), lines))
        self.elements = [[line[i] if i < len(line) else 0.0 for i in range(max_line_length)] for line in lines]
    def dimensions(self) -> Tuple[int, int]:
        lines_n = len(self.elements)
        columns_n = len(self.elements[0])
        return (lines_n, columns_n)

    def lines(self) -> List[List[float]]:
        return self.elements
    
    def columns(self) -> List[List[float]]:
        # Fetch Dimensions
        (lines_n, columns_n) = self.dimensions()
        # Compute Column Chunks
        return [[self.elements[i][j] for i in range(lines_n)] for j in range(columns_n)]
    # Define Print Function
    def __str__(self) -> str:
        return f"Matrix: {self.elements.__str__()}"
    # Define Basic Matrix Operations
    def __add__(self, other: Matrix) -> Matrix:
        # Check Dimensions
        dim_self = self.dimensions()
        dim_other = other.dimensions()
        if dim_self != dim_other:
            raise TypeError(f"Tried to add matrix of dimensions {dim_self} to a matrix of dimensions {dim_other}")
        # Sum Operation
        new_elements = [[e1 + e2 for (e1, e2) in zip(line_self, line_other)] for (line_self, line_other) in zip(self.lines(), other.lines())]
        # Create new Matrix and return it
        return Matrix(new_elements)
    def __sub__(self, other: Matrix) -> Matrix:
        # Check Dimensions
        dim_self = self.dimensions()
        dim_other = other.dimensions()
        if dim_self != dim_other:
            raise TypeError(f"Tried to add matrix of dimensions {dim_self} to a matrix of dimensions {dim_other}")
        # Sub Operation
        new_elements = [[e1 - e2 for (e1, e2) in zip(line_self, line_other)] for (line_self, line_other) in zip(self.lines(), other.lines())]
        # Create new Matrix and return it
        return Matrix(new_elements)
    def __mul__(self, other: int | float | Matrix) -> Matrix:
        if type(other) is Matrix:
            # Check Dimensions
            (_, col_self) = self.dimensions()
            (lin_other, _) = other.dimensions()
            if (col_self != lin_other):
                raise TypeError(f"Tried to multiply a matrix of {col_self} columns with a matrix of {lin_other} lines")
            # Multiply Operation
            new_elements = [[reduce(lambda el, lc: el + (lc[0] * lc[1]), zip(line, column), 0) for column in other.columns()] for line in self.lines()]
            # Create new Matrix and return it
            return Matrix(new_elements)
        elif type(other) is int or type(other) is float:
            # Multiply Operation
            new_elements = [[(element * other) for element in line] for line in self.lines()]
            # Create new Matrix and return it
            return Matrix(new_elements)
        else:
            raise TypeError(f"Cannot multitply a matrix with {type(other)}")
    def __rmul__(self, other) -> Matrix:
        # Proxy Operation
        return self.__mul__(other)
    def as_transverse(self) -> Matrix:
        # Transverse Matrix
        new_elements = self.columns()
        # Create new Matrix and return it
        return Matrix(new_elements)
    # Define Type Coercion
    def try_into_vec2(self) -> Vector2:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 2:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Import Vector2
        from primitives.vec2 import Vector2
        # Get Values
        x, y, *_ = self.lines()[0]
        # Cast Matrix
        return Vector2(x, y)
    def try_into_vec3(self) -> Vector3:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 3:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Import Vector3
        from primitives.vec2 import Vector3
        # Get Values
        x, y, z, *_ = self.lines()[0]
        # Cast Matrix
        return Vector3(x, y, z)


# Define 2D Homogeneus Transformation Matrices
def homo_coords2_matrix_translate(dx: float, dy: float) -> Matrix:
    # Define and Return Matrix
    return Matrix([[1, 0, 0], [0, 1, 0], [dx, dy, 1]])

def homo_coords2_matrix_scale(sx: float, sy: float) -> Matrix:
    # Define and Return Matrix
    return Matrix([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])

def homo_coords2_matrix_rotate(theta: float) -> Matrix:
    # Define and Return Matrix
    return Matrix([[cos(theta), -sin(theta), 0], [sin(theta), cos(theta), 0], [0, 0, 1]])
# Static Imports
from __future__ import annotations
from itertools import chain, zip_longest
from typing import Any, Iterable, List, Tuple, TypeVar
from math import cos, sin, sqrt
from array import array, ArrayType

# Define Helper Function
T = TypeVar("T")
def chunks(iterable: Iterable[T], chunk_size: int, fillValue: T = None) -> List[List[T]]:
    return list(zip_longest(*[iter(iterable)] * chunk_size, fillvalue=fillValue))
# Define Classes
class Matrix:
    # Define Matrix Initialization
    def __init__(self, n_cols: int, elements: ArrayType[float]) -> None:
        # Force Complete Matrices
        self.n_cols = n_cols
        self.n_lines = len(elements) // n_cols
        self.elements = elements

    @staticmethod
    def from_list(elements: List[List[float]]) -> Matrix:
        # Define number of columns
        n_cols = len(elements[0])
        new_elements = array("d", chain.from_iterable(elements))
        # Return Matrix
        return Matrix(n_cols, new_elements)

    def dimensions(self) -> Tuple[int, int]:
        return (self.n_lines, self.n_cols)

    def lines(self) -> List[List[float]]:
        return chunks(self.elements.tolist(), self.n_cols, 0)
    
    def columns(self) -> List[List[float]]:
        # Fetch Dimensions
        (lines_n, columns_n) = self.dimensions()
        # Compute Column Chunks
        return [[self.elements[i * columns_n + j] for i in range(lines_n)] for j in range(columns_n)]
    # Define Print Function
    def __str__(self) -> str:
        return f"Matrix: {self.elements.__str__()}"
    def __repr__(self) -> str:
        repr = "Matrix:\n"
        repr += "\n".join(["\t"+ "[" + "\t".join(["{:.6f}".format(el) for el in line]) + "]" for line in self.lines()])
        return repr
    # Define Basic Matrix Operations
    def __add__(self, other: Matrix) -> Matrix:
        # Check Dimensions
        dim_self = self.dimensions()
        dim_other = other.dimensions()
        if dim_self != dim_other:
            raise TypeError(f"Tried to add matrix of dimensions {dim_self} to a matrix of dimensions {dim_other}")
        # Alloc new Matrix
        new_elements = array("d", self.elements)
        # Sum Operation
        for (idx, other_el) in enumerate(other.elements):
            new_elements[idx] += other_el
        # Create new Matrix and return it
        return Matrix(self.n_cols, new_elements)
    def __sub__(self, other: Matrix) -> Matrix:
        # Check Dimensions
        dim_self = self.dimensions()
        dim_other = other.dimensions()
        if dim_self != dim_other:
            raise TypeError(f"Tried to subtract matrix of dimensions {dim_self} to a matrix of dimensions {dim_other}")
        # Alloc new Matrix
        new_elements = array("d", self.elements)
        # Sum Operation
        for (idx, other_el) in enumerate(other.elements):
            new_elements[idx] -= other_el
        # Create new Matrix and return it
        return Matrix(self.n_cols, new_elements)

    def __mul__(self, other: int | float | Matrix) -> Matrix:
        if type(other) is Matrix:
            # Check Dimensions
            (final_lines, col_self) = self.dimensions()
            (lin_other, final_cols) = other.dimensions()
            if (col_self != lin_other):
                raise TypeError(f"Tried to multiply a matrix of {col_self} columns with a matrix of {lin_other} lines")
            # Alloc Matrix
            new_elements = array("d", [0] * (final_lines * final_cols))
            # Multiply Operation
            for i in range(final_lines):
                for j in range(final_cols):
                    for k in range(col_self):
                        new_elements[j + i * final_cols] += self.elements[k + i * col_self] * other.elements[j + k * final_cols]
            # Create new Matrix and return it
            return Matrix(final_cols, new_elements)
        elif type(other) is int or type(other) is float:
            # Alloc Matrix
            new_elements = array("d", self.elements)
            # Multiply Operation
            for i in range(len(new_elements)):
                new_elements[i] *= other
            # Create new Matrix and return it
            return Matrix(self.n_cols, new_elements)
        else:
            raise TypeError(f"Cannot multitply a matrix with {type(other)}")
    def __rmul__(self, other: Any) -> Matrix:
        # Proxy Operation
        return self.__mul__(other)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Matrix):
            return all(all(el_s == el_o for (el_s, el_o) in zip(ls,lo)) for (ls, lo) in zip(self.lines(), other.lines()))
        else:
            return False

    def as_transverse(self) -> Matrix:
        # Alloc new Array
        new_elements = array("d", self.elements)
        # Transverse Matrix
        for n in range(self.n_cols * self.n_lines):
            i = n // self.n_lines
            j = n % self.n_lines
            new_elements[n] = self.elements[self.n_cols * j + i]
        # Create new Matrix and return it
        return Matrix(self.n_lines, new_elements)
    # Define Type Coercion
    def try_into_vec2(self) -> Vector2:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 2:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Get Values
        x, y, *_ = self.lines()[0]
        # Cast Matrix
        return Vector2(x, y)
    def try_into_vec3(self) -> Vector3:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 3:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Get Values
        x, y, z, *_ = self.lines()[0]
        # Cast Matrix
        return Vector3(x, y, z)

# Define Fixed Size Matrices
class Vector2(Matrix):
    # Define Factory
    @staticmethod
    def from_tuple(tuple: Tuple[float, float]) -> Vector2:
        # Destructure Tuple
        x, y = tuple
        # Create new Vector
        return Vector2(x, y)
    # Define String
    def __str__(self) -> str:
        return f"Vector2: [{self.elements[0]}, {self.elements[1]}]"
    # Define Constructor
    def __init__(self, x: float, y: float) -> None:
        # Call Super Constructor
        super().__init__(2, array("d", [x, y]))
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
    def dot_product(self, other: Vector2) -> float:
        # Destructure Values
        (x1, y1) = self.as_tuple()
        (x2, y2) = other.as_tuple()
        # Make OP
        return (x1 * x2) + (y1 * y2)
    # Conversions
    def as_vec3(self, z: float = 0) -> Vector3:
        # Destructure Matrix
        x, y = self.as_tuple()
        # Transform into Vector
        return Vector3(x, y, z)
    def modulo(self) -> float:
        return sqrt(sum(el**2 for el in self.lines()[0]))

class Vector3(Matrix):
    # Define Constructor
    def __init__(self, x: float, y: float, z: float) -> None:
        # Call Super Constructor
        super().__init__(3, array("d", [x, y, z]))
    # Define String
    def __str__(self) -> str:
        return f"Vector2: [{self.elements[0]}, {self.elements[1]}, {self.elements[2]}]"
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
    def dot_product(self, other: Vector3) -> float:
        # Destructure Values
        (x1, y1, z1) = self.as_tuple()
        (x2, y2, z2) = other.as_tuple()
        # Make OP
        return (x1 * x2) + (y1 * y2) + (z1 * z2)
    def modulo(self) -> float:
        return sqrt(sum(el**2 for el in self.lines()[0]))


# Define Matrices Helpers
def gen_identity_matrix(size: int) -> Matrix:
    # Define and Return Matrix
    return Matrix(size, array("d", [1.0 if ((i % (size + 1)) == 0) else 0.0 for i in range(size**2)]))

# Define 2D Homogeneus Transformation Matrices
def homo_coords2_matrix_identity() -> Matrix:
    return gen_identity_matrix(3)

def homo_coords2_matrix_translate(dx: float, dy: float) -> Matrix:
    # Define and Return Matrix
    return Matrix(3, array("d", [1., 0., 0., 0., 1., 0., dx, dy, 1.]))

def homo_coords2_matrix_scale(sx: float, sy: float) -> Matrix:
    # Define and Return Matrix
    return Matrix(3, array("d",[sx, 0., 0., 0., sy, 0., 0., 0., 1.]))

def homo_coords2_matrix_rotate(theta: float) -> Matrix:
    # Define and Return Matrix
    return Matrix(3, array("d", [cos(theta), sin(theta), 0., -sin(theta), cos(theta), 0., 0., 0., 1.]))
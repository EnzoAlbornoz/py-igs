# Static Imports
from __future__ import annotations
from itertools import zip_longest
from typing import Any, Iterable, List, Tuple, TypeVar
from math import cos, sin, sqrt
# from array import array, ArrayType


# Use Numpy + Numba to Speed Up Calculations ===================================
from numba import jit #type: ignore
from numpy import arccos, float64, array, identity
from numpy.linalg import inv, multi_dot
from numpy.typing import NDArray

@jit(nopython=True, nogil=True, cache=True, fastmath=True) #type: ignore
def __matrix_multiply__(matrixA: NDArray[float64], matrixB: NDArray[float64]) -> NDArray[float64]:
    return matrixA @ matrixB

@jit(nopython=True, nogil=True, cache=True, fastmath=True) #type: ignore
def __matrix_scale__(matrixA: NDArray[float64], scalar: float64) -> NDArray[float64]:
    return matrixA * scalar

@jit(nopython=True, nogil=True, cache=True, fastmath=True) #type: ignore
def __matrix_sum__(matrixA: NDArray[float64], matrixB: NDArray[float64]) -> NDArray[float64]:
    return matrixA + matrixB

@jit(nopython=True, nogil=True, cache=True, fastmath=True) #type: ignore
def __matrix_sub__(matrixA: NDArray[float64], matrixB: NDArray[float64]) -> NDArray[float64]:
    return matrixA - matrixB
# ==============================================================================
# Define Helper Function
T = TypeVar("T")
def chunks(iterable: Iterable[T], chunk_size: int, fillValue: T = None) -> List[List[T]]:
    return list(zip_longest(*[iter(iterable)] * chunk_size, fillvalue=fillValue))
# Define Classes
class Matrix:
    # Define Matrix Initialization
    def __init__(self, elements: NDArray[float64]) -> None:
        # Force Complete Matrices
        self.elements = elements

    @staticmethod
    def from_list(elements: List[List[float]]) -> Matrix:
        # Define number of columns
        new_elements: NDArray[float64] = array(elements, dtype=float64)
        # Return Matrix
        return Matrix(new_elements)

    def dimensions(self) -> Tuple[int, int]:
        # Get Shape
        (nlines, ncols) = tuple(self.elements.shape)
        return (nlines, ncols)

    def lines(self) -> List[List[float]]:
        return self.elements.tolist()
    
    def columns(self) -> List[List[float]]:
        # Compute Column Chunks
        return self.elements.transpose().tolist()
    # Define Print Function
    def __str__(self) -> str:
        return f"Matrix: {self.elements.__str__()}"
    def __repr__(self) -> str:
        repr = "Matrix:\n"
        repr += "\n".join(["\t"+ "[" + "\t".join(["{:.6f}".format(el) for el in line]) + "]" for line in self.lines()])
        return repr
    # Define Basic Matrix Operations
    def __add__(self, other: Matrix) -> Matrix:
        # Create new Matrix and return it
        return Matrix(__matrix_sum__(self.elements, other.elements))
    def __sub__(self, other: Matrix) -> Matrix:
        # Create new Matrix and return it
        return Matrix(__matrix_sub__(self.elements, other.elements))

    def __mul__(self, other: int | float | Matrix) -> Matrix:
        if isinstance(other, Matrix):
            # Create new Matrix and return it
            return Matrix(__matrix_multiply__(self.elements, other.elements))
        elif type(other) is float or type(other) is int:
            # Create new Matrix and return it
            return Matrix(__matrix_scale__(self.elements, float64(float(other))))
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

    def as_inverse(self) -> Matrix:
        data: NDArray[float64] = inv(self.elements)
        return Matrix(data)

    def as_transposed(self) -> Matrix:
        # Create new Matrix and return it
        return Matrix(self.elements.transpose())
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
    def try_into_vec2_homo(self) -> Vector2:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 3:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Get Values
        x, y, z, *_ = self.lines()[0]
        # Cast Matrix
        return Vector2(x/z, y/z)
    def try_into_vec3(self) -> Vector3:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 3:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Get Values
        x, y, z, *_ = self.lines()[0]
        # Cast Matrix
        return Vector3(x, y, z)
    def try_into_vec3_homo(self) -> Vector3:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 4:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Get Values
        x, y, z, w, *_ = self.lines()[0]
        # Cast Matrix
        return Vector3(x/w, y/w, z/w)
    def try_into_vec4(self) -> Vector4:
        # Check Dimensions
        (lines_n, columns_n) = self.dimensions()
        if lines_n != 1 or columns_n < 4:
            raise ValueError(f"Cannot cast {self} as a Vector2")
        # Get Values
        x, y, z, w, *_ = self.lines()[0]
        # Cast Matrix
        return Vector4(x, y, z, w)

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
        return f"Vector2: [{self.elements[0,0]}, {self.elements[0,1]}]"
    # Define Constructor
    def __init__(self, x: float, y: float) -> None:
        # Call Super Constructor
        elements: NDArray[float64] = array([[x, y]], dtype=float64)
        super().__init__(elements)
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
    def as_vec4(self, z: float = 0, w: float = 0) -> Vector4:
        # Destructure Matrix
        x, y = self.as_tuple()
        # Transform into Vector
        return Vector4(x, y, z, w)
    def modulo(self) -> float:
        return sqrt(sum(el**2 for el in self.lines()[0]))

class Vector3(Matrix):
    # Define Constructor
    def __init__(self, x: float, y: float, z: float) -> None:
        # Call Super Constructor
        elements: NDArray[float64] = array([[x, y, z]], dtype=float64)
        super().__init__(elements)
    # Define String
    def __str__(self) -> str:
        return f"Vector3: [{self.elements[0,0]}, {self.elements[0,1]}, {self.elements[0,2]}]"
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
    def as_vec4(self, w: float = 0) -> Vector4:
        # Destructure Matrix
        x, y, z = self.as_tuple()
        # Transform into Vector
        return Vector4(x, y, z, w)
    def modulo(self) -> float:
        return sqrt(sum(el**2 for el in self.lines()[0]))

class Vector4(Matrix):
    # Define Constructor
    def __init__(self, x: float, y: float, z: float, w: float) -> None:
        # Call Super Constructor
        elements: NDArray[float64] = array([[x, y, z, w]], dtype=float64)
        super().__init__(elements)
    # Define String
    def __str__(self) -> str:
        return f"Vector4: [{self.elements[0,0]}, {self.elements[0,1]}, {self.elements[0,2]}, {self.elements[0,3]}]"
    # Getters
    def as_tuple(self)-> Tuple[float, float, float, float]:
        # Destructure Matrix
        x, y, z, w = self.lines()[0]
        # Return as Tuple
        return (x, y, z, w)
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
    def get_w(self) -> float:
        # Destructure Matrix
        w = self.lines()[0][2]
        # Return value
        return w
    def dot_product(self, other: Vector4) -> float:
        # Destructure Values
        (x1, y1, z1, w1) = self.as_tuple()
        (x2, y2, z2, w2) = other.as_tuple()
        # Make OP
        return (x1 * x2) + (y1 * y2) + (z1 * z2) + (w1 * w2)
    def modulo(self) -> float:
        return sqrt(sum(el**2 for el in self.lines()[0]))


# Define Matrices Helpers
def gen_identity_matrix(size: int) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = identity(size, dtype=float64)
    return Matrix(elements)

# Define 2D Homogeneus Transformation Matrices
def homo_coords2_matrix_identity() -> Matrix:
    return gen_identity_matrix(3)

def homo_coords2_matrix_translate(dx: float, dy: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([[1, 0, 0], [0, 1, 0], [dx, dy, 1]], dtype=float64)
    return Matrix(elements)

def homo_coords2_matrix_scale(sx: float, sy: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], dtype=float64)
    return Matrix(elements)

def homo_coords2_matrix_rotate(theta: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([[cos(theta), sin(theta), 0], [-sin(theta), cos(theta), 0], [0, 0, 1]])
    return Matrix(elements) 

# Define 3D Homogeneus Transformation Matrices
def homo_coords3_matrix_identity() -> Matrix:
    return gen_identity_matrix(4)


def homo_coords3_matrix_translate(dx: float, dy: float, dz: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [dx, dy, dz, 1]], dtype=float64)
    return Matrix(elements)

def homo_coords3_matrix_scale(sx: float, sy: float, sz: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]], dtype=float64)
    return Matrix(elements)

def homo_coords3_matrix_rotate_x(theta: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([
        [1,          0,          0, 0],
        [0, cos(theta), sin(theta), 0],
        [0,-sin(theta), cos(theta), 0],
        [0,          0,          0, 1]
    ])
    return Matrix(elements) 

def homo_coords3_matrix_rotate_y(theta: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([
        [ cos(theta), 0,-sin(theta), 0],
        [          0, 1,          0, 0],
        [ sin(theta), 0, cos(theta), 0],
        [          0, 0,          0, 1]
    ])
    return Matrix(elements) 

def homo_coords3_matrix_rotate_z(theta: float) -> Matrix:
    # Define and Return Matrix
    elements: NDArray[float64] = array([
        [ cos(theta), sin(theta), 0, 0],
        [-sin(theta), cos(theta), 0, 0],
        [          0,          0, 1, 0],
        [          0,          0, 0, 1]
    ])
    return Matrix(elements) 

def homo_coords3_matrix_rotate_xyz(theta_x: float, theta_y: float, theta_z: float) -> Matrix:
    # Define and Return Matrix
    rotate_x: NDArray[float64] = array([
        [1,            0,            0, 0],
        [0, cos(theta_x), sin(theta_x), 0],
        [0,-sin(theta_x), cos(theta_x), 0],
        [0,            0,            0, 1]
    ])
    rotate_y: NDArray[float64] = array([
        [ cos(theta_y), 0,-sin(theta_y), 0],
        [            0, 1,            0, 0],
        [ sin(theta_y), 0, cos(theta_y), 0],
        [            0, 0,            0, 1]
    ])
    rotate_z: NDArray[float64] = array([
        [ cos(theta_z), sin(theta_z), 0, 0],
        [-sin(theta_z), cos(theta_z), 0, 0],
        [          0,          0, 1, 0],
        [          0,          0, 0, 1]
    ])
    # Multiply
    rotation: NDArray[float64] = multi_dot([rotate_x, rotate_y, rotate_z])
    return Matrix(rotation)

def angle_between_vectors(vector_a: Vector3, vector_b: Vector3) -> float:
    return arccos(vector_a.dot_product(vector_b) / (vector_a.modulo() * vector_b.modulo()))
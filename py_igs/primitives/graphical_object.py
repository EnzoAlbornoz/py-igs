from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from cairo import Context, Matrix

class GraphicalObject(ABC):
    # Define Interface
    def draw(self, cairo: Context, inherited_matrix: Matrix):
        raise NotImplementedError("GraphicalObject is an abstract class.")
    def transform(self, transformation: Matrix):
        raise NotImplementedError("GraphicalObject is an abstract class.")
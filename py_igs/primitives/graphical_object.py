from __future__ import annotations
from cairo import Matrix
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from objects.object_type import ObjectType
if TYPE_CHECKING:
    from cairo import Context

class GraphicalObject(ABC):
    # Define Interface
    @abstractmethod
    def get_type() -> ObjectType:
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def draw(self, cairo: Context, inherited_matrix: Matrix):
        raise NotImplementedError("GraphicalObject is an abstract class.")
    @abstractmethod
    def transform(self, transformation: Matrix):
        raise NotImplementedError("GraphicalObject is an abstract class.")
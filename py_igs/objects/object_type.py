from __future__ import annotations
from enum import Enum, unique, auto

@unique
class ObjectType(Enum):
    # Define Enum Values
    POINT_2D = auto()
    LINE_2D = auto()
    WIREFRAME_2D = auto()
    # Handle Print
    def __str__(self) -> str:
        if self is ObjectType.POINT_2D:
            return "POINT_2D"
        elif self is ObjectType.LINE_2D:
            return "LINE_2D"
        elif self is ObjectType.WIREFRAME_2D:
            return "WIREFRAME_2D"
        else:
            raise ValueError("Invalid Type")
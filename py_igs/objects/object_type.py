from __future__ import annotations
from enum import IntEnum, unique

@unique
class ObjectType(IntEnum):
    # Define Enum Values
    POINT_2D = 1
    LINE_2D = 2
    WIREFRAME_2D = 3
    BEZIER_2D = 4
    BSPLINE_2D = 5
    POINT_3D = 6
    LINE_3D = 7
    WIREFRAME_3D = 8
    OBJECT_2D = 9
    OBJECT_3D = 10
    BEZIER_3D = 11
    # Handle Print
    def __str__(self) -> str:
        if self is ObjectType.POINT_2D:
            return "POINT_2D"
        elif self is ObjectType.LINE_2D:
            return "LINE_2D"
        elif self is ObjectType.WIREFRAME_2D:
            return "WIREFRAME_2D"
        elif self is ObjectType.BEZIER_2D:
            return "BEZIER_2D"
        elif self is ObjectType.BSPLINE_2D:
            return "BSPLINE_2D"
        elif self is ObjectType.POINT_3D:
            return "POINT_3D"
        elif self is ObjectType.LINE_3D:
            return "LINE_3D"
        elif self is ObjectType.WIREFRAME_3D:
            return "WIREFRAME_3D"
        elif self is ObjectType.OBJECT_2D:
            return "OBJECT_2D"
        elif self is ObjectType.OBJECT_3D:
            return "OBJECT_3D"
        elif self is ObjectType.BEZIER_3D:
            return "BEZIER_3D"
        else:
            raise ValueError("Invalid Type")
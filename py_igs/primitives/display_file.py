from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING, Tuple

from math import radians
from primitives.matrix import homo_coords2_matrix_identity, homo_coords2_matrix_rotate, homo_coords2_matrix_scale, homo_coords2_matrix_translate
from primitives.vec2 import Vector2
if TYPE_CHECKING:
    from primitives.matrix import Matrix
    from primitives.graphical_object import GraphicalObject
    from objects.object_type import ObjectType
class DisplayFile:
    # Define Initialization
    def __init__(self, objects: List[Tuple[str, ObjectType, GraphicalObject]] = []) -> None:
        # Define Attributes
        self.objects: Dict[str, Tuple[ObjectType, GraphicalObject]] = {}
        for (object_name, object_type, object_ref) in objects:
            self.objects[object_name] = (object_type, object_ref)
    # Define Methods
    def get_names(self) -> List[str]:
        # Destructure List
        return self.objects.keys()

    def get_objects(self) -> List[Tuple[str, ObjectType, GraphicalObject]]:
        return [(object_name, object_type, object_ref) for (object_name, (object_type, object_ref)) in self.objects.items()]

    def get_drawable_objects(self) -> List[GraphicalObject]:
        # Destructure List
        return [object_ref for (_object_type, object_ref) in self.objects.values()]
    
    def add_object(self, object_name: str, object_graphics: GraphicalObject) -> None:
        # Check if already exists
        if object_name not in self.get_names():
            # Define Object To Store
            self.objects[object_name] = (object_graphics.get_type(), object_graphics)
        else:
            raise ValueError("Name already in display file")

    def get_object(self, object_name):
        # Get Data
        (object_type, object_ref) = self.objects[object_name]
        # Return Full "Row"
        return (object_name, object_type, object_ref)

    def get_object_ref(self, object_name):
        # Get Data
        (_object_type, object_ref) = self.objects[object_name]
        # Return Full "Row"
        return object_ref

    def remove_object(self, object_name: str) -> None:
        # Delete By Name
        self.objects.pop(object_name)
    
    def transform_object(
        self, object_name: str,
        translate_x: float, translate_y: float,
        rotation_dg: float, rotation_point_x: float, rotation_point_y: float,
        scale_perc_x: float, scale_perc_y: float
    ):
        # Create Transformation Matrix
        transform_matrix = homo_coords2_matrix_identity()
        #  Check Rotation
        if rotation_dg != 0:
            rotation_radians = radians(rotation_dg)
            # Compute Rotation
            rotation_matrix = homo_coords2_matrix_translate(-rotation_point_x, -rotation_point_y)
            rotation_matrix *= homo_coords2_matrix_rotate(rotation_radians)
            rotation_matrix *= homo_coords2_matrix_translate(rotation_point_x, rotation_point_y)
            # Apply Rotation
            transform_matrix *= rotation_matrix
        # Check Scaling
        if scale_perc_x != 0 or scale_perc_y != 0:
            (point_x, point_y) = self.get_object_ref(object_name).get_center_coords().as_tuple()
            # Compute Scaling
            scale_x = 1 + (scale_perc_x / 100)
            scale_y = 1 + (scale_perc_y / 100)
            scaling_matrix = homo_coords2_matrix_translate(-point_x, -point_y)
            scaling_matrix *= homo_coords2_matrix_scale(scale_x, scale_y)
            scaling_matrix *= homo_coords2_matrix_translate(point_x, point_y)
            # Apply Scaling
            transform_matrix *= scaling_matrix
         #  Check Translate
        if translate_x != 0 or translate_y != 0:
            transform_matrix *= homo_coords2_matrix_translate(translate_x, translate_y)
        # Apply Transformation
        self.get_object_ref(object_name).transform(transform_matrix)
            
from __future__ import annotations
from typing import List, TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from primitives.matrix import Matrix
    from primitives.graphical_object import GraphicalObject
    from objects.object_type import ObjectType
class DisplayFile:
    # Define Initialization
    def __init__(self, objects: List[Tuple[str, ObjectType, GraphicalObject]] = []) -> None:
        # Define Attributes
        self.objects = objects
    # Define Methods
    def get_names(self) -> List[str]:
        # Destructure List
        return [object_name for (object_name, _object_type, _object_graphics) in self.objects]

    def get_objects(self) -> List[Tuple[str, ObjectType, GraphicalObject]]:
        return self.objects

    def get_drawable_objects(self) -> List[GraphicalObject]:
        # Destructure List
        return [object_graphics for (_object_name, _object_type, object_graphics) in self.objects]
    
    def add_object(self, object_name: str, object_graphics: GraphicalObject) -> None:
        # Check if already exists
        if object_name not in self.get_names():
            # Define Object To Store
            object_to_include = (object_name, object_graphics.get_type(), object_graphics)
            self.objects.append(object_to_include)
        else:
            raise ValueError("Name already in display file")

    def remove_object(self, object_name: str) -> None:
        # Filter By Name
        self.objects = list(filter(lambda object: object[0] != object_name, self.objects))
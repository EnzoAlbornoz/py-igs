from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING, Tuple
# from objects.bezier_2d import Bezier2D
# from objects.line_3d import Line3D
from objects.object_3d import Object3D
from objects.wireframe_3d import Wireframe3D
from primitives.matrix import Matrix, Vector3
if TYPE_CHECKING:
    from primitives.graphical_object import GraphicalObject
    from objects.object_type import ObjectType
class DisplayFile:
    # Define Initialization
    def __init__(self, objects: List[Tuple[str, ObjectType, GraphicalObject]] = []) -> None:
        # Define Attributes
        self.objects: Dict[str, Tuple[ObjectType, GraphicalObject]] = {}
        for (object_name, object_type, object_ref) in objects:
            self.objects[object_name] = (object_type, object_ref)
        # self.add_object("test", Wireframe3D(Vector3(0,0,0), Vector3(50, 100,0), Vector3(100, 100,0), Vector3(150, 0,0)))
        # self.add_object("test2", Bezier2D(0.01, Vector2(0,0), Vector2(50, 100), Vector2(100, 100), Vector2(150, 0), Vector2(300, 300)))
        # self.add_object("testl", Line3D(Vector3(0,0, 0), Vector3(100,100, 0)))
        self.add_object("test3", Object3D(
            Wireframe3D(Vector3(0, 0, 0), Vector3(0,100, 0), Vector3(100, 100, 0), Vector3(100, 0, 0)),
            Wireframe3D(Vector3(0, 0, 100), Vector3(0,100, 100), Vector3(100, 100, 100), Vector3(100, 0, 100)),
            Wireframe3D(Vector3(0, 0, 0), Vector3(0,  0, 100), Vector3(0, 100, 100), Vector3(0, 100, 0)),
            Wireframe3D(Vector3(100, 0, 0), Vector3(100,  0, 100), Vector3(100, 100, 100), Vector3(100, 100, 0)),
            Wireframe3D(Vector3(0, 100, 0), Vector3(100, 100, 0), Vector3(100, 100, 100), Vector3(0, 100, 100)),
            Wireframe3D(Vector3(0, 0, 0), Vector3(100, 0, 0), Vector3(100, 0, 100), Vector3(0, 0, 100))
        ))
    # Define Methods
    def get_names(self) -> List[str]:
        # Destructure List
        return list(self.objects.keys())

    def get_objects(self) -> List[Tuple[str, ObjectType, GraphicalObject]]:
        return [(object_name, object_type, object_ref) for (object_name, (object_type, object_ref)) in self.objects.items()]

    def get_drawable_objects(self) -> List[GraphicalObject]:
        # Destructure List
        return [object_ref for (_, object_ref) in self.objects.values()]
    
    def add_object(self, object_name: str, object_graphics: GraphicalObject) -> None:
        # Check if already exists
        if object_name not in self.get_names():
            # Define Object To Store
            self.objects[object_name] = (object_graphics.get_type(), object_graphics)
        else:
            raise ValueError("Name already in display file")

    def get_object(self, object_name: str):
        # Get Data
        (object_type, object_ref) = self.objects[object_name]
        # Return Full "Row"
        return (object_name, object_type, object_ref)

    def get_object_ref(self, object_name: str):
        # Get Data
        (_, object_ref) = self.objects[object_name]
        # Return Full "Row"
        return object_ref

    def remove_object(self, object_name: str) -> None:
        # Delete By Name
        self.objects.pop(object_name)
    
    def clear(self) -> None:
        # Delete All
        self.objects.clear()

    def transform_object_matrix(self, object_name: str, transformation: Matrix):
        # Initialize Pipeline for Object
        self.get_object_ref(object_name).pipeline()
        # Apply Transformation
        self.get_object_ref(object_name).transform(transformation)
        # Persist Transform
        self.get_object_ref(object_name).pipeline_apply()
            
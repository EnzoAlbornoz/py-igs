# Import Dependencies
from typing import List, cast
from objects.object_2d import Object2D
from objects.object_type import ObjectType
from objects.wireframe_2d import Wireframe2D
from objects.wireframe_3d import Wireframe3D
from primitives.graphical_object import Graphical3DObject, GraphicalObject
from primitives.matrix import Matrix, Vector3
# Define Class
class Object3D(Graphical3DObject):
    # Define Constructor
    def __init__(self, *wireframes: Wireframe3D) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.wireframes = list(wireframes)
        # Define Fill Options
        self.filled = False
    def __str__(self) -> str:
        desc = "Wireframe3D\n"
        for wireframe in self.wireframes:
            desc += "\t" + wireframe.__str__() + "\n"
        return desc
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.OBJECT_3D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline wireframes
        for wireframe in self.wireframes:
            wireframe.pipeline()
    def pipeline_apply(self):
        for wireframe in self.wireframes:
            wireframe.pipeline_apply()
    def pipeline_abort(self):
        for wireframe in self.wireframes:
            wireframe.pipeline_abort()
    # Filled Methods
    def set_filled(self, fill: bool) -> None:
        for wireframe in self.wireframes:
            wireframe.set_filled(fill)
    # Define Methods    
    def project(self, projection_matrix: Matrix) -> GraphicalObject:
        # Project Object
        wireframes = cast(List[Wireframe2D], [wireframe.project(projection_matrix) for wireframe in self.wireframes])
        object_2d = Object2D(*wireframes)
        object_2d.pipeline()
        # Return Projected Object
        return object_2d

    def transform(self, transformation: Matrix):
        # Transform wireframes
        for wireframe in self.wireframes:
            wireframe.transform(transformation)
        # Return Chain
        return self

    def get_center_coords3(self) -> Vector3:
        # Get wireframes
        wireframes_center_coords = [wireframe.get_center_coords3() for wireframe in self.wireframes]
        wireframes_center = sum(wireframes_center_coords, Vector3(0, 0, 0))
        # Compute Average
        return (wireframes_center * (1 / len(wireframes_center_coords))).try_into_vec3()
from __future__ import annotations
from objects.object_type import ObjectType
from primitives.graphical_object import Graphical3DObject, GraphicalObject
from primitives.matrix import Matrix, Vector3
from objects.wireframe_2d import Wireframe2D

class Wireframe3D(Graphical3DObject):
    # Define Constructor
    def __init__(self, *points: Vector3) -> None:
        # Call Super Constructor
        super().__init__()
        # Check Points Length
        if len(points) < 3:
            raise ValueError("Wireframe3D need 3 or more points to be defined")
        # Define Attributes
        self.points = list(points)
        # Define Pipeline Attributes
        self.pipeline_points = list(points)
        # Define Fill Options
        self.filled = False
    def __str__(self) -> str:
        desc = "Wireframe3D\n"
        for point in (self.pipeline_points if self.in_pipeline else self.points):
            desc += "\t" + point.__str__() + "\n"
        return desc
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.WIREFRAME_3D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_points = list(self.points)
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.points = list(self.pipeline_points)
            # Call Super
        super().pipeline_apply()
    # Filled Methods
    def set_filled(self, fill: bool) -> None:
        self.filled = fill
    # Define Methods    
    def project(self, projection_matrix: Matrix) -> GraphicalObject:
        # Get Points
        points = self.pipeline_points if self.in_pipeline else self.points
        # Project Points
        points = [(point.as_vec4(1) * projection_matrix).try_into_vec2() for point in points]
        # Return new Wireframe
        wireframe = Wireframe2D(*points, color=self.color, filled=self.filled)
        return wireframe

    def transform(self, transformation: Matrix):
        # Transform points
        if self.in_pipeline:
            # Pipeline
            self.pipeline_points = [
                (point.as_vec4(1) * transformation).try_into_vec3()
                for point in self.pipeline_points
            ]
        else:
            # Raw Transform
            self.points = [
                (point.as_vec4(1) * transformation).try_into_vec3()
                for point in self.points
            ]
        # Return Chain
        return self

    def get_center_coords3(self) -> Vector3:
        # Get Points
        points = self.pipeline_points if self.in_pipeline else self.points
        # Get Avg Point
        points_len_mult = 1 / len(points)
        avg_coords = Vector3(0, 0, 0)
        for point in points:
            avg_coords += point
        avg_coords *= points_len_mult
        return avg_coords.try_into_vec3()
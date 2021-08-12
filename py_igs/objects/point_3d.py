from __future__ import annotations
from typing import TYPE_CHECKING
from objects.object_type import ObjectType
from primitives.graphical_object import Graphical3DObject, GraphicalObject
from objects.point_2d import Point2D

if TYPE_CHECKING:
    from primitives.matrix import Matrix, Vector3

class Point3D(Graphical3DObject):
    # Define Constructor
    def __init__(self, point: Vector3) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.point = point
        # Define Pipeline Attributes
        self.pipeline_point = point
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.POINT_3D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_point = self.point
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.point = self.pipeline_point
            # Call Super
            super().pipeline_apply()
    # Define Methods    
    def project(self, projection_matrix: Matrix) -> GraphicalObject:
        point = self.pipeline_point if self.in_pipeline else self.point
        return Point2D((point.as_vec4(1) * projection_matrix).try_into_vec2())

    def transform(self, transformation: Matrix):
        # Transform Point
        if self.in_pipeline:
            # Pipelines
            self.pipeline_point = (self.pipeline_point.as_vec4(1) * transformation).try_into_vec3()
        else:
            # Raw Transform
            self.point = (self.point.as_vec4(1) * transformation).try_into_vec3()
        # Return Chain
        return self

    def get_center_coords3(self) -> Vector3:
        return self.point
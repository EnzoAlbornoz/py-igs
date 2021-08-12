from __future__ import annotations
from typing import TYPE_CHECKING
from primitives.graphical_object import Graphical3DObject, GraphicalObject
from objects.object_type import ObjectType
from objects.line_2d import Line2D
from primitives.matrix import Vector3
if TYPE_CHECKING:
    from primitives.matrix import Matrix

class Line3D(Graphical3DObject):
    # Define Constructor
    def __init__(self, point_a: Vector3, point_b: Vector3) -> None:
        # Call Super Constructor
        super().__init__()
        # Define Attributes
        self.point_a = point_a
        self.point_b = point_b
        # Define Pipeline Attributes
        self.pipeline_point_a = point_a
        self.pipeline_point_b = point_b
    def __str__(self) -> str:
        if self.in_pipeline:
            return f"[({self.pipeline_point_a.get_x()}, {self.pipeline_point_a.get_y()}, {self.pipeline_point_a.get_z()}), ({self.pipeline_point_b.get_x()}, {self.pipeline_point_b.get_y()}, {self.pipeline_point_b.get_z()})]"
        else:
            return f"[({self.point_a.get_x()}, {self.point_a.get_y()}, {self.point_a.get_z()}), ({self.point_b.get_x()}, {self.point_b.get_y()}, {self.point_b.get_z()})]"
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.LINE_3D
    # Define Pipeline Methods
    def pipeline(self):
        # Reset Pipeline Points
        self.pipeline_point_a = self.point_a
        self.pipeline_point_b = self.point_b
        # Call Super
        super().pipeline()
    def pipeline_apply(self):
        if self.in_pipeline:
            # Persist Pipeline Points
            self.point_a = self.pipeline_point_a
            self.point_b = self.pipeline_point_b
            # Call Super
            super().pipeline_apply()
    # Define Methods    
    def project(self, projection_matrix: Matrix) -> GraphicalObject:
        # Get Points
        point_a = self.pipeline_point_a if self.in_pipeline else self.point_a
        point_b = self.pipeline_point_b if self.in_pipeline else self.point_b
        # Transform
        point_a = (point_a.as_vec4(1) * projection_matrix).try_into_vec2()
        point_b = (point_b.as_vec4(1) * projection_matrix).try_into_vec2()
        # Create New Object
        return Line2D(point_a, point_b)

    def transform(self, transformation: Matrix):
        # Transform Points
        if self.in_pipeline:
            # Pipelines
            self.pipeline_point_a = (self.pipeline_point_a.as_vec4(1) * transformation).try_into_vec3()
            self.pipeline_point_b = (self.pipeline_point_b.as_vec4(1) * transformation).try_into_vec3()
        else:
            # Raw Transform
            self.point_a = (self.point_a.as_vec4(1) * transformation).try_into_vec3()
            self.point_b = (self.point_b.as_vec4(1) * transformation).try_into_vec3()
        # Return Chain
        return self

    def get_center_coords3(self) -> Vector3:
        # Get Points
        point_a = self.pipeline_point_a if self.in_pipeline else self.point_a
        point_b = self.pipeline_point_b if self.in_pipeline else self.point_b
        # Return Center
        center_coord = (point_a + point_b) * 0.5
        return center_coord.try_into_vec3()
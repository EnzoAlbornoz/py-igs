# Import Dependencies
from __future__ import annotations
from io import open
from typing import List, Tuple
from graphics.vec3 import Vec3
from scene.object3 import Object3
# Define Class
class FileOBJ:

    def __init__(self, vertices: List[Vec3] = [], faces: List[Tuple[int, int, int]] = [], normal_vertices: List[Vec3] = [] ,texture_vertices: List[Vec3] = []) -> None:
        self.vertices = vertices
        self.faces = faces
        self.normal_vertices = normal_vertices
        self.texture_vertices = texture_vertices

    @staticmethod
    def from_path(file_path: str) -> FileOBJ:
        # Open File
        file = open(file_path, "r")
        # Read Content
        content = file.read()
        # Close File
        file.close()
        # Parse
        return FileOBJ.from_string(content)
        
    @staticmethod
    def from_string(string: str) -> FileOBJ:
        # Initialize variables to build the 3D Model
        vertices = []
        faces = []
        normal_vertices = []
        texture_vertices = []
        # Iterate over lines
        lines = string.splitlines()
        for line in lines:
            # Split By Space
            line = line.split(" ")
            # First element defines the type
            if (line[0] == "v"):
                # Its a vertex
                x, y, z = [float(vd) for vd in line[1:]]
                # Add vertex to list
                vertices.append(Vec3(x, y, z))
            if (line[0] == "f"):
                # Its a face
                (v1, _, _), (v2, _, _), (v3, _, _) = [
                    [
                        (int(fde[i]) - 1) if i < len(fde := fd.split("/")) and fde[i] != "" else None\
                        for i in range(3)
                    ]\
                    for fd in line[1:]
                ]
                # Add vertex to list
                faces.append((v1, v2, v3))
        # Instantiate class
        return FileOBJ(vertices, faces, normal_vertices, texture_vertices)

    def into_object3(self) -> Object3:
        return Object3(self.vertices, self.faces)
from typing import List, Tuple
from graphics.vec3 import Vec3

class Object3:
    def __init__(self, points: List[Vec3], faces: List[Tuple[int, int, int]]) -> None:
        self.points = points
        self.faces = faces

    # def draw_wireframe() -> None:

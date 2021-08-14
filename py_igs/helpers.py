# pyright: reportUnknownMemberType=false
# pyright: reportMissingTypeStubs=false
# pyright: reportGeneralTypeIssues=false
# pyright: reportUntypedBaseClass=false
# pyright: reportUntypedBaseClass=false
# pyright: reportUnknownParameterType=false
# pyright: reportUntypedClassDecorator=false
# pyright: reportUntypedFunctionDecorator=false
import gi
from typing import Any, Iterable, List, Tuple, TypeVar
from ast import literal_eval
from itertools import zip_longest
from primitives.matrix import Vector2, Vector3
# Setup Graphic
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
# Setup Helper Functions
def extract_points_as_vec2_from_box(container_box: Any) -> List[Vector2]:
    # Get Points
    points: List[List[float]] = [
        [
            point_box_item.get_value()
            for point_box_item in point_box if isinstance(point_box_item, Gtk.SpinButton)
        ]
        for point_box in container_box
    ]
    # Map Points as Vectors
    vec_points = [Vector2(point_x, point_y) for [point_x, point_y] in points]
    # Return Vectors
    return vec_points

def extract_points_as_vec3_from_box(container_box: Any) -> List[Vector3]:
    # Get Points
    points: List[List[float]] = [
        [
            point_box_item.get_value()
            for point_box_item in point_box if isinstance(point_box_item, Gtk.SpinButton)
        ]
        for point_box in container_box
    ]
    # Map Points as Vectors
    vec_points = [Vector3(point_x, point_y, point_z) for [point_x, point_y, point_z] in points]
    # Return Vectors
    return vec_points

def parse_text_into_points_2d(text: str) -> List[Vector2]:
    # Parse Tuple List
    point_tuples = literal_eval(text)
    # Transform to Vectors
    points = [Vector2(x, y) for (x, y, *_) in point_tuples]
    # Return List
    return points

def parse_text_into_points_3d(text: str) -> List[Vector3]:
    # Parse Tuple List
    point_tuples = literal_eval(text)
    # Transform to Vectors
    points = [Vector3(x, y, more[0] if len(more) > 0 else 0) for (x, y, *more) in point_tuples]
    # Return List
    return points

def gdk_rgba_as_tuple(gdk_rgba: Any) -> Tuple[float, float, float, float]:
    return (gdk_rgba.red, gdk_rgba.green, gdk_rgba.blue, gdk_rgba.alpha)

V = TypeVar("V")
def chunks_non_null(iterable: Iterable[V], chunk_size: int) -> List[List[V]]:
    return [
        [el for el in chunked if el is not None]
        for chunked in (
            zip_longest(*[iter(iterable)] * chunk_size, fillvalue=None)
        )
    ]
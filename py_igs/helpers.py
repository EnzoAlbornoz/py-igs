import gi
from gi.repository import Gtk
from primitives.vec2 import Vector2
from typing import List, Tuple
# Setup Graphic
gi.require_version("Gtk", "3.0")
# Setup Helper Functions
def extract_points_as_vec2_from_box(container_box) -> List[Vector2]:
    []
    # Get Points
    points = [
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

def gdk_rgba_as_tuple(gdk_rgba) -> Tuple[float, float, float, float]:
    return (gdk_rgba.red, gdk_rgba.green, gdk_rgba.blue, gdk_rgba.alpha)
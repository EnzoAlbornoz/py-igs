from __future__ import annotations
from typing import List, TYPE_CHECKING, Tuple
from objects.object_type import ObjectType
from primitives.clipping_method import EClippingMethod, EWeilerAthertonDirection, clockwise_follow_border, cohen_sutherland_clip_line, is_vec_list_clockwise
from primitives.graphical_object import GraphicalObject
if TYPE_CHECKING:
    from cairo import Context
    from primitives.matrix import Matrix, Vector2

class Wireframe2D(GraphicalObject):
    # Define Constructor
    def __init__(self, *points: Vector2) -> None:
        # Call Super Constructor
        super().__init__()
        # Check Points Length
        if len(points) < 3:
            raise ValueError("Wireframe2D need 3 or more points to be defined")
        # Define Attributes
        self.points = list(points)
        # Define Pipeline Attributes
        self.pipeline_points = list(points)
        # Define Fill Options
        self.filled = True
    def __str__(self) -> str:
        desc = "Wireframe2D\n"
        for point in (self.pipeline_points if self.in_pipeline else self.points):
            desc += "\t" + point.__str__() + "\n"
        return desc
    # Type Definition
    @staticmethod
    def get_type() -> ObjectType:
        return ObjectType.WIREFRAME_2D
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

    def __get_current_points(self) -> List[Vector2]:
        return self.pipeline_points if self.in_pipeline else self.points
    # Filled Methods
    def set_filled(self, fill: bool) -> None:
        self.filled = fill
    # Define Methods
    def draw(self, cairo: Context):
        # Get Points
        points = self.pipeline_points if self.in_pipeline else self.points
        # Set Color
        cairo.set_source_rgba(*self.color)
        # Cast points into homogeneus space and match them with screen coords
        xy_points = [ point.as_tuple() for point in points ]
        xy_points_len = len(xy_points)
        # Draw segments in canvas
        for (x, y), idx in zip(xy_points, range(xy_points_len)):

            # Check non starting the drawing
            if idx != 0:
                 # Draw normal line
                cairo.line_to(x, y)
                # Check ending the drawing
                if idx == (xy_points_len - 1):
                    # Close drawing
                    # (x_init, y_init) = xy_points[0]
                    # cairo.line_to(x_init, y_init)
                    cairo.close_path()
            else:
                # Move to polygon start
                cairo.move_to(x, y)
        # Show result
        if self.filled:
            cairo.fill()
        else:
            cairo.stroke()
    
    def transform(self, transformation: Matrix):
        # Transform points
        if self.in_pipeline:
            # Pipeline
            self.pipeline_points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.pipeline_points
            ]
        else:
            # Raw Transform
            self.points = [
                (point.as_vec3(1) * transformation).try_into_vec2()
                for point in self.points
            ]
        # Return Chain
        return self

    def get_center_coords(self) -> Vector2:
        # Get Points
        points = self.pipeline_points if self.in_pipeline else self.points
        # Get Avg Point
        points_len_mult = 1 / len(points)
        avg_coords = Vector2(0, 0)
        for point in points:
            avg_coords += point
        avg_coords *= points_len_mult
        return avg_coords.try_into_vec2()

    def clip(self, method: EClippingMethod) -> GraphicalObject | None:
        # Switch Method
        if method == EClippingMethod.POLY_WEILER_ATHERTON:
            # Def Helper
            def is_inside(vec: Vector2):
                return abs(vec.get_x()) <= 1 and abs(vec.get_y()) <= 1
            # Heuristics - Outside
            heuristics = list(map(is_inside, self.__get_current_points()))
            # Heuristics - All Inside
            if all(heuristics):
                # All Visible
                return self
            # Get Points
            points = self.__get_current_points()
            if not is_vec_list_clockwise(points):
                points.reverse()
            points = [
                (
                    point,
                    (
                        EWeilerAthertonDirection.INSIDE
                            if is_inside(point) else
                        EWeilerAthertonDirection.OUTSIDE
                    )
                ) 
                for point in points
            ]
            new_points: List[Tuple[Vector2, EWeilerAthertonDirection]] = []
            for (idx, (point, status)) in enumerate(points):
                (next_point, _) =  points[(idx+1) % len(points)]
                clipped_points = cohen_sutherland_clip_line(point, next_point)
                # If none, simply continue to next iteration 
                if clipped_points is None:
                    new_points.append((point, status))
                    continue
                # Both Inside - Update Value
                (clipped_left, clipped_right) = clipped_points
                # Insert New Points
                new_points.append((point, status))
                if point != clipped_left:
                    new_points.append(
                        (
                            clipped_left,
                            (
                                EWeilerAthertonDirection.ENTER if
                                (
                                    not is_inside(point) and
                                    is_inside(clipped_right)
                                )
                                else EWeilerAthertonDirection.EXIT
                            )
                        )
                    )
                if next_point != clipped_right:
                    new_points.append(
                        (
                            clipped_right,
                            (
                                EWeilerAthertonDirection.EXIT if
                                (
                                    is_inside(clipped_left) and
                                    not is_inside(next_point)
                                )
                                else EWeilerAthertonDirection.ENTER
                            )
                        )
                    )
            # Return None if there is no point to render
            if (
                len(new_points) == 0 or
                all(map(lambda np: np[1] == EWeilerAthertonDirection.OUTSIDE, new_points))
            ):
                return None
            # Find the Entry inside Window
            new_points_idx = next(
                map(
                    lambda x: x[0],
                    filter(
                        lambda x: x[1][1] == EWeilerAthertonDirection.ENTER,
                        enumerate(new_points)
                    )
                )
            )
            final_points: List[Vector2] = []
            # Iterate Overt Path
            for it_idx in range(1, len(new_points) + 1):
                # Fetch Point
                (point, status) = new_points[(new_points_idx + it_idx) % len(new_points)]
                # Switch Status
                if status == EWeilerAthertonDirection.INSIDE:
                    final_points.append(point)
                elif status == EWeilerAthertonDirection.EXIT:
                    final_points.append(point)
                elif status == EWeilerAthertonDirection.OUTSIDE:
                    pass
                elif status == EWeilerAthertonDirection.ENTER:
                    # Follow the Window Border in Clockwise
                    last_point = final_points[-1]
                    border_points = clockwise_follow_border(last_point, point)
                    # Add Intersection Point
                    final_points.extend(border_points)
                    final_points.append(point)
            # Update Self Points
            if self.in_pipeline:
                self.pipeline_points = final_points
            else:
                self.points = final_points
            return self
        else:
            # Default - Trait as None Clipping
            return self
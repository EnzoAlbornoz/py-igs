# Import Dependencies
from __future__ import annotations
# from typing import TYPE_CHECKING
from enum import unique, IntEnum, IntFlag
from typing import List, Tuple
from primitives.matrix import Vector2
# Define Enum
@unique
class EClippingMethod(IntEnum):
    NONE = 0
    POINT_CLIP = 1
    LINE_COHEN_SUTHERLAND = 2
    POLY_WEILER_ATHERTON = 3
    
@unique
class ERegionCode(IntFlag):
    WINDOW = 0b0000
    LEFT   = 0b0001
    RIGHT  = 0b0010
    BOTTOM = 0b0100
    UPPER  = 0b1000
    UPPER_LEFT   = UPPER  | LEFT
    UPPER_RIGHT  = UPPER  | RIGHT
    BOTTOM_LEFT  = BOTTOM | LEFT
    BOTTOM_RIGHT = BOTTOM | RIGHT
    CLIP_LEFT   = 0b1101
    CLIP_UPPER  = 0b1011
    CLIP_RIGHT  = 0b1110
    CLIP_BOTTOM = 0b0111

def cohen_sutherland_clip_line(point_a: Vector2, point_b: Vector2) -> Tuple[Vector2, Vector2] | None:
    # Get Current Points
    points = [point_a, point_b]
    # Compute Region Codes
    region_codes = [
        (
            (
                # Compute X Axis
                (
                    ERegionCode.LEFT if point.get_x() < -1
                    else ERegionCode.RIGHT if point.get_x()
                    > 1 else ERegionCode.WINDOW
                )
            ) |
            (
                # Compute Y Axis
                (
                    ERegionCode.BOTTOM if point.get_y() < -1
                    else ERegionCode.UPPER if point.get_y()
                    > 1 else ERegionCode.WINDOW
                )
            )
        )
        for point in points
    ]
    # Get Left and Right RC
    pl, pr = points
    rc_l, rc_r = region_codes
    # Compare Region Codes
    if (rc_l | rc_r) == ERegionCode.WINDOW:
        # Is Completely Visible
        return (point_a, point_b)
    if (rc_l & rc_r) != ERegionCode.WINDOW:
        # Is Completely Invisible
        return None
    else:
        # Partially Visible - Clip
        clipped_left = pl
        clipped_right = pr
        # Handle Edge Case (Xs are equal)
        if pl.get_x() == pr.get_x():
            clipped_left = Vector2(pl.get_x(), min(max(-1, pl.get_y()), 1))
            clipped_right = Vector2(pr.get_x(), min(max(-1, pr.get_y()), 1))
        else:
            angular_coefficient = (pr.get_y() - pl.get_y()) / (pr.get_x() - pl.get_x())
            # Clip First Point
            if rc_l != ERegionCode.WINDOW:
                clipped_left = clip_point_region_code(pl, pl, rc_l, angular_coefficient)
                if (
                    clipped_left.get_x() < -1 or
                    clipped_left.get_x() >  1 or
                    clipped_left.get_y() < -1 or
                    clipped_left.get_y() >  1
                ):
                    return None
            # Clip Second Point
            if rc_r != ERegionCode.WINDOW:
                clipped_right = clip_point_region_code(pr, pl, rc_r, angular_coefficient)
                if (
                    clipped_right.get_x() < -1 or
                    clipped_right.get_x() >  1 or
                    clipped_right.get_y() < -1 or
                    clipped_right.get_y() >  1
                ):
                    return None
        # Return Clipped Data
        return (clipped_left, clipped_right)

def clip_point_region_code(point: Vector2, inital_point: Vector2, region_code: ERegionCode, angular_coefficient: float) -> Vector2:
    # Define Vars
    current_point = point
    point_bl = Vector2(-1, -1)
    point_ur = Vector2(1, 1)
    # Clip Left/Right
    if region_code & ERegionCode.LEFT:
        if angular_coefficient != 0:
            current_point = Vector2(
                point_bl.get_x(),
                inital_point.get_y() + (angular_coefficient * (point_bl.get_x() - inital_point.get_x()))
            )
        else:
            current_point = Vector2(point_bl.get_x(), inital_point.get_y())
    if region_code & ERegionCode.RIGHT:
        current_point = Vector2(
            point_ur.get_x(),
            inital_point.get_y() + (angular_coefficient * (point_ur.get_x() - inital_point.get_x()))
        )
    # Check Done Already
    if abs(current_point.get_x()) <= 1 and abs(current_point.get_y()) <= 1:
        return current_point
    # Clip Up/Down
    if region_code & ERegionCode.UPPER:
        current_point = Vector2(
            inital_point.get_x() + ((point_ur.get_y() - inital_point.get_y()) / angular_coefficient),
            point_ur.get_y()
        )
    if region_code & ERegionCode.BOTTOM:
        current_point = Vector2(
            inital_point.get_x() + ((point_bl.get_y() - inital_point.get_y()) / angular_coefficient),
            point_bl.get_y()
        )
    # Return Clipped Data
    return current_point

@unique
class EWeilerAthertonDirection(IntEnum):
    INSIDE = 0
    OUTSIDE = 1
    EXIT = 2
    ENTER = 3

WINDOW_BORDERS = [Vector2(-1, -1), Vector2(-1, 1), Vector2(1, 1), Vector2(1, -1)]
def next_clockwise_window_border_idx(point: Vector2) -> int:
    # Switch Point
    if point.get_y() <= -1:
        return 0
    elif point.get_x() <= -1:
        return 1
    elif point.get_y() >= 1:
        return 2
    elif point.get_x() >= 1:
        return 3
    return 0

def clockwise_follow_border(point_a: Vector2, point_b: Vector2) -> List[Vector2]:
    # Get Index of First Element
    fe_idx = next_clockwise_window_border_idx(point_a)
    # Get Index of Last Element
    le_idx = next_clockwise_window_border_idx(point_b)
    # Slice it
    points: List[Vector2] = []
    idx = 0
    while (fe_idx + idx) % len(WINDOW_BORDERS) != le_idx:
        points.append(WINDOW_BORDERS[(fe_idx + idx) % len(WINDOW_BORDERS)])
        idx += 1
    return points

def is_vec_list_clockwise(points: List[Vector2]) -> bool:
    # Based on https://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order
    total = sum(
        [
            (
                (points[(idx + 1) % len(points)].get_x() - point.get_x())
                    *
                (points[(idx + 1) % len(points)].get_y() + point.get_y())
            )
            for (idx, point) in enumerate(points)
        ]
    )
    return total >= 0
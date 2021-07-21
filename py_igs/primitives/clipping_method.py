# Import Dependencies
from __future__ import annotations
# from typing import TYPE_CHECKING
from enum import unique, IntEnum, IntFlag
from typing import Callable, List, Tuple
from primitives.matrix import Vector2
from itertools import chain

# Define Enum
@unique
class EClippingMethod(IntEnum):
    NONE = 0
    POINT_CLIP = 1
    LINE_COHEN_SUTHERLAND = 2
    LINE_LIANG_BARSKY = 3
    POLY_WEILER_ATHERTON_WITH_CS = 4
    POLY_WEILER_ATHERTON_WITH_LB = 5
    
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

def liang_barsky_clip_line(point_a: Vector2, point_b: Vector2) -> Tuple[Vector2, Vector2] | None:
    
    # Check Heuristic
    # Compute Delta X and Delta Y
    delta_x = point_b.get_x() - point_a.get_x()
    delta_y = point_b.get_y() - point_a.get_y()
    # Compute P and Q values
    p_values = [-delta_x, delta_x, -delta_y, delta_y]
    q_values = [(point_a.get_x() + 1), (1 - point_a.get_x()), (point_a.get_y() + 1), (1 - point_a.get_y())]
    # Compute Zetas
    zeta_one = max(0, *[(q_values[idx] / p_value) for (idx, p_value) in enumerate(p_values) if p_value < 0])
    zeta_two = min(1, *[(q_values[idx] / p_value) for (idx, p_value) in enumerate(p_values) if p_value > 0])
    # Check Outside
    if zeta_one > zeta_two:
        return None
    # Define Clipped Tuples
    clipped_left = (
        Vector2(point_a.get_x() + (zeta_one * delta_x), point_a.get_y() + (zeta_one * delta_y))
        if zeta_one != 0 else point_a
    )
    clipped_right = (
        Vector2(point_a.get_x() + (zeta_two * delta_x), point_a.get_y() + (zeta_two * delta_y))
        if zeta_two != 1 else point_b
    )
    # Return as Tuple
    return (clipped_left, clipped_right)

@unique
class EWeilerAthertonDirection(IntEnum):
    INSIDE = 0
    OUTSIDE = 1
    EXIT = 2
    ENTER = 3

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

WINDOW_BORDERS = [Vector2(-1, -1), Vector2(-1, 1), Vector2(1, 1), Vector2(1, -1)]
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

def weiler_atherton_w_cs_clip_poly(poly_points: List[Vector2]) -> List[Vector2] | None:
    # Def Helper
    def is_inside(vec: Vector2):
        return abs(vec.get_x()) <= 1 and abs(vec.get_y()) <= 1
    # Heuristics - Outside
    heuristics = list(map(is_inside, poly_points))
    # Heuristics - All Inside
    if all(heuristics):
        # All Visible
        return poly_points
    # Get Points
    points = poly_points
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
    return final_points

# Is Inside Function Helper
IS_INSIDE: Callable[[Vector2], bool] = lambda point: abs(point.get_x()) <= 1 and abs(point.get_y()) <= 1
def weiler_atherton_modified_liang_barsky(point_a: Vector2, point_b: Vector2) -> List[Tuple[Vector2, EWeilerAthertonDirection]]:
    # Check if Point A is inside
    is_point_a_inside = IS_INSIDE(point_a)
    point_a_status = EWeilerAthertonDirection.INSIDE if is_point_a_inside else EWeilerAthertonDirection.OUTSIDE
    # Compute Delta X and Delta Y
    delta_x = point_b.get_x() - point_a.get_x()
    delta_y = point_b.get_y() - point_a.get_y()
    # Compute P and Q values
    p_values = [-delta_x, delta_x, -delta_y, delta_y]
    q_values = [(point_a.get_x() + 1), (1 - point_a.get_x()), (point_a.get_y() + 1), (1 - point_a.get_y())]
    # Compute Zetas
    zeta_one = max(0, 0, *[(q_values[idx] / p_value) for (idx, p_value) in enumerate(p_values) if p_value < 0])
    zeta_two = min(1, 1, *[(q_values[idx] / p_value) for (idx, p_value) in enumerate(p_values) if p_value > 0])
    # Check Outside
    if zeta_one > zeta_two:
        return []
    # Define Clipped Tuples
    clipped_left = (
        Vector2(point_a.get_x() + (zeta_one * delta_x), point_a.get_y() + (zeta_one * delta_y))
        if zeta_one != 0 else None
    )
    clipped_right = (
        Vector2(point_a.get_x() + (zeta_two * delta_x), point_a.get_y() + (zeta_two * delta_y))
        if zeta_two != 1 else None
    )
    # Return as Tuple
    new_points = [
        (point_a, point_a_status),
        (clipped_left, EWeilerAthertonDirection.ENTER),
        (clipped_right, EWeilerAthertonDirection.EXIT)
    ]
    return [
        (point, status)
        for (point, status) in new_points
        if point is not None and status != EWeilerAthertonDirection.OUTSIDE and IS_INSIDE(point)
    ]

def weiler_atherton_w_lb_clip_poly(poly_points: List[Vector2]) -> List[Vector2]:
    # Check All Points in Domain
    if all([abs(vec.get_x()) <= 1 and abs(vec.get_y()) <= 1 for vec in poly_points]):
        return poly_points
    # Check Clockwise Points
    points = poly_points if is_vec_list_clockwise(poly_points) else poly_points[::-1]
    # Get Points Intersected
    points = list(
        chain.from_iterable(
            [
                weiler_atherton_modified_liang_barsky(
                    point,
                    points[(idx + 1) % len(points)]
                )
                for (idx, point) in enumerate(points)
            ]
        )
    )
    # Add Window Borders
    points = list(
        chain.from_iterable(
            [
                [point, *clockwise_follow_border(point, points[(idx + 1) % len(points)][0])]
                    if status == EWeilerAthertonDirection.EXIT else
                [point]
                for (idx, (point, status)) in enumerate(points)
            ]
        )
    )
    # Return Points
    return points
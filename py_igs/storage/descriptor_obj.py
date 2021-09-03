# Import Dependencies
from __future__ import annotations
from math import floor, sqrt
from pathlib import Path
from typing import Dict, List, Tuple, cast
from pathlib import Path
from helpers import chunks_non_null
from objects.bezier_3d import Bezier3D
from objects.bspline_2d import BSpline2D
from objects.bezier_2d import Bezier2D
from objects.bspline_3d import BSpline3D
from objects.object_3d import Object3D
from objects.point_2d import Point2D
from objects.line_2d import Line2D
from objects.wireframe_2d import Wireframe2D
from objects.wireframe_3d import Wireframe3D
from primitives.display_file import DisplayFile
from primitives.graphical_object import GraphicalObject
from primitives.matrix import Vector2, Vector3
from primitives.window import Window
# Declare Class
class DescriptorOBJ:
    # Define Constructor
    def __init__(self, objects: Dict[str, GraphicalObject], window_config: Tuple[Vector3, int, int]) -> None:
        # Destructure Params
        (window_center, window_width, window_height) = window_config
        # Attributes
        self.objects = objects
        self.window_center = window_center
        self.window_width = window_width
        self.window_height = window_height
    # Define Parser
    @staticmethod
    def parseFile(file_name: str, default_width: int, default_height: int, fill_faces: bool = False) -> DescriptorOBJ:
        DISPLAY_UNDEFINED_FIELDS = False
        # Define Working Dir Context
        file_path = Path(file_name).resolve()
        # working_dir = file_path.parent
        # Check is File
        if not file_path.is_file():
            raise ValueError("Invalid file path")
        # Define Vertices
        vertices_positions: List[Tuple[float, float, float]] = []
        # Define Objects
        current_object: str | None = None
        objects: Dict[str, GraphicalObject] = dict()
        # Define Window Config
        window_center: Vector3 = Vector3(0, 0, 0)
        window_width: int = default_width
        window_height: int = default_height
        is_normalized = False
        # Define Materials
        materials: Dict[str, Tuple[float, float, float]] = dict()
        current_reading_material = "loaded_material"
        current_using_material: str | None = None
        current_curve_type: str = "bspline"
        # Read File
        with file_path.open() as file:
            # Iterate over Lines
            for line in file:
                # Switch For Line Type
                if len(line.strip()) == 0:
                    # Empty Line
                    pass
                elif line.startswith("#"):
                    # Comment
                    pass
                elif line.startswith("v "):
                    # Vertex
                    _, *values = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Parse XYZ
                    vx, vy, vz = [float(values[idx]) if len(values) > idx else 0.0 for idx in range(3)]
                    # Add vertex to vertices list
                    vertices_positions.append((vx,vy,vz))
                elif line.startswith("l "):
                    # Line
                    _, *values = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Parse FROM and TO
                    idx_vecs = [int(value.split("/")[0]) for value in values]
                    # Load Vertices into Vector 2D
                    line_vecs = [vertices_positions[idx_vec - 1] for idx_vec in idx_vecs]
                    line_vecs = [
                        Vector2(
                            (vx * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (vy * (0.5 * window_height if is_normalized else 1)) + window_center.get_y()
                        )
                        for (vx, vy, *_) in line_vecs
                    ]
                    # Build Object
                    line = Wireframe2D(*line_vecs) if len(line_vecs) > 2 else Line2D(*line_vecs)
                    # Check Filled
                    if isinstance(line, Wireframe2D):
                        line.set_filled(fill_faces)
                    # Check Color
                    if current_using_material is not None:
                        # Update Object Material
                        material_kd_rgb = materials[current_using_material]
                        line.set_color((*material_kd_rgb, 1))
                    # Add Line to Objects
                    if current_object is None:
                        objects[f"loaded_object_{len(objects)}"] = line
                    else:
                        objects[current_object] = line
                elif line.startswith("curv2 "):
                    # Line
                    _, *values = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Parse FROM and TO
                    idx_vecs = [int(value.split("/")[0]) for value in values]
                    # Load Vertices into Vector 2D
                    curve_vecs = [vertices_positions[idx_vec - 1] for idx_vec in idx_vecs]
                    curve_vecs = [
                        Vector2(
                            (vx * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (vy * (0.5 * window_height if is_normalized else 1)) + window_center.get_y()
                        )
                        for (vx, vy, *_) in curve_vecs
                    ]
                    # Build Object
                    curve = Bezier2D(0.01, *curve_vecs) if current_curve_type == "bezier" else BSpline2D(0.01, *curve_vecs)
                    # Check Filled
                    if isinstance(curve, Wireframe2D):
                        curve.set_filled(fill_faces)
                    # Check Color
                    if current_using_material is not None:
                        # Update Object Material
                        material_kd_rgb = materials[current_using_material]
                        curve.set_color((*material_kd_rgb, 1))
                    # Add curve to Objects
                    if current_object is None:
                        objects[f"loaded_object_{len(objects)}"] = curve
                    else:
                        objects[current_object] = curve
                elif line.startswith("f "):
                    # Face (Triangle)
                    # Get Values List
                    _, *values = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Parse Triangle Vertices
                    vectors = [int(value.split("/")[0]) for value in values]
                    # Load Vertices
                    vectors = [vertices_positions[v_idx - 1] for v_idx in vectors]
                    vectors = [
                        Vector3(
                            (vx * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (vy * (0.5 * window_height if is_normalized else 1)) + window_center.get_y(),
                            (vz * (0.5 * window_height if is_normalized else 1)) + window_center.get_z()
                        )
                        for (vx, vy, vz) in vectors
                    ]
                    # Define Triangle
                    triangle = Wireframe3D(*vectors)
                    # Fill Faces
                    triangle.set_filled(fill_faces)
                    # Check Color
                    if current_using_material is not None:
                        # Update Object Material
                        material_kd_rgb = materials[current_using_material]
                        triangle.set_color((*material_kd_rgb, 1))
                    # Add Triangle to Objects
                    if current_object is None:
                        if "loaded_object" in objects.keys():
                            cast(Object3D, objects["loaded_object"]).wireframes.append(triangle)
                        else:
                            objects["loaded_object"] = Object3D(triangle)
                    else:
                        if current_object in objects.keys() and isinstance(objects[current_object], Object3D):
                            cast(Object3D, objects[current_object]).wireframes.append(triangle)
                        else:
                            objects[current_object] = Object3D(triangle)
                elif line.startswith("p "):
                    # Point
                    # Get Point Data
                    _, point_idx = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Parse Point Index
                    point_idx = int(point_idx.split("/")[0])
                    (vx, vy, *_) = vertices_positions[point_idx - 1]
                    # Create Object
                    point = Point2D(
                        Vector2(
                            (vx * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (vy * (0.5 * window_height if is_normalized else 1)) + window_center.get_y()
                        )
                    )
                    # Check Color
                    if current_using_material is not None:
                        # Update Object Material
                        material_kd_rgb = materials[current_using_material]
                        point.set_color((*material_kd_rgb, 1))
                    # Add Point to Objects
                    if current_object is None:
                        objects[f"loaded_object_{len(objects)}"] = point
                    else:
                        objects[current_object] = point
                elif line.startswith("surf "):
                    # Point
                    # Get Point Data
                    _, _, _, _, _, *values  = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Parse FROM and TO
                    idx_vecs = [int(value.split("/")[0]) for value in values]
                    # Load Vertices into Vector 2D
                    curve_vecs = [vertices_positions[idx_vec - 1] for idx_vec in idx_vecs]
                    curve_vecs = [
                        Vector3(
                            (vx * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (vy * (0.5 * window_height if is_normalized else 1)) + window_center.get_y(),
                            (vz * (0.5 * window_height if is_normalized else 1)) + window_center.get_z()
                        )
                        for (vx, vy, vz, *_) in curve_vecs
                    ]
                    size = floor(sqrt(len(curve_vecs)))
                    surf_mats = chunks_non_null(curve_vecs, size)
                    # Build Object
                    curve = Bezier3D(0.05, *surf_mats) if current_curve_type == "bezier" else BSpline3D(0.05, *surf_mats)
                    # Check Filled
                    if isinstance(curve, Wireframe2D):
                        curve.set_filled(fill_faces)
                    # Check Color
                    if current_using_material is not None:
                        # Update Object Material
                        material_kd_rgb = materials[current_using_material]
                        curve.set_color((*material_kd_rgb, 1))
                    # Add curve to Objects
                    if current_object is None:
                        objects[f"loaded_object_{len(objects)}"] = curve
                    else:
                        objects[current_object] = curve
                elif line.startswith("o "):
                    # Object Name
                    _, object_name = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Update Object Name
                    current_object = object_name.strip().strip("\n")
                elif line.startswith("cstype "):
                    # Object Name
                    _, curve_type = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Update Curve Type
                    current_curve_type = curve_type
                elif line.startswith("w "):
                    # Definition of Window Sizing
                    _, *values = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Parse Data
                    vi_center, vi_dims = [int(values[idx]) for idx in range(2)]
                    # Load From Vectors
                    (vc_x, vc_y, vc_z, *_) = vertices_positions[vi_center - 1]
                    (v_w, v_h, *_) = vertices_positions[vi_dims - 1]
                    # Update Data
                    window_center = Vector3(vc_x, vc_y, vc_z)
                    window_width = int(v_w)
                    window_height = int(v_h)
                    # is_normalized = True
                elif line.startswith("mtllib"):
                    # Import Material File
                    _, material_file_path = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Resolve File
                    material_file_path = file_path.parent.joinpath(material_file_path.strip().strip("\n"))
                    # Open and Read File
                    with material_file_path.open() as mat_file:
                        for mat_line in mat_file:
                            mat_line = mat_line.strip().strip("\n")
                            if len(mat_line.strip()) == 0 or mat_line.startswith("#"):
                                pass
                            elif mat_line.startswith("newmtl "):
                                # New Material
                                _, material_name = [el for el in mat_line.strip("\n").split(" ") if len(el) > 0]
                                # Update Current Material Name
                                current_reading_material = material_name
                            elif mat_line.startswith("Kd "):
                                # Get Material Data
                                _, *values = [el for el in mat_line.strip("\n").split(" ") if len(el) > 0]
                                kd_r, kd_g, kd_b = [float(values[idx]) if len(values) > idx else 1 for idx in range(3)]
                                # Save Material
                                materials[current_reading_material] = (kd_r, kd_g, kd_b)
                            else:
                                # No Behaviour
                                if DISPLAY_UNDEFINED_FIELDS:
                                    print(f"Unrecognized line: '{mat_line}'")
                elif line.startswith("usemtl "):
                    # Use Material
                    _, material_name = [el for el in line.strip("\n").split(" ") if len(el) > 0]
                    # Update Current Material
                    current_using_material = material_name
                else:
                    # No Behaviour
                    if DISPLAY_UNDEFINED_FIELDS:
                        print(f"Unrecognize Field: {line.strip()}")
        # Create Class
        return DescriptorOBJ(objects, (window_center, window_width, window_height))

    @staticmethod
    def serializeToFiles(file_name_obj: str, file_name_mtl: str, display_file: DisplayFile, window: Window) -> None:
        # Get Objects Dict
        objects = display_file.get_objects()
        # Get Window Data
        window_center = window.get_center()
        window_width = window.get_width()
        window_height = window.get_height()
        window_vup = window.get_vec_up()
        window_vpn = window.get_vec_normal()
        # Define Lists
        vertices: List[Vector3] = []
        object_lines: List[str] = []
        materials: List[str] = []
        # Define Window
        vertices.append(window_center)
        vertices.append(Vector3(window_width, window_height, 1))
        vertices.append(window_vpn)
        vertices.append(window_vup)
        window_settings = "w 1 2 3 4"
        # Define Material Import
        object_file_path = Path(file_name_obj)
        material_file_path = Path(file_name_mtl)
        relative_material_file_path = material_file_path.relative_to(object_file_path.parent)
        material_import = f"mtllib {relative_material_file_path}"
        # Iterate over Objects
        for (object_name, _, object_graphics) in objects:
            # Normalized Object
            object_graphics.pipeline()
            if isinstance(object_graphics, Point2D):
                points = [object_graphics.pipeline_point]
                vertex_idxs: List[int] = []
                for point in points:
                    vertices.append(point.as_vec3(1))
                    vertex_idx = len(vertices)
                    vertex_idxs.append(vertex_idx)
                # Declare Materials
                (kd_r, kd_g, kd_b, *_) = object_graphics.color
                material_lines: List[str] = []
                material_lines.append(f"newmtl mtl_{object_name.strip()}")
                material_lines.append(f"Kd {float(kd_r)} {float(kd_g)} {float(kd_b)}")
                # Declare Object
                content: List[str] = []
                content.append(f"o {object_name}")
                content.append(f"usemtl mtl_{object_name.strip()}")
                content.append("p " + " ".join(map(str, vertex_idxs)))
                # Save Into List
                object_lines.append("\n".join(content))
                materials.append("\n".join(material_lines))
            elif isinstance(object_graphics, Line2D):
                points = [object_graphics.pipeline_point_a, object_graphics.pipeline_point_b]
                vertex_idxs: List[int] = []
                for point in points:
                    vertices.append(point.as_vec3(1))
                    vertex_idx = len(vertices)
                    vertex_idxs.append(vertex_idx)
                # Declare Materials
                (kd_r, kd_g, kd_b, *_) = object_graphics.color
                material_lines: List[str] = []
                material_lines.append(f"newmtl mtl_{object_name.strip()}")
                material_lines.append(f"Kd {float(kd_r)} {float(kd_g)} {float(kd_b)}")
                # Declare Object
                content: List[str] = []
                content.append(f"o {object_name}")
                content.append(f"usemtl mtl_{object_name.strip()}")
                content.append("curv2 " + " ".join(map(str, vertex_idxs)))
                # Save Into List
                object_lines.append("\n".join(content))
                materials.append("\n".join(material_lines))
            elif isinstance(object_graphics, Bezier2D):
                points = object_graphics.control_points
                vertex_idxs: List[int] = []
                for point in points:
                    vertices.append(point.as_vec3(1))
                    vertex_idx = len(vertices)
                    vertex_idxs.append(vertex_idx)
                # Declare Materials
                (kd_r, kd_g, kd_b, *_) = object_graphics.color
                material_lines: List[str] = []
                material_lines.append(f"newmtl mtl_{object_name.strip()}")
                material_lines.append(f"Kd {float(kd_r)} {float(kd_g)} {float(kd_b)}")
                # Declare Object
                content: List[str] = []
                content.append(f"o {object_name}")
                content.append("cstype bezier")
                content.append(f"usemtl mtl_{object_name.strip()}")
                content.append("curv2 " + " ".join(map(str, vertex_idxs)))
                # Save Into List
                object_lines.append("\n".join(content))
                materials.append("\n".join(material_lines))
            elif isinstance(object_graphics, BSpline2D):
                points = object_graphics.control_points
                vertex_idxs: List[int] = []
                for point in points:
                    vertices.append(point.as_vec3(1))
                    vertex_idx = len(vertices)
                    vertex_idxs.append(vertex_idx)
                # Declare Materials
                (kd_r, kd_g, kd_b, *_) = object_graphics.color
                material_lines: List[str] = []
                material_lines.append(f"newmtl mtl_{object_name.strip()}")
                material_lines.append(f"Kd {float(kd_r)} {float(kd_g)} {float(kd_b)}")
                # Declare Object
                content: List[str] = []
                content.append(f"o {object_name}")
                content.append("cstype bspline")
                content.append(f"usemtl mtl_{object_name.strip()}")
                content.append("l " + " ".join(map(str, vertex_idxs)))
                # Save Into List
                object_lines.append("\n".join(content))
                materials.append("\n".join(material_lines))
            elif isinstance(object_graphics, Wireframe2D):
                points = object_graphics.pipeline_points
                is_triangle = len(points) == 3
                vertex_idxs: List[int] = []
                for point in points:
                    vertices.append(point.as_vec3(1))
                    vertex_idx = len(vertices)
                    vertex_idxs.append(vertex_idx)
                # Declare Materials
                (kd_r, kd_g, kd_b, *_) = object_graphics.color
                material_lines: List[str] = []
                material_lines.append(f"newmtl mtl_{object_name.strip()}")
                material_lines.append(f"Kd {float(kd_r)} {float(kd_g)} {float(kd_b)}")
                # Declare Object
                content: List[str] = []
                content.append(f"o {object_name}")
                content.append(f"usemtl mtl_{object_name.strip()}")
                content.append(("f" if is_triangle else "l") + " " + " ".join(map(str, vertex_idxs)))
                # Save Into List
                object_lines.append("\n".join(content))
                materials.append("\n".join(material_lines))
            elif isinstance(object_graphics, Object3D):
                wf_points = [wf.pipeline_points for wf in object_graphics.wireframes]
                # Declare Objects
                content: List[str] = []
                material_lines: List[str] = []
                # Stringify Objects
                content.append(f"o {object_name}")
                for points in wf_points:
                    vertex_idxs: List[int] = []
                    for point in points:
                        vertices.append(point)
                        vertex_idx = len(vertices)
                        vertex_idxs.append(vertex_idx)
                    # Declare Materials
                    (kd_r, kd_g, kd_b, *_) = object_graphics.color
                    material_lines.append(f"newmtl mtl_{object_name.strip()}")
                    material_lines.append(f"Kd {float(kd_r)} {float(kd_g)} {float(kd_b)}")
                    # Declare Object
                    content.append(f"usemtl mtl_{object_name.strip()}")
                    content.append(("f") + " " + " ".join(map(str, vertex_idxs)))
                # Save Into List
                object_lines.append("\n".join(content))
                materials.append("\n".join(material_lines))
        # Serialize Vertices
        vertices_serialized = "\n".join([f"v {vertex.get_x()} {vertex.get_y()} 0" for vertex in vertices])
        object_lines_serialized = "\n".join(object_lines)
        # Serialize
        materials_serialized = "\n".join(materials)
        object_file_content = "\n".join([material_import, vertices_serialized, window_settings, object_lines_serialized])
        # Write File
        with object_file_path.open("w") as f:
            f.write(object_file_content)
        with material_file_path.open("w") as f:
            f.write(materials_serialized)
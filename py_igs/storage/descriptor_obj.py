# Import Dependencies
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
from pathlib import Path
from objects.point_2d import Point2D
from objects.line_2d import Line2D
from objects.wireframe_2d import Wireframe2D
from primitives.display_file import DisplayFile
from primitives.graphical_object import GraphicalObject
from primitives.matrix import Vector2
from primitives.window import Window
# Declare Class
class DescriptorOBJ:
    # Define Constructor
    def __init__(self, objects: Dict[str, GraphicalObject], window_config: Tuple[Vector2, int, int]) -> None:
        # Destructure Params
        (window_center, window_width, window_height) = window_config
        # Attributes
        self.objects = objects
        self.window_center = window_center
        self.window_width = window_width
        self.window_height = window_height
    # Define Parser
    @staticmethod
    def parseFile(file_name: str, default_width: int, default_height: int) -> DescriptorOBJ:
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
        window_center: Vector2 = Vector2(0, 0)
        window_width: int = default_width
        window_height: int = default_height
        is_normalized = False
        # Define Materials
        materials: Dict[str, Tuple[float, float, float]] = dict()
        current_reading_material = "loaded_material"
        current_using_material: str | None = None
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
                elif line.startswith("v"):
                    # Vertex
                    _, *values = [el for el in line.split(" ") if len(el) > 0]
                    # Parse XYZ
                    vx, vy, vz = [float(values[idx]) if len(values) > idx else 0.0 for idx in range(3)]
                    # Add vertex to vertices list
                    vertices_positions.append((vx,vy,vz))
                elif line.startswith("l"):
                    # Line
                    _, *values = [el for el in line.split(" ") if len(el) > 0]
                    # Parse FROM and TO
                    idx_vecs = [int(values[idx].split("/")[0]) if len(values) > idx else 0 for idx in range(max(2, len(values)))]
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
                elif line.startswith("f"):
                    # Face (Triangle)
                    # Get Values List
                    _, *values = [el for el in line.split(" ") if len(el) > 0]
                    # Parse Triangle Vertices
                    vi_1, vi_2, vi_3 = [int(values[idx].split("/")[0]) if len(values) > idx else 0 for idx in range(3)]
                    # Load Vertices
                    (v1_x, v1_y, *_) = vertices_positions[vi_1 - 1]
                    (v2_x, v2_y, *_) = vertices_positions[vi_2 - 1]
                    (v3_x, v3_y, *_) = vertices_positions[vi_3 - 1]
                    (v4_x, v4_y, *_) = vertices_positions[vi_3 - 1]
                    # Define Triangle
                    triangle = Wireframe2D(
                        Vector2(
                            (v1_x * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (v1_y * (0.5 * window_height if is_normalized else 1)) + window_center.get_y()
                        ),
                        Vector2(
                            (v2_x * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (v2_y * (0.5 * window_height if is_normalized else 1)) + window_center.get_y()
                        ),
                        Vector2(
                            (v3_x * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (v3_y * (0.5 * window_height if is_normalized else 1)) + window_center.get_y()
                        ),
                        Vector2(
                            (v4_x * (0.5 * window_width if is_normalized else 1)) + window_center.get_x(),
                            (v4_y * (0.5 * window_height if is_normalized else 1)) + window_center.get_y()
                        )
                    )
                    # Check Color
                    if current_using_material is not None:
                        # Update Object Material
                        material_kd_rgb = materials[current_using_material]
                        triangle.set_color((*material_kd_rgb, 1))
                    # Add Triangle to Objects
                    if current_object is None:
                        objects[f"loaded_object_{len(objects)}"] = triangle
                    else:
                        objects[current_object] = triangle
                elif line.startswith("p"):
                    # Point
                    # Get Point Data
                    _, point_idx = [el for el in line.split(" ") if len(el) > 0]
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
                elif line.startswith("o"):
                    # Object Name
                    _, object_name = [el for el in line.split(" ") if len(el) > 0]
                    # Update Object Name
                    current_object = object_name.strip().strip("\n")
                elif line.startswith("w"):
                    # Definition of Window Sizing
                    _, *values = [el for el in line.split(" ") if len(el) > 0]
                    # Parse Data
                    vi_center, vi_dims = [int(values[idx]) for idx in range(2)]
                    # Load From Vectors
                    (vc_x, vc_y, *_) = vertices_positions[vi_center - 1]
                    (v_w, v_h, *_) = vertices_positions[vi_dims - 1]
                    # Update Data
                    window_center = Vector2(vc_x, vc_y)
                    window_width = int(v_w)
                    window_height = int(v_h)
                    is_normalized = True
                elif line.startswith("mtllib"):
                    # Import Material File
                    _, material_file_path = [el for el in line.split(" ") if len(el) > 0]
                    # Resolve File
                    material_file_path = file_path.parent.joinpath(material_file_path.strip().strip("\n"))
                    # Open and Read File
                    with material_file_path.open() as mat_file:
                        for mat_line in mat_file:
                            if len(mat_line.strip()) == 0 or mat_line.startswith("#"):
                                pass
                            elif mat_line.startswith("newmtl"):
                                # New Material
                                _, material_name = [el for el in mat_line.split(" ") if len(el) > 0]
                                # Update Current Material Name
                                current_reading_material = material_name
                            elif mat_line.startswith("Kd"):
                                # Get Material Data
                                _, *values = [el for el in mat_line.split(" ") if len(el) > 0]
                                kd_r, kd_g, kd_b = [float(values[idx]) if len(values) > idx else 1 for idx in range(3)]
                                # Save Material
                                materials[current_reading_material] = (kd_r, kd_g, kd_b)
                            else:
                                # No Behaviour
                                print(f"Unrecognized line: '{mat_line}'")
                elif line.startswith("usemtl"):
                    # Use Material
                    _, material_name = [el for el in line.split(" ") if len(el) > 0]
                    # Update Current Material
                    current_using_material = material_name
                else:
                    # No Behaviour
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
        normalization_matrix = window.as_normalized_coordinates_transform()
        # Define Lists
        vertices: List[Vector2] = []
        object_lines: List[str] = []
        materials: List[str] = []
        # Define Window
        vertices.append(window_center)
        vertices.append(Vector2(window_width, window_height))
        window_settings = "w 1 2"
        # Define Material Import
        object_file_path = Path(file_name_obj)
        material_file_path = Path(file_name_mtl)
        relative_material_file_path = material_file_path.relative_to(object_file_path.parent)
        material_import = f"mtllib {relative_material_file_path}"
        # Iterate over Objects
        for (object_name, _, object_graphics) in objects:
            # Normalized Object
            object_graphics.pipeline()
            object_graphics.transform(normalization_matrix)
            if isinstance(object_graphics, Point2D):
                points = [object_graphics.pipeline_point]
                vertex_idxs: List[int] = []
                for point in points:
                    vertices.append(point)
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
                    vertices.append(point)
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
                content.append("l " + " ".join(map(str, vertex_idxs)))
                # Save Into List
                object_lines.append("\n".join(content))
                materials.append("\n".join(material_lines))
            elif isinstance(object_graphics, Wireframe2D):
                points = object_graphics.pipeline_points
                is_triangle = len(points) == 3
                vertex_idxs: List[int] = []
                for point in points:
                    vertices.append(point)
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
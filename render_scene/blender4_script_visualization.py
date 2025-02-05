import argparse
import faulthandler
import pickle
import traceback
from functools import cache

import math
from bpy import ops
from bpy.ops import object, file

import json
import random
import sys
from typing import Callable, Dict, Tuple, Generator, Optional, List, Any

import bpy
from bpy.ops import import_scene, wm, preferences, uv, mesh, image
from pathlib import Path
from numpy import abs, sqrt, arange
from mathutils import Vector, Euler

faulthandler.enable()

IMPORT_FUNCTIONS: Dict[str, Callable] = {
    "usd": bpy.ops.wm.usd_import,
    "usda": bpy.ops.wm.usd_import,
    "usdc": bpy.ops.wm.usd_import,
    "usdz": bpy.ops.wm.usd_import,

    "glb": bpy.ops.import_scene.gltf,
    "gltf": bpy.ops.import_scene.gltf,

    "fbx": bpy.ops.import_scene.fbx,
    "stl": bpy.ops.wm.stl_import,
    "dae": bpy.ops.wm.collada_import,
    "ply": bpy.ops.wm.ply_import,
    "abc": bpy.ops.wm.alembic_import,
    "obj": bpy.ops.wm.obj_import,
    "x3d": bpy.ops.import_scene.x3d,

    "blend": bpy.ops.wm.open_mainfile,
}


def scale_root_object(change_scale=(1, 1, 1), restore=False):
    import traceback
    from typing import Generator
    import bpy

    def get_scene_root_objects() -> Generator[bpy.types.Object, None, None]:
        """Returns all root objects in the scene.

        Yields:
            Generator[bpy.types.Object, None, None]: Generator of all root objects in the
                scene.
        """
        for obj in bpy.context.scene.objects.values():
            if not obj.parent:
                yield obj

    restore_scale = tuple(1 / s for s in change_scale)
    for obj in get_scene_root_objects():
        if "building_asset_" not in obj.name:
            continue
        try:
            if restore:
                scale = tuple(objs * s for objs, s in zip(obj.scale, restore_scale, strict=True))
            else:
                scale = tuple(objs * s for objs, s in zip(obj.scale, change_scale, strict=True))
            print("scaling: ", scale)
            obj.scale = scale
        except Exception as e:
            print(traceback.format_exc())


def _add_collection(col_name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(col_name, None)
    if col is None:
        # Create a new collection with a given name
        col = bpy.data.collections.new(col_name)
        # Link the new collection to the scene collection
        bpy.context.scene.collection.children.link(col)
    return col


def _add_mesh(name, verts, faces, edges=None, col=bpy.context.scene.collection):
    if edges is None:
        edges = []
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)
    bpy.ops.object.select_all(action="DESELECT")
    print("added", name)
    return obj


def _move_points(points, offset=None):
    if offset is None:
        offset = (0, 0, 0)
    moved_points = []
    for point in points:
        zipped = zip(point, offset)
        mapped = map(sum, zipped)
        moved = tuple(mapped)
        moved_points.append(moved)
    return moved_points


# https://mathworld.wolfram.com/PolygonArea.html
def _judge_poly_direction(vertices):
    res = calculate_area(vertices)
    assert res != 0, "area==0"
    return res < 0


def calculate_area(vertices) -> float:
    res = 0
    length = len(vertices)
    for i in range(length):
        j = (i + 1) % length
        res += vertices[i][0] * vertices[j][1] - vertices[i][1] * vertices[j][0]
    return res / 2


def _gen_verts_faces(bottom_verts, top_verts):
    assert len(bottom_verts) == len(top_verts)
    number_side_face = len(bottom_verts)
    faces = [
        tuple(arange(number_side_face - 1, -1, -1)),
        tuple(arange(number_side_face, number_side_face * 2, 1)),
    ]

    if _judge_poly_direction(bottom_verts):
        print("bottom_verts reversing to reverse-clockwise")
        bottom_verts.reverse()
        top_verts.reverse()

    for idx in range(number_side_face):
        side_face = (
            idx,
            (idx + 1) % number_side_face,
            number_side_face + (idx + 1) % number_side_face,
            number_side_face + idx,
        )
        faces.append(side_face)
    return bottom_verts + top_verts, faces


def _cut_one_hole_on_mesh(mesh_name, cutter_name):
    # Select the object that you want to be cut on another object
    # bpy.ops.object.select_all(action="DESELECT")
    mesh_to_be_cut = bpy.data.objects[mesh_name]
    # mesh_to_be_cut.select_set(True)
    bpy.context.view_layer.objects.active = mesh_to_be_cut
    # Select the second object in which you want another object to be cut on
    cutter_mesh = bpy.data.objects[cutter_name]

    # Apply the bool tool
    """
    Only Manifold meshes are guaranteed to give proper results, other cases (especially "opened" meshes, Non-manifold but without any self-intersections) will usually work well, but might give odd glitches and artifacts in some cases.
    The boolean modifier is not guaranteed to work correctly with non-manifold meshes. It is recommended to convert the mesh to manifold before applying the modifier.
    """
    bool_mod = mesh_to_be_cut.modifiers.new("create_hole", type="BOOLEAN")
    bool_mod.operation = "DIFFERENCE"
    bool_mod.solver = "EXACT"
    bool_mod.object = cutter_mesh
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)

    bpy.data.objects.remove(cutter_mesh, do_unlink=True)


def add_meshes_with_holes(name, boundaries, col_name) -> bpy.types.Object | None:
    col = _add_collection(col_name)
    show_only_collection(col_name)
    obj: bpy.types.Object = None
    boundaries.sort(key=lambda x: len(x), reverse=True)
    for idx in range(len(boundaries)):
        verts = boundaries[idx]
        if idx == 0:
            obj = _add_mesh(name, verts, [tuple(arange(len(verts)))], None, col)
            continue
        cut_name = f"{name}_cut_{idx}"
        thickness: int = 100
        bottom_points = _move_points(verts, (0, 0, -thickness))
        top_points = _move_points(verts, (0, 0, thickness))

        bottom_top_verts, faces = _gen_verts_faces(bottom_points, top_points)
        _add_mesh(cut_name, bottom_top_verts, faces, None, col)
        _cut_one_hole_on_mesh(name, cut_name)
        print("cut", cut_name)
    return obj


def _get_random_color() -> Tuple[float, float, float, float]:
    """Generates a random RGB-A color.

    The alpha value is always 1.

    Returns:
        Tuple[float, float, float, float]: A random RGB-A color. Each value is in the
        range [0, 1].
    """
    return random.random(), random.random(), random.random(), 1


def _apply_color_to_object(
        obj: bpy.types.Object,
        color: Tuple[float, float, float, float]
) -> None:
    """Applies the given color to the object.

    Args:
        obj (bpy.types.Object): The object to apply the color to.
        color (Tuple[float, float, float, float]): The color to apply to the object.

    Returns:
        None
    """
    mat = bpy.data.materials.new(name=f"Material_{obj.name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = color
    obj.data.materials.append(mat)


def apply_image_to_plane(image_file_path: str, plane_object: bpy.types.Object,
                         is_water_node=False, texture_scale=(10.0, 10.0, 1.0)):
    image_file_name = Path(image_file_path).name

    # create material_image
    mat = bpy.data.materials.new(name=f"material_image_{image_file_name}")
    mat.use_nodes = True

    # initialize material_image node group
    def material_image_node_group():
        material_image = mat.node_tree
        # start with a clean node tree
        for node in material_image.nodes:
            material_image.nodes.remove(node)
        # material_image interface

        # initialize material_image nodes
        # node Principled BSDF
        principled_bsdf = material_image.nodes.new("ShaderNodeBsdfPrincipled")
        principled_bsdf.name = "Principled BSDF"
        principled_bsdf.distribution = 'MULTI_GGX'
        principled_bsdf.subsurface_method = 'RANDOM_WALK'

        if is_water_node:
            # Metallic
            principled_bsdf.inputs[1].default_value = 0.9
            # Roughness
            principled_bsdf.inputs[2].default_value = 0.3
            # IOR
            principled_bsdf.inputs[3].default_value = 1.33
        else:
            # Metallic
            principled_bsdf.inputs[1].default_value = 0.0
            # Roughness
            principled_bsdf.inputs[2].default_value = 0.5
            # IOR
            principled_bsdf.inputs[3].default_value = 1.45

        # Alpha
        principled_bsdf.inputs[4].default_value = 1.0
        # Normal
        principled_bsdf.inputs[5].default_value = (0.0, 0.0, 0.0)
        # Weight
        principled_bsdf.inputs[6].default_value = 0.0
        # Subsurface Weight
        principled_bsdf.inputs[7].default_value = 0.0
        # Subsurface Radius
        principled_bsdf.inputs[8].default_value = (1.0, 0.2, 0.1)
        # Subsurface Scale
        principled_bsdf.inputs[9].default_value = 0.05
        # Subsurface IOR
        principled_bsdf.inputs[10].default_value = 1.4
        # Subsurface Anisotropy
        principled_bsdf.inputs[11].default_value = 0.0
        # Specular IOR Level
        principled_bsdf.inputs[12].default_value = 0.5
        # Specular Tint
        principled_bsdf.inputs[13].default_value = (1.0, 1.0, 1.0, 1.0)
        # Anisotropic
        principled_bsdf.inputs[14].default_value = 0.0
        # Anisotropic Rotation
        principled_bsdf.inputs[15].default_value = 0.0
        # Tangent
        principled_bsdf.inputs[16].default_value = (0.0, 0.0, 0.0)
        # Transmission Weight
        principled_bsdf.inputs[17].default_value = 0.0
        # Coat Weight
        principled_bsdf.inputs[18].default_value = 0.0
        # Coat Roughness
        principled_bsdf.inputs[19].default_value = 0.03
        # Coat IOR
        principled_bsdf.inputs[20].default_value = 1.5
        # Coat Tint
        principled_bsdf.inputs[21].default_value = (1.0, 1.0, 1.0, 1.0)
        # Coat Normal
        principled_bsdf.inputs[22].default_value = (0.0, 0.0, 0.0)
        # Sheen Weight
        principled_bsdf.inputs[23].default_value = 0.0
        # Sheen Roughness
        principled_bsdf.inputs[24].default_value = 0.5
        # Sheen Tint
        principled_bsdf.inputs[25].default_value = (1.0, 1.0, 1.0, 1.0)
        # Emission Color
        principled_bsdf.inputs[26].default_value = (1.0, 1.0, 1.0, 1.0)
        # Emission Strength
        principled_bsdf.inputs[27].default_value = 0.0

        # node Material Output
        material_output = material_image.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        # Displacement
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Thickness
        material_output.inputs[3].default_value = 0.0

        # node Image Texture
        image_texture = material_image.nodes.new("ShaderNodeTexImage")
        image_texture.image = bpy.data.images.get(image_file_name)

        image_texture.extension = 'REPEAT'
        image_texture.image_user.frame_current = 1
        image_texture.image_user.frame_duration = 1
        image_texture.image_user.frame_offset = -1
        image_texture.image_user.frame_start = 1
        image_texture.image_user.tile = 0
        image_texture.image_user.use_auto_refresh = False
        image_texture.image_user.use_cyclic = False
        image_texture.interpolation = 'Linear'
        image_texture.projection = 'FLAT'
        image_texture.projection_blend = 0.0

        # node Mapping
        mapping = material_image.nodes.new("ShaderNodeMapping")
        mapping.name = "Mapping"
        mapping.vector_type = 'POINT'
        # Location
        mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
        # Rotation
        mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Scale
        mapping.inputs[3].default_value = texture_scale

        # node Texture Coordinate
        texture_coordinate = material_image.nodes.new("ShaderNodeTexCoord")
        texture_coordinate.name = "Texture Coordinate"
        texture_coordinate.from_instancer = False

        # Set locations
        image_texture.location = (-578.6414794921875, 310.54150390625)
        mapping.location = (-737.5525512695312, 292.684814453125)
        texture_coordinate.location = (-912.8843994140625, 280.4270935058594)
        principled_bsdf.location = (-251.06985473632812, 334.2558288574219)
        material_output.location = (16.444652557373047, 354.41314697265625)

        # Set dimensions
        image_texture.width, image_texture.height = 240.0, 100.0
        mapping.width, mapping.height = 140.0, 100.0
        texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
        principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
        material_output.width, material_output.height = 140.0, 100.0

        # initialize material_image links
        # principled_bsdf.BSDF -> material_output.Surface
        material_image.links.new(principled_bsdf.outputs[0], material_output.inputs[0])
        # image_texture.Color -> principled_bsdf.Base Color
        material_image.links.new(image_texture.outputs[0], principled_bsdf.inputs[0])
        # texture_coordinate.UV -> mapping.Vector
        material_image.links.new(texture_coordinate.outputs[2], mapping.inputs[0])
        # mapping.Vector -> image_texture.Vector
        material_image.links.new(mapping.outputs[0], image_texture.inputs[0])

        if is_water_node:
            # node Bump
            bump = material_image.nodes.new("ShaderNodeBump")
            bump.name = "Bump"
            bump.invert = False
            # Strength
            bump.inputs[0].default_value = 1.0
            # Distance
            bump.inputs[1].default_value = 1.0
            # Normal
            bump.inputs[3].default_value = (0.0, 0.0, 0.0)
            # Bump Height
            bump.inputs[2].default_value = 0.1

            # node Noise Texture
            noise_texture = material_image.nodes.new("ShaderNodeTexNoise")
            noise_texture.name = "Noise Texture"
            noise_texture.noise_dimensions = '3D'
            noise_texture.normalize = True
            # Vector
            noise_texture.inputs[0].default_value = (0.0, 0.0, 0.0)
            # W
            noise_texture.inputs[1].default_value = 0.0
            # Scale
            noise_texture.inputs[2].default_value = 50.0
            # Detail
            noise_texture.inputs[3].default_value = 2.0
            # Roughness
            noise_texture.inputs[4].default_value = 1.0
            # Lacunarity
            noise_texture.inputs[5].default_value = 2.0
            # Distortion
            noise_texture.inputs[6].default_value = 0.0

            # Set locations
            noise_texture.location = (-568.6123046875, 18.71480369567871)
            bump.location = (-409.5118408203125, 21.734079360961914)

            # Set dimensions
            noise_texture.width, noise_texture.height = 140.0, 100.0
            bump.width, bump.height = 140.0, 100.0

            # initialize material_image links
            # noise_texture.Fac -> bump.Height
            material_image.links.new(noise_texture.outputs[0], bump.inputs[2])
            # bump.Normal -> principled_bsdf.Normal
            material_image.links.new(bump.outputs[0], principled_bsdf.inputs[5])
        return material_image

    material_image = material_image_node_group()
    # apply material_image to object
    plane_object.data.materials.append(mat)

    # uv unwrap, keep the x,y direction
    bpy.ops.object.select_all(action="DESELECT")
    plane_object.select_set(True)
    bpy.context.view_layer.objects.active = plane_object
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0.001)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")


def apply_color_to_collection(
        col_name="Collection", rand_color=None
) -> Tuple[float, float, float, float]:
    """Applies a color to all objects in the collection.

    Returns:
        Tuple[float, float, float, float]: The color that was applied to all
        objects.
    """
    if rand_color is None:
        rand_color = _get_random_color()

    for obj in bpy.data.collections[col_name].objects:
        if obj.type == "MESH":
            _apply_color_to_object(obj, rand_color)
    return rand_color


def place_buildings(buildings_data, col_name='building_assets'):
    glb_to_buildings = {}
    hide_all_collections()
    for idx, building in enumerate(buildings_data):
        if building is None or building.get("layout", None) is None or len(building["layout"]) == 0:
            continue

        # add_meshes_with_holes(f"building_layout_{idx}", building["layout"], "building_layout")
        x_list = [v[0] for v in building["layout"][0]]
        y_list = [v[1] for v in building["layout"][0]]
        center_point = (sum(x_list) / len(x_list), sum(y_list) / len(y_list), 0)

        if building["asset_path"] is None or building["img_path"] is None:
            continue

        annotation_folder = Path(building["img_path"]).parent
        with open(annotation_folder / f"{annotation_folder.name}.json", "r") as fr:
            number_of_floors = json.load(fr)["annotations"]["number of floors"]

        scale_x, scale_y, rotation = building["scale_x"], building["scale_y"], building["rotation"]
        _place_one_object(glb_to_buildings, layout_area=abs(calculate_area(building["layout"][0])),
                          scale=(scale_x, scale_y, (abs(scale_x) + abs(scale_y)) / 2), location=center_point,
                          rotation=(0, 0, rotation), col_name=col_name, obj_name=f"building_asset_{idx}",
                          glb_path=str(building["asset_path"]), floors_number=number_of_floors)
        # break  # for debug
    show_all_collections()
    print("place buildings done")
    for obj_path, building_info in glb_to_buildings.items():
        print(obj_path, building_info["linked_root_objects"])


def copy_ob(ob, parent, collection=bpy.context.scene.collection, name: str = None):
    # copy ob
    copied_obj = ob.copy()
    if name is not None:
        copied_obj.name = name

    copied_obj.parent = parent
    copied_obj.matrix_parent_inverse = ob.matrix_parent_inverse.copy()
    # copy particle settings
    for ps in copied_obj.particle_systems:
        ps.settings = ps.settings.copy()
    collection.objects.link(copied_obj)
    return copied_obj


def tree_copy(ob, root_parent, collection, loaded_objects: list):
    def _recurse(ob, parent, root_parent):
        copied_obj = copy_ob(ob, parent, collection)
        loaded_objects.append(copied_obj)
        if root_parent is not None:
            copied_obj.parent = root_parent
        for child in ob.children:
            _recurse(child, copied_obj, None)

    _recurse(ob, ob.parent, root_parent)


def tree_move(root_obj, tmp_col, real_col):
    def _recurse(obj):
        real_col.objects.link(obj)
        for child in obj.children:
            _recurse(child)

    _recurse(root_obj)

    for obj in tmp_col.objects:
        tmp_col.objects.unlink(obj)


@cache
def calculate_scale_factor(layout_area, scale, bbox_length_x, bbox_length_y):
    scale_factor = sqrt(layout_area / (abs(scale[0] * scale[1]) * bbox_length_x * bbox_length_y))
    return scale_factor


def show_only_collection(col_name):
    # for col in bpy.data.collections:
    #     col.hide_viewport = (col.name != col_name)

    vl_colls = bpy.context.view_layer.layer_collection.children
    for coll in vl_colls:
        if coll.exclude != (coll.name != col_name):
            coll.exclude = (coll.name != col_name)


def hide_all_collections():
    # for col in bpy.data.collections:
    #     col.hide_viewport = True

    vl_colls = bpy.context.view_layer.layer_collection.children
    for coll in vl_colls:
        if not coll.exclude:
            coll.exclude = True


def show_all_collections():
    # for col in bpy.data.collections:
    #     col.hide_viewport = False

    vl_colls = bpy.context.view_layer.layer_collection.children
    for coll in vl_colls:
        if coll.exclude:
            coll.exclude = False


def _place_one_object(
        glb_to_objects_dict: dict,
        layout_area: float, scale: Tuple[float, float, float] = (1, 1, 1),
        location: Optional[Tuple[float, float, float]] = (0, 0, 0),
        rotation: Optional[Tuple[float, float, float]] = (0, 0, 0),  # rotation in radians 弧度制
        col_name: str = "Collection", obj_name: str = "testBuilding0",
        glb_path=None,
        floors_number: int = None
):
    tmp_col = _add_collection("Temp_Collection_For_Placing")
    real_col = _add_collection(col_name)
    show_only_collection("Temp_Collection_For_Placing")

    parent_empty = bpy.data.objects.new(obj_name, None)  # create an empty object
    tmp_col.objects.link(parent_empty)  # link the empty parent to collection

    if glb_path not in glb_to_objects_dict:
        bpy.ops.object.select_all(action="DESELECT")
        try:
            _load_object(glb_path)
        except Exception as e:
            print(f"Error: {e}, failed to load {glb_path}")
            traceback.print_exc()
            return
        loaded_objects = [obj for obj in bpy.context.selected_objects]
        for obj in loaded_objects:
            tmp_col.objects.link(obj)  # link obj to collection
        glb_to_objects_dict.update({glb_path: {"linked_root_objects": [obj_name],
                                               "loaded_objects": loaded_objects}})
        bpy.ops.object.select_all(action="DESELECT")
    else:
        loaded_objects = []
        org_building = bpy.data.objects[glb_to_objects_dict[glb_path]["linked_root_objects"][0]]
        glb_to_objects_dict[glb_path]["linked_root_objects"].append(obj_name)
        for child in org_building.children:
            # loaded_objects.append(child)
            tree_copy(child, parent_empty, tmp_col, loaded_objects)
        bpy.context.view_layer.update()  # update the view layer, avoid error scale
        print(len(loaded_objects), "reused objects")

    bbox_min, bbox_max = _objects_bbox(loaded_objects)
    bbox_length = bbox_max - bbox_min

    offset = -(bbox_min + bbox_max) / 2  # align obj to the center
    offset.z = -bbox_min.z  # align obj to the bottom
    for obj in _get_loaded_root_objects(loaded_objects):
        if obj != parent_empty:
            obj.parent = parent_empty
            obj.location = obj.location + offset  # align obj to the bottom center

    # after the operation above, the origin should be at the bottom center of the building
    bpy.ops.object.select_all(action="DESELECT")

    # The following equation is the derivation of the equality of area before and after scaling
    scale_factor = calculate_scale_factor(layout_area, scale, bbox_length.x, bbox_length.y)

    parent_empty.location = location  # move the building

    if floors_number is None:
        parent_empty.scale = tuple(s * scale_factor for s in scale)  # scale the building
        print(f"layout_area={layout_area}", f"bbox_length={bbox_length}", f"scale={scale}*{scale_factor}")
    else:
        current_height = bbox_length.z
        scaled_height = floors_number * 5  # 5m per floor
        z_factor = scaled_height / current_height
        parent_empty.scale = (scale[0] * scale_factor, scale[1] * scale_factor, z_factor)
        print(f"layout_area={layout_area}", f"bbox_length={bbox_length}",
              f"scale_xy={scale[:-1]}*{scale_factor}", f"scale_z={z_factor}")

    # for XYZ Euler, X is applied on the axis formed after Y and Z rotation
    parent_empty.rotation_euler = Euler(rotation, 'XYZ')  # rotate the building

    tree_move(parent_empty, tmp_col, real_col)  # move added objects to the real collection


def _get_objects_meshes(multi_objs: [bpy.types.Object]) -> Generator[bpy.types.Object, None, None]:
    """Returns all meshes in the scene.

    Yields:
        Generator[bpy.types.Object, None, None]: Generator of all meshes in the scene.
    """
    for obj in multi_objs:
        if isinstance(obj.data, bpy.types.Mesh):
            yield obj


def _objects_bbox(
        multi_objs: [bpy.types.Object], ignore_matrix: bool = False
) -> Tuple[Vector, Vector]:
    """Returns the bounding box of the scene.

    Taken from Shap-E rendering script
    (https://github.com/openai/shap-e/blob/main/shap_e/rendering/blender/blender_script.py#L68-L82)

    Args:
        multi_objs ([bpy.types.Object]): computes the bounding box for the given objects.
        ignore_matrix (bool, optional): Whether to ignore the object's matrix. Defaults
            to False.

    Raises:
        RuntimeError: If there are no objects in the scene.

    Returns:
        Tuple[Vector, Vector]: The minimum and maximum coordinates of the bounding box.
    """
    bbox_min = (math.inf,) * 3
    bbox_max = (-math.inf,) * 3
    found = False
    for obj in _get_objects_meshes(multi_objs):
        found = True
        for coord in obj.bound_box:
            coord = Vector(coord)
            if not ignore_matrix:
                coord = obj.matrix_world @ coord
            bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
            bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))

    if not found:
        raise RuntimeError("no objects in scene to compute bounding box for")

    return Vector(bbox_min), Vector(bbox_max)


def _get_loaded_root_objects(loaded_objects) -> Generator[bpy.types.Object, None, None]:
    """Returns all root objects in loaded objects.

    Yields:
        Generator[bpy.types.Object, None, None]: Generator of all root loaded objects.
    """
    for obj in loaded_objects:
        if not obj.parent:
            yield obj


def _place_object_to_coords(plane_layout_name: str, object_glb_path: str,
                            occupied_area: float, coords: List[Tuple[float, float, float]],
                            col_name: str,
                            glb_to_objects_dict={}):  # used to store the loaded trees, global variable !!!
    hide_all_collections()
    print(f"placing {len(coords)} {col_name} on {plane_layout_name}")
    for idx, coord in enumerate(coords):
        print(f"{idx}/{len(coords)}, name: {plane_layout_name}_{col_name}_{idx}")
        _place_one_object(glb_to_objects_dict, occupied_area, (1, 1, 1), coord, (0, 0, 0),
                          f"{plane_layout_name}_{col_name}",
                          f"{plane_layout_name}_{col_name}_{idx}", object_glb_path, None)
    show_all_collections()


def random_add_objects_on_plane(plane_layout: bpy.types.Object, object_glb_path: str,
                                occupied_area: float = 9, col_name: str = "Collection",
                                distance_min: float = 1.0, density_max: float = 0.2,
                                density: float = 0.001,  # seems no effect
                                density_factor: float = 0.5,  # 0~1
                                random_seed: int = 42):
    # initialize point_distribution node group
    def point_distribution_node_group():
        point_distribution = bpy.data.node_groups.new(type='GeometryNodeTree', name="Point Distribution")
        point_distribution.is_modifier = True

        # initialize point_distribution nodes
        # point_distribution interface
        # Socket Geometry
        geometry_socket = point_distribution.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                                  socket_type='NodeSocketGeometry')
        geometry_socket.attribute_domain = 'POINT'

        # Socket Geometry
        geometry_socket_1 = point_distribution.interface.new_socket(name="Geometry", in_out='INPUT',
                                                                    socket_type='NodeSocketGeometry')
        geometry_socket_1.attribute_domain = 'POINT'

        # node Instance on Points
        instance_on_points = point_distribution.nodes.new("GeometryNodeInstanceOnPoints")
        instance_on_points.name = "Instance on Points"
        # Selection
        instance_on_points.inputs[1].default_value = True
        # Pick Instance
        instance_on_points.inputs[3].default_value = False
        # Instance Index
        instance_on_points.inputs[4].default_value = 0
        # Rotation
        instance_on_points.inputs[5].default_value = (0.0, 0.0, 0.0)
        # Scale
        instance_on_points.inputs[6].default_value = (1.0, 1.0, 1.0)

        # node Realize Instances
        realize_instances = point_distribution.nodes.new("GeometryNodeRealizeInstances")
        realize_instances.name = "Realize Instances"

        # node Mesh Line
        mesh_line = point_distribution.nodes.new("GeometryNodeMeshLine")
        mesh_line.name = "Mesh Line"
        mesh_line.count_mode = 'TOTAL'
        mesh_line.mode = 'OFFSET'
        # Count
        mesh_line.inputs[0].default_value = 1
        # Resolution
        mesh_line.inputs[1].default_value = 1.0
        # Start Location
        mesh_line.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Offset
        mesh_line.inputs[3].default_value = (0.0, 0.0, 1.0)

        # node Group Output
        group_output = point_distribution.nodes.new("NodeGroupOutput")
        group_output.name = "Group Output"
        group_output.is_active_output = True

        # node Group Input
        group_input = point_distribution.nodes.new("NodeGroupInput")
        group_input.name = "Group Input"
        group_input.outputs[1].hide = True

        # node Distribute Points on Faces
        distribute_points_on_faces = point_distribution.nodes.new("GeometryNodeDistributePointsOnFaces")
        distribute_points_on_faces.name = "Distribute Points on Faces"
        distribute_points_on_faces.distribute_method = 'POISSON'
        distribute_points_on_faces.use_legacy_normal = True
        # Selection
        distribute_points_on_faces.inputs[1].default_value = True
        # Distance Min
        distribute_points_on_faces.inputs[2].default_value = distance_min
        # Density Max
        distribute_points_on_faces.inputs[3].default_value = density_max
        # Density
        distribute_points_on_faces.inputs[4].default_value = density
        # Density Factor
        distribute_points_on_faces.inputs[5].default_value = density_factor
        # Seed
        distribute_points_on_faces.inputs[6].default_value = random_seed

        # Set locations
        instance_on_points.location = (248.409912109375, 121.29292297363281)
        realize_instances.location = (415.7618103027344, 113.5146713256836)
        mesh_line.location = (69.47602844238281, 46.95783615112305)
        group_output.location = (583.2474365234375, 71.37263488769531)
        group_input.location = (-278.40863037109375, 25.450664520263672)
        distribute_points_on_faces.location = (-121.09808349609375, 95.45195770263672)

        # Set dimensions
        instance_on_points.width, instance_on_points.height = 140.0, 100.0
        realize_instances.width, realize_instances.height = 140.0, 100.0
        mesh_line.width, mesh_line.height = 140.0, 100.0
        group_output.width, group_output.height = 140.0, 100.0
        group_input.width, group_input.height = 140.0, 100.0
        distribute_points_on_faces.width, distribute_points_on_faces.height = 170.0, 100.0

        # initialize point_distribution links
        # group_input.Geometry -> distribute_points_on_faces.Mesh
        point_distribution.links.new(group_input.outputs[0], distribute_points_on_faces.inputs[0])
        # mesh_line.Mesh -> instance_on_points.Instance
        point_distribution.links.new(mesh_line.outputs[0], instance_on_points.inputs[2])
        # distribute_points_on_faces.Points -> instance_on_points.Points
        point_distribution.links.new(distribute_points_on_faces.outputs[0], instance_on_points.inputs[0])
        # realize_instances.Geometry -> group_output.Geometry
        point_distribution.links.new(realize_instances.outputs[0], group_output.inputs[0])
        # instance_on_points.Instances -> realize_instances.Geometry
        point_distribution.links.new(instance_on_points.outputs[0], realize_instances.inputs[0])
        return point_distribution

    # copy the layout
    bpy.ops.object.select_all(action="DESELECT")
    obj = copy_ob(plane_layout, None, _add_collection(col_name), f"{plane_layout.name}_{col_name}_pos")
    show_only_collection(col_name)
    # add point_distribution node group
    gn_mod = obj.modifiers.new(name="Point Distribution", type='NODES')
    gn_mod.node_group = point_distribution_node_group()

    # get vertices
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj = obj.evaluated_get(depsgraph)
    coords = [(obj.matrix_world @ v.co) for v in obj.data.vertices]
    _place_object_to_coords(plane_layout.name, object_glb_path, occupied_area, coords, col_name)


def random_add_objects_on_border(plane_layout: bpy.types.Object, object_glb_path: str,
                                 occupied_area: float = 4, col_name: str = "Collection",
                                 density_factor: float = 0.05, ):
    coords = [(plane_layout.matrix_world @ v.co) for v in plane_layout.data.vertices]
    coords = random.sample(coords, int(len(coords) * density_factor))
    _place_object_to_coords(plane_layout.name, object_glb_path, occupied_area, coords, col_name)


def interpolation_add_objects_on_border(plane_layout: bpy.types.Object, object_glb_path: str,
                                        distance: float, border_lines: list,
                                        occupied_area: float = 4, col_name: str = "Collection",
                                        ):
    coords = []
    distance_squared = distance ** 2
    for one_line in border_lines:
        if len(one_line) < 3:
            continue
        coords.append(one_line[0])
        start_pos = one_line[0]
        for point in one_line:
            cur_pos = coords[-1]
            if ((point[0] - cur_pos[0]) ** 2 + (point[1] - cur_pos[1]) ** 2 > distance_squared
                    and (point[0] - start_pos[0]) ** 2 + (point[1] - start_pos[1]) ** 2 > distance_squared):
                coords.append(point)
    _place_object_to_coords(plane_layout.name, object_glb_path, occupied_area, coords, col_name)


def _load_object(object_path: str) -> None:
    print(f"_load_object: {object_path}")
    """Loads a model with a supported file extension into the scene.

    Args:
        object_path (str): Path to the model file.

    Raises:
        ValueError: If the file extension is not supported.

    Returns:
        None
    """
    file_extension = object_path.split(".")[-1].lower()
    match file_extension:
        case None:
            raise ValueError(f"Unsupported file type: {object_path}")
        case "3ds":
            addon_name = "io_scene_3ds"
            bpy.ops.preferences.addon_enable(module=addon_name)
            bpy.ops.import_scene.max3ds(filepath=object_path)
            return
        case "dxf":
            addon_name = "io_import_dxf"
            bpy.ops.preferences.addon_enable(module=addon_name)
            bpy.ops.import_scene.dxf(filepath=object_path)
            return
        case "skp":
            dirname = Path.cwd()
            skp_package = dirname / Path("sketchup_importer.zip")
            if sys.platform != "win32":
                raise NotImplementedError("Sketchup importer only support windows.")
            bpy.ops.preferences.addon_install(filepath=str(skp_package.absolute()))
            addon_name = "sketchup_importer"
            bpy.ops.preferences.addon_enable(module=addon_name)
            bpy.ops.import_scene.skp(filepath=object_path)
            return
        case _:
            try:
                print(f"Loading {object_path} with {IMPORT_FUNCTIONS[file_extension]}")
                import_function = IMPORT_FUNCTIONS[file_extension]
            except KeyError:
                raise ValueError(f"Unsupported file type: {object_path}")

    if file_extension in {"glb", "gltf"}:
        import_function(filepath=object_path, merge_vertices=True)
    else:
        import_function(filepath=object_path)


def read_all_vertices(file_path):
    max_xyz = (0, 0, 0)
    with open(file_path, "rb") as file:
        all_vertices_dict = pickle.load(file)
        for key, type in all_vertices_dict.items():
            for i, instance in enumerate(type):
                for j, edge in enumerate(instance):
                    # y,x,z -> x,y,z
                    all_vertices_dict[key][i][j] = [(vertex[1], vertex[0], vertex[2]) for vertex in edge]
                    max_xyz = tuple(max(max_xyz[idx], vertex[idx])
                                    for vertex in all_vertices_dict[key][i][j]
                                    for idx in range(3))
            print(key, len(type), [len(instance) for instance in type])
    return max_xyz, all_vertices_dict


def add_terrain(max_xyz, soil_image_path: str):
    city_center = (max_xyz[0] / 2, max_xyz[1] / 2)
    base_size = max(max_xyz) * 1.0
    base_z = -0.1
    min_point = (city_center[0] - base_size / 2, city_center[1] - base_size / 2)
    corner_points = [
        (min_point[0], min_point[1], base_z),
        (min_point[0] + base_size, min_point[1], base_z),
        (min_point[0] + base_size, min_point[1] + base_size, base_z),
        (min_point[0], min_point[1] + base_size, base_z),
    ]
    print("terrain:", corner_points)
    # hide_all_collections()
    add_meshes_with_holes("terrain", [corner_points], "Collection")
    apply_image_to_plane(soil_image_path, bpy.data.objects["terrain"])
    # show_all_collections()


def load_image(image_path: str):
    if Path(image_path).is_file():
        bpy.ops.image.open(filepath=image_path)
    else:
        print(f"Texture image not found: {image_path}")


def add_world_hdri(world_hdri_path: str):
    world = bpy.context.scene.world
    world.use_nodes = True
    world_nodes = world.node_tree.nodes
    world_links = world.node_tree.links

    # Clear default nodes
    world_nodes.clear()

    # Add Background node
    bg_node = world_nodes.new("ShaderNodeBackground")

    # Add Environment Texture node
    env_node = world_nodes.new("ShaderNodeTexEnvironment")
    env_node.image = bpy.data.images.load(world_hdri_path)
    env_node.location = (-200, 0)

    # Add Output node
    out_node = world_nodes.new(type='ShaderNodeOutputWorld')
    out_node.location = (200, 0)

    # Link nodes
    world_links.new(env_node.outputs["Color"], bg_node.inputs["Color"])
    world_links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])


def get_file_from_folder(folder_path, extensions=None, mode='default'):
    """Get a file path from a folder based on specified mode.
    
    Args:
        folder_path: Path to folder containing files
        extensions: List of valid file extensions (e.g. ['.jpg', '.png'])
        mode: 'default' to get first file, 'random' for random selection
        
    Returns:
        Path object for selected file or None if no valid files found
    """
    if folder_path is None:
        return None
        
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        print(f"Warning: {folder_path} is not a valid directory")
        return None
        
    # Get all files with specified extensions
    if extensions:
        files = []
        for ext in extensions:
            files.extend(folder.glob(f"*{ext}"))
    else:
        files = list(folder.iterdir())
        
    if not files:
        print(f"Warning: No valid files found in {folder_path}")
        return None
        
    if mode == 'random':
        return random.choice(files)
    else:  # default mode
        return sorted(files)[0]


def citycraft(
        pickle_path_1=None,
        pickle_path_2=None,
        grass_image_folder=None,
        water_image_folder=None,
        stone_image_folder=None, 
        brick_image_folder=None,
        asphalt_image_folder=None,
        soil_image_folder=None,
        world_hdri_folder=None,
        tree_glb_folder=None,
        grass_glb_folder=None,
        lamp_glb_folder=None,
        light_glb_folder=None,
        flower_glb_folder=None,
        stuff_glb_folder=None,
        selection_mode='default',  # 'default' or 'random'
        ignore_keys=None,
        add_side_line_func=None
):
    # Get specific files from folders
    grass_image_path = get_file_from_folder(grass_image_folder, ['.jpg', '.png'], selection_mode)
    water_image_path = get_file_from_folder(water_image_folder, ['.jpg', '.png'], selection_mode)
    stone_image_path = get_file_from_folder(stone_image_folder, ['.jpg', '.png'], selection_mode)
    brick_image_path = get_file_from_folder(brick_image_folder, ['.jpg', '.png'], selection_mode)
    asphalt_image_path = get_file_from_folder(asphalt_image_folder, ['.jpg', '.png'], selection_mode)
    soil_image_path = get_file_from_folder(soil_image_folder, ['.jpg', '.png'], selection_mode)
    world_hdri_path = get_file_from_folder(world_hdri_folder, ['.hdr'], selection_mode)
    tree_glb_path = get_file_from_folder(tree_glb_folder, ['.glb'], selection_mode)
    grass_glb_path = get_file_from_folder(grass_glb_folder, ['.glb'], selection_mode)
    lamp_glb_path = get_file_from_folder(lamp_glb_folder, ['.glb'], selection_mode)
    light_glb_path = get_file_from_folder(light_glb_folder, ['.glb'], selection_mode)
    flower_glb_path = get_file_from_folder(flower_glb_folder, ['.glb'], selection_mode)
    stuff_glb_path = get_file_from_folder(stuff_glb_folder, ['.glb'], selection_mode)

    # Convert Path objects to strings for compatibility
    grass_image_path = str(grass_image_path) if grass_image_path else None
    water_image_path = str(water_image_path) if water_image_path else None
    stone_image_path = str(stone_image_path) if stone_image_path else None
    brick_image_path = str(brick_image_path) if brick_image_path else None
    asphalt_image_path = str(asphalt_image_path) if asphalt_image_path else None
    soil_image_path = str(soil_image_path) if soil_image_path else None
    world_hdri_path = str(world_hdri_path) if world_hdri_path else None
    tree_glb_path = str(tree_glb_path) if tree_glb_path else None
    grass_glb_path = str(grass_glb_path) if grass_glb_path else None
    lamp_glb_path = str(lamp_glb_path) if lamp_glb_path else None
    light_glb_path = str(light_glb_path) if light_glb_path else None
    flower_glb_path = str(flower_glb_path) if flower_glb_path else None
    stuff_glb_path = str(stuff_glb_path) if stuff_glb_path else None

    for image_path in [grass_image_path, water_image_path, stone_image_path, brick_image_path,
                       asphalt_image_path, soil_image_path]:
        load_image(image_path)
    add_world_hdri(world_hdri_path)

    class_colors = {
        "ground": [85, 107, 47, 255],  # ground -> OliveDrab
        "vegetation": [0, 255, 0, 255],  # vegetation -> Green
        "building": [255, 165, 0, 255],  # building -> orange
        "rail": [255, 0, 255, 255],  # rail -> Magenta
        "road": [200, 200, 200, 255],  # road ->  grey
        "footpath": [255, 255, 0, 255],  # Footpath  ->  deeppink
        "water": [0, 191, 255, 255],  # water ->  skyblue
    }

    max_xyz, all_vertices_dict = read_all_vertices(pickle_path_1)
    hide_all_collections()
    add_terrain(max_xyz, soil_image_path)
    for key in all_vertices_dict.keys():
        object_all_meshes = all_vertices_dict[key]
        print(key, len(object_all_meshes))

        if ignore_keys is not None and key in ignore_keys:
            continue

        # if key != "footpath" and key != "road":
        #     continue  # debug

        for i, one_layout_lines in enumerate(object_all_meshes):
            if len(one_layout_lines) == 0:
                continue

            try:
                obj = add_meshes_with_holes(f"{key}_{i}", one_layout_lines, key)
                if key == "vegetation":
                    apply_image_to_plane(grass_image_path, obj, )
                    random_add_objects_on_plane(obj, flower_glb_path, 16, "flower",
                                                distance_min=0.2, density_factor=0.1, random_seed=2042)
                    random_add_objects_on_plane(obj, grass_glb_path, 25, "grass",
                                                distance_min=0.2, density_factor=0.2, random_seed=2077)
                    random_add_objects_on_plane(obj, tree_glb_path, 81, "tree",
                                                distance_min=3, density_factor=0.05)
                elif key == "water":
                    apply_image_to_plane(water_image_path, obj, is_water_node=True)
                elif key == "footpath":
                    apply_image_to_plane(brick_image_path, obj, texture_scale=(100.0, 100.0, 1.0))
                    interpolation_add_objects_on_border(obj, lamp_glb_path, 20, one_layout_lines, 1, "lamp")
                    random_add_objects_on_border(obj, flower_glb_path, 9, "flower")
                elif key == "road":
                    apply_image_to_plane(asphalt_image_path, obj)
                    interpolation_add_objects_on_border(obj, light_glb_path, 20, one_layout_lines, 11, "light")
                    if add_side_line_func is not None:
                        for j, one_line in enumerate(one_layout_lines):
                            one_line = [(x, y, 0.01) for x, y, _ in one_line]
                            add_side_line_func(one_line, f"{key}_{i}_line_{j}")
                elif key == "ground":
                    apply_image_to_plane(stone_image_path, obj)
                    random_add_objects_on_plane(obj, stuff_glb_path, 1600, "stuff",
                                                distance_min=10, density_factor=0.01)
                else:
                    color = apply_color_to_collection(
                        key, [c / 255 for c in class_colors[key]]
                    )
                    print("color", color)
            except Exception as e:
                print(i, traceback.format_exc())
                continue
        print(key, "done")
    show_all_collections()
    print("citycraft all done")
    return


def read_building_transforms(file_path):
    with open(file_path, "rb") as file:
        building_transforms_list = pickle.load(file)

    for i, building in enumerate(building_transforms_list):
        if building is None:
            continue
        # y,x -> x,y
        building["scale_x"], building["scale_y"] = building["scale_y"], building["scale_x"]
        building["rotation"] = -building["rotation"]

        for j, edge in enumerate(building["layout"]):
            # y,x,z -> x,y,z
            building_transforms_list[i]["layout"][j] = [(vertex[1], vertex[0], vertex[2]) for vertex in edge]
    return building_transforms_list


def main(pickle_path1: str, pickle_path2: str, add_side_line_func=None):
    reset_scene()
    ignore_keys = []  # for debug
    ignore_keys.append("building")
        
    citycraft(
        pickle_path_1=pickle_path1,
        pickle_path_2=pickle_path2,
        # textures 
        grass_image_folder="./textures/grass",
        water_image_folder="./textures/water",
        stone_image_folder="./textures/stone",
        brick_image_folder="./textures/brick",
        asphalt_image_folder="./textures/asphalt",
        soil_image_folder="./textures/soil",
        # extra assets
        world_hdri_folder="./extra_assets/world_hdri",
        tree_glb_folder="./extra_assets/tree",
        grass_glb_folder="./extra_assets/grass",
        lamp_glb_folder="./extra_assets/lamp",
        light_glb_folder="./extra_assets/light",
        flower_glb_folder="./extra_assets/flower",
        stuff_glb_folder="./extra_assets/stuff",
        ignore_keys=ignore_keys,
        add_side_line_func=add_side_line_func
    )

    place_buildings(read_building_transforms(pickle_path2))

def reset_scene() -> None:
    """Resets the scene to a clean state.

    Returns:
        None
    """
    # delete everything that isn't part of a camera or a light
    for obj in bpy.data.objects:
        if obj.type not in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    # delete all the materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material, do_unlink=True)

    # delete all the textures
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture, do_unlink=True)

    # delete all the images
    for image in bpy.data.images:
        bpy.data.images.remove(image, do_unlink=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pickle_file1",
        type=str,
        default=None,
        help="Path to the project file to be saved.",
    )

    parser.add_argument(
        "--pickle_file2",
        type=str,
        default=None,
        help="Path to the project file to be saved.",
    )

    parser.add_argument(
        "--use_roadcurve_py",
        action="store_true",
        help="whether to use roadcurve",
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="Path to the project file to be saved.",
    )

    try:
        argv = sys.argv[sys.argv.index("--") + 1:]
        args = parser.parse_args(argv)
    except ValueError:
        print("No -- found in argv, now use default args")
        args = parser.parse_args()
    print("blender script args:", args)

    try:
        add_side_line_func = None
        if args.use_roadcurve_py:
            sys.path.append(Path.cwd().as_posix())  # current path has the roadcurve script
            from blender4_script_roadcurve import add_road_side_line

            add_side_line_func = add_road_side_line
       
        main(args.pickle_file1, args.pickle_file2, add_side_line_func)

        if args.output_file is not None:
            # auto pack
            bpy.ops.file.autopack_toggle()
            bpy.ops.wm.save_mainfile(filepath=args.output_file)
            # bpy.ops.wm.save_as_mainfile(filepath=args.output_file)
    except Exception as e:
        print(traceback.format_exc())

from collections import deque
from time import time
from multiprocessing import Pool
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from numba import njit, prange
from scipy import ndimage
from scipy.optimize import minimize, NonlinearConstraint, basinhopping
from scipy.spatial.transform import Rotation
from shapely.geometry import Polygon
from torchvision import transforms
import torch
from typing import Tuple
import itertools
from copy import deepcopy
import sys
from tqdm import tqdm
from pathlib import Path
import subprocess

sys.setrecursionlimit(300 ** 2)
print("recursion limit set to", sys.getrecursionlimit())

NUM_WORKERS = 8

CLASS_NAMES = (
    'ground',
    'vegetation',
    'building',
    'rail',
    'road',
    'footpath',
    'water'
)

PALETTE = (
    (0, 0, 0),  # ground -> OliveDrab
    (0, 255, 0),  # vegetation -> Green
    (255, 165, 0),  # building -> orange
    (255, 0, 255),  # rail -> Magenta
    (200, 200, 200),  # road ->  grey
    (255, 255, 0),  # Footpath  ->  deeppink
    (0, 191, 255)  # water ->  skyblue
)


# helper functions
def get_palette():
    return PALETTE


def print_class_info(label: np.ndarray):
    for i in range(len(CLASS_NAMES)):
        print('class: ', CLASS_NAMES[i], ', total points: ', (label == i).sum())


def throw_error(e):
    raise e


def rgb_to_onehot(rgb):
    """
    Converts a segmentation mask (H, W, C) to (H, W, K) where the last dim is a one
    hot encoding vector, C is usually 1 or 3, and K is the number of class.
    """
    semantic_map = []
    palette = get_palette()

    for color in palette:
        equality = np.equal(rgb, color)
        class_map = np.all(equality, axis=-1)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=-1).astype(np.uint8)
    return semantic_map


# conver a H x W input label to a H x W x 3 RGB array
def label_to_image(label: np.ndarray):
    palette = get_palette()
    new_image = np.zeros((label.shape[0], label.shape[1], 3), dtype=np.uint8)
    for i in range(len(palette)):
        new_image[label == i] = palette[i]

    return new_image  # helper functions


def get_object_locations(labeled_mask, num_features):
    objects = []
    for i in range(1, num_features + 1):
        indices = np.where(np.array(labeled_mask) == i)
        # print(indices)
        objects.append(list(zip(indices[0], indices[1])))
    return objects


# get locations of points where mask == target and on the edge
# apply this function to the building mask we can get edges of the buildings
def get_edge_points(mask, target=1, reverse_bool=False):
    mask = np.array(mask, dtype=np.float32)
    if len(mask.shape) == 2:
        mask = np.expand_dims(mask, axis=-1)
    target = np.array(target, dtype=np.float32, ndmin=1)
    # print("mask shape", mask.shape, "target", target, "reverse_bool", reverse_bool)

    if len(mask.shape) == 3:
        h, w, dim = mask.shape
        assert dim == len(target)
    else:
        raise ValueError(f"mask shape {mask.shape} not supported")

    @njit
    def at_boundary(i, j):
        return i == 0 or i == h - 1 or j == 0 or j == w - 1

    @njit
    def at_intersection(i, j):
        if reverse_bool:
            return (np.array_equal(mask[i - 1, j], target) or
                    np.array_equal(mask[i + 1, j], target) or
                    np.array_equal(mask[i, j - 1], target) or
                    np.array_equal(mask[i, j + 1], target))
        else:
            return not (np.array_equal(mask[i - 1, j], target) and
                        np.array_equal(mask[i + 1, j], target) and
                        np.array_equal(mask[i, j - 1], target) and
                        np.array_equal(mask[i, j + 1], target))

    @njit(parallel=True)  # print() or type() functions are not allowed in njit
    def check_all():
        is_edge_point = np.zeros((h, w), dtype=np.bool_)
        for i in prange(h):
            for j in prange(w):
                if reverse_bool:
                    if not np.array_equal(mask[i, j], target) and (at_boundary(i, j) or at_intersection(i, j)):
                        is_edge_point[i, j] = True
                else:
                    if np.array_equal(mask[i, j], target) and (at_boundary(i, j) or at_intersection(i, j)):
                        is_edge_point[i, j] = True
        return is_edge_point

    # start_time = time()
    edge_points = np.argwhere(check_all())
    # end_time = time()
    # to [(x,y), (x,y), ...]
    edge_points = [tuple(x) for x in edge_points]
    # print("edge_points", len(edge_points))
    # print(f"get_edge_points time use {time() - start_time}={end_time - start_time}+{time() - end_time}")
    return edge_points


def find_closest_point(current_point, all_points, longest_threshold):
    """Find the closest point to the current point."""
    min_distance = float('inf')
    closest_point = None

    for p in all_points:
        distance = (p[0] - current_point[0]) ** 2 + (p[1] - current_point[1]) ** 2
        if distance < min_distance:
            min_distance = distance
            closest_point = p

    # set a threshold to avoid far points
    if min_distance > longest_threshold:  # ▲x^2 + ▲y^2 > threshold
        if min_distance < float('inf'):
            print(f"longest_threshold {longest_threshold} < min_distance {min_distance}")
        return None
    else:
        return closest_point


def remove_duplicate_points(ordered_points):
    # remove verts on the same line, point: tuple(x,y)
    if len(ordered_points) >= 3:
        index_to_remove = []
        # iterate from the end to the beginning
        for idx in range(len(ordered_points) - 3, -1, -1):
            x1, y1 = ordered_points[idx]
            x2, y2 = ordered_points[idx + 1]
            x3, y3 = ordered_points[idx + 2]
            if (x1 + x3 == 2 * x2) and (y1 + y3 == 2 * y2):
                index_to_remove.append(idx + 1)
        for idx in index_to_remove:
            ordered_points.pop(idx)
    return ordered_points


def get_connected_graph(shape, nodes) -> np.ndarray:
    connected_graph = np.zeros(shape[:2], dtype=np.int8)  # create a adjacent matrix
    for n in nodes:
        connected_graph[n[0], n[1]] = 1
    return connected_graph


def label_connected_area(connected_graph, connected_structure=None):
    # time use
    # start = time()
    labeled_area, num_area = ndimage.label(connected_graph, structure=connected_structure)
    # print("label time use", time() - start)
    return labeled_area, num_area


def get_points_2_neighbor(all_points, connected_graph) -> list:
    def caculate_neighbor(x, y):
        number_1s = 0
        x_list, y_list = [x], [y]
        if x - 1 >= 0:
            x_list.append(x - 1)
        if x + 1 < connected_graph.shape[0]:
            x_list.append(x + 1)
        if y - 1 >= 0:
            y_list.append(y - 1)
        if y + 1 < connected_graph.shape[1]:
            y_list.append(y + 1)
        for i, j in itertools.product(x_list, y_list):
            number_1s += connected_graph[i][j]
        return number_1s - 1  # 减去自己

    points_2_neighbor = []
    for p in all_points:
        if caculate_neighbor(p[0], p[1]) == 2:
            points_2_neighbor.append(p)
    return points_2_neighbor


def dfs_order_points(connected_graph: np.ndarray, start_point: Tuple[int, int]):
    complete_paths = []
    travered_points: deque = deque()

    def dfs_search_graph(x: int, y: int):
        if (x >= connected_graph.shape[0] or y >= connected_graph.shape[1] or
                x < 0 or y < 0 or connected_graph[x][y] == 0):
            # leaf node next to start point
            start_x, start_y = travered_points[0]
            last_x, last_y = travered_points[-1]
            # last point close to start point, consider as complete path
            if (last_x - start_x) ** 2 + (last_y - start_y) ** 2 <= 3:
                complete_paths.append(list(travered_points))
            return

        assert connected_graph[x][y] == 1, "It must be a new edge point"
        connected_graph[x][y] = 0  # mark it is visited
        travered_points.append((x, y))
        # print(f"travered_points {travered_points}")
        for next_x, next_y in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),  # 先十字搜索，比斜角更近
                               (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]:  # 对角线
            dfs_search_graph(next_x, next_y)
        travered_points.pop()

    dfs_search_graph(start_point[0], start_point[1])
    return complete_paths


def order_points(all_edge_points: list, shape, ignore_hole=False, compress: bool = True):
    """Order points by finding the closest neighbor iteratively."""

    # create a graph with the same size as the image
    all_connected_graph = get_connected_graph(shape, all_edge_points)
    connected_structure = [[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]]
    # 用连通区域分离每一条边
    labeled_graph, num_edges = label_connected_area(all_connected_graph, connected_structure)
    labeled_edges = get_object_locations(labeled_graph, num_edges)  # find all the edges

    def method_new():
        ordered_edges = []
        for one_edge_points in labeled_edges:  # connect all the edges
            connected_graph = get_connected_graph(shape, one_edge_points)
            points_2_neighbor = get_points_2_neighbor(one_edge_points, connected_graph)
            if len(points_2_neighbor) <= 0:
                continue

            ordered_points_tried = []
            for i in range(10):  # try for several times
                start_point = points_2_neighbor[np.random.randint(0, len(points_2_neighbor))]
                complete_paths: list = dfs_order_points(deepcopy(connected_graph), start_point)
                travered_points = max(complete_paths, key=lambda x: len(x))
                ordered_points_tried.append(travered_points)
                if len(travered_points) / len(one_edge_points) <= 0.95:
                    continue
                else:
                    if i > 0:
                        print(
                            f"ordered points {[len(x) for x in ordered_points_tried]} / all points {len(one_edge_points)}, retried {i} times")
                    break
            ordered_points = max(ordered_points_tried, key=lambda x: len(x))
            if compress:
                ordered_points = remove_duplicate_points(ordered_points)
            if len(ordered_points) < 3:
                continue  # remove lines with less than 3 points
            ordered_edges.append(ordered_points)
        return ordered_edges

    def method_old():
        ordered_edges = []
        for one_edge_points in labeled_edges:  # connect all the edges
            ordered_points = [one_edge_points.pop()]
            while one_edge_points:
                closest_point = find_closest_point(ordered_points[-1], one_edge_points,
                                                   longest_threshold=20)
                if closest_point is None:
                    break  # 太远的点不要
                ordered_points.append(closest_point)
                one_edge_points.remove(closest_point)
            if compress:
                ordered_points = remove_duplicate_points(ordered_points)
            if len(ordered_points) < 3:
                continue  # remove lines with less than 3 points
            ordered_edges.append(ordered_points)
        return ordered_edges

    if 1:  # 新方法
        ordered_edges = method_new()
    else:
        ordered_edges = method_old()

    if ignore_hole:
        # return the longest edge
        ordered_points = max(ordered_edges, key=lambda x: len(x))
        return [ordered_points]
    else:
        # sort the edge in order of the number of points (longest first)
        ordered_edges.sort(key=lambda x: len(x), reverse=True)
        return ordered_edges


def intersection_of_tuples(list1, list2):
    intersection_set = set(list1).intersection(set(list2))
    return list(intersection_set)


def create_edges_vertices(buildings, edge_points, shape,
                          description: str, compress: bool = True):
    buildings_edges = []
    for building in tqdm(buildings, desc=description):
        building_edge_points = intersection_of_tuples(building, edge_points)
        one_building_edges = order_points(building_edge_points, shape, ignore_hole=False, compress=compress)
        buildings_edges.append(one_building_edges)
    return buildings_edges


def add_third_element(tuples):
    return [(x, y, 0) for x, y in tuples]


def load_image(img_path: Path, alpha_color=None, visualize=False):
    def alpha_to_color(image):
        image = np.array(image)
        r, g, b, a = np.rollaxis(image, axis=-1)
        r[a == 0] = alpha_color[0]
        g[a == 0] = alpha_color[1]
        b[a == 0] = alpha_color[2]
        image = np.dstack([r, g, b, a])
        return Image.fromarray(image, 'RGBA')

    # setting the origin to the lower left, the default is the upper left
    image = Image.open(img_path).transpose(Image.FLIP_TOP_BOTTOM)

    if alpha_color is not None:
        image = alpha_to_color(image)
    image = image.convert("RGB")
    if visualize:
        show_image(image)
    return np.array(image)


def show_image(image_array, gray=False):
    plt.xlabel('x')
    plt.ylabel('y')
    plt.imshow(image_array, origin='lower', cmap='gray' if gray else None)
    plt.show()


def save_image(image_array, file_name):
    # setting the origin to the upper left
    Image.fromarray((image_array * 255).astype(np.uint8)).transpose(Image.FLIP_TOP_BOTTOM).save(file_name)
    print("saved image", file_name)


def scale_image(image, ideal_size):
    transform = transforms.Resize(size=(ideal_size, ideal_size),
                                  interpolation=transforms.InterpolationMode.NEAREST_EXACT)
    image = torch.from_numpy(image)
    image = image.permute(2, 0, 1)
    image = transform(image)
    image = image.permute(1, 2, 0)
    return np.array(image)


def visualize_edge_points(shape, edge_points):
    test_edge_image = np.zeros(shape[:2])  # create a blank image with the same size as the original image
    for p in edge_points:
        test_edge_image[p[0], p[1]] = 1
    show_image(test_edge_image, gray=True)
    save_image(test_edge_image, f"./output/edge_{len(edge_points)}.png")


# separate instances, create a mask for each class
def seperate_instances(masks, compress_edge: bool = True):
    all_vertices_dict = {}
    for i, mask in enumerate(masks):
        print(f"Processing class {CLASS_NAMES[i]}")
        labeled_mask, num_features = label_connected_area(mask)
        objects = get_object_locations(labeled_mask, num_features)
        edge_points = get_edge_points(mask)
        buildings_edges = create_edges_vertices(objects, edge_points, mask.shape,
                                                CLASS_NAMES[i], compress_edge)
        edges_corrected = []
        for edges in buildings_edges:
            edges_corrected.append([add_third_element(edge) for edge in edges])
        all_vertices_dict.update({CLASS_NAMES[i]: edges_corrected})

    return all_vertices_dict


def rotate_polygon(polygon: Polygon, angle: float) -> Polygon:
    """Rotate a Shapely Polygon by a given angle."""
    rotation_matrix = Rotation.from_euler('z', angle)
    rotated_polygon = rotation_matrix.apply(np.array(polygon.exterior.coords))
    rotated_polygon = Polygon(rotated_polygon)
    return rotated_polygon


def scale_polygon(polygon: Polygon, scale_factor_x: float, scale_factor_y: float) -> Polygon:
    """Scale a Shapely Polygon by a given factor."""

    scaled_polygon = np.array(polygon.exterior.coords)
    scaled_polygon[:, 0] *= scale_factor_x
    scaled_polygon[:, 1] *= scale_factor_y
    scaled_polygon = Polygon(scaled_polygon)
    return scaled_polygon


def move_polygon(polygon: Polygon, moved_center: Tuple[float, float, float]) -> Polygon:
    """Move a Shapely Polygon to the given center point."""
    current_center = np.array(polygon.centroid.coords).squeeze()
    current_center = np.concatenate([current_center, [0]])
    move_vector = np.array(moved_center) - current_center
    moved_polygon = np.array(polygon.exterior.coords) + move_vector
    moved_polygon = Polygon(moved_polygon)
    return moved_polygon


def transform_polygon(polygon: Polygon, polygon_center: Tuple[float, float, float],
                      scale_factor_x: float,
                      scale_factor_y: float,
                      rotation_angle: float) -> Polygon:
    """Transform a Shapely Polygon by scaling and rotating."""
    polygon = scale_polygon(polygon, scale_factor_x, scale_factor_y)
    polygon = rotate_polygon(polygon, rotation_angle)
    polygon = move_polygon(polygon, polygon_center)
    return polygon


def find_best_matching(origin_shape: Polygon, target_shape: Polygon):
    polygon = move_polygon(origin_shape, (0, 0, 0))
    target_center = np.array(target_shape.centroid.coords).squeeze()
    target_center = np.concatenate([target_center, [0]])

    def iou_with_target(transformed_shape: Polygon):
        intersection_area = transformed_shape.intersection(target_shape).area
        union_area = transformed_shape.union(target_shape).area
        return intersection_area / union_area
    
    def matching_metric(params):
        scale_factor_x, scale_factor_y, rotation_angle = params
        transformed_shape = transform_polygon(polygon, target_center,
                                              scale_factor_x, scale_factor_y, rotation_angle)
        return -iou_with_target(transformed_shape)  # loss_function

    def constraint_function(x):
        if x[0] == 0:
            return 0
        elif x[1] == 0:
            return 4
        return np.abs(x[0] / x[1])

    iou_list = []
    constraints = NonlinearConstraint(constraint_function, lb=0.3, ub=3)
    for initial_params in [[-1.0, -1.0, 0.0], [1.0, 1.0, 0.0], [-1.0, 1.0, 0.0], [1.0, -1.0, 0.0]]:
        match 1:
            case 0:
                result = minimize(matching_metric, initial_params, method="COBYLA", constraints=constraints)
            case 1:
                result = minimize(matching_metric, initial_params, method="Powell")
            case 2:
                result = basinhopping(matching_metric, initial_params)
            case _:
                raise ValueError("find_best_matching method not supported")
        scale_x, scale_y, rotation_angle = result.x
        transformed_shape = transform_polygon(origin_shape, target_center,
                                              scale_x, scale_y, rotation_angle)
        area_iou = iou_with_target(transformed_shape)
        iou_list.append({"iou": area_iou, "scale_x": scale_x, "scale_y": scale_y,
                         "rotation": rotation_angle, "shape": transformed_shape, })
    return max(iou_list, key=lambda x: x["iou"])


def get_asset_edge(top_view_image_path: Path, background_color=(0, 0, 0), visualize=False, compress: bool = True):
    image_origin_BEV = load_image(top_view_image_path, background_color, visualize)
    
    image_origin_edge = get_edge_points(image_origin_BEV, background_color, True)
    if visualize:
        visualize_edge_points(image_origin_BEV.shape, image_origin_edge)

    image_ordered_edge = order_points(image_origin_edge, image_origin_BEV.shape,
                                      ignore_hole=True, compress=compress)[0]
    if visualize:
        visualize_edge_points(image_origin_BEV.shape, image_ordered_edge)

    return image_ordered_edge


def load_one_asset_info(args):
    asset_id, assets_folder, assets_renders_folder = args

    asset_path = Path(f"{assets_folder}/{asset_id}.glb")
    img_path = Path(f"{assets_renders_folder}/{asset_id}.glb/002.png")
    if not img_path.exists() or not asset_path.exists():
        print(f"img_path {img_path} or asset_path {asset_path} not exists")
        return {asset_id: {"asset_path": None, "asset_edge": None, "img_path": None, }}

    asset_edge = get_asset_edge(img_path)
    return {asset_id: {"asset_path": asset_path, "img_path": img_path, "asset_edge": asset_edge}}


def handle_planning(selected_buildings_dict,
                    assets_folder=None,
                    assets_renders_folder=None):
    selected_buildings = []
    all_asset_ids = set()
    for idx in tqdm(range(len(selected_buildings_dict))):
        asset_candidates = selected_buildings_dict[str(idx)]["asset candidates"]
        selected_buildings.append(asset_candidates)
        all_asset_ids.update(asset_candidates)

    def task_data_generator():
        for asset_id in all_asset_ids:
            yield asset_id, assets_folder, assets_renders_folder

    my_pool = Pool(NUM_WORKERS)
    result = my_pool.imap(load_one_asset_info, task_data_generator())
    assets_info = {}
    for asset_info in tqdm(result, total=len(all_asset_ids)):
        assets_info.update(asset_info)
    my_pool.close()
    my_pool.join()

    return selected_buildings, assets_info


def best_match_asset(target_shape, candidate_ids, assets_info, random_asset=True):
    best_iou, best_asset_id = None, None
    for asset_id in candidate_ids:

        if random_asset:
            asset_id = np.random.choice(candidate_ids)

        asset_edge = assets_info[asset_id]["asset_edge"]
        if asset_edge is None:
            print(f"asset_id {asset_id} not found")
            continue
        asset_shape = Polygon(add_third_element(asset_edge))
        current_iou = find_best_matching(asset_shape, target_shape)
        if best_iou is None or current_iou["iou"] > best_iou["iou"]:
            best_iou = current_iou
            best_asset_id = asset_id

        if random_asset:
            break
    return best_iou, best_asset_id


def match_one_building(args):
    one_building_edges, candidate_ids, assets_info, random_asset = args

    if len(one_building_edges) == 0:
        return None

    target_shape = Polygon(one_building_edges[0])

    best_iou, best_asset_id = best_match_asset(target_shape, candidate_ids, assets_info, random_asset)

    if best_iou is not None:
        return {"layout": one_building_edges,
                "asset_path": assets_info[best_asset_id]["asset_path"],
                "img_path": assets_info[best_asset_id]["img_path"],
                "scale_x": best_iou["scale_x"], "scale_y": best_iou["scale_y"],
                "rotation": best_iou["rotation"]}
    else:
        print("Warning!!!!!!!!!No asset found for building!!!!!!!!!!!")
        return {"layout": one_building_edges,
                "asset_path": None, "img_path": None,
                "scale_x": 0, "scale_y": 0, "rotation": 0}


def find_building_transforms(all_buildings_vertices: list, selected_buildings: list, assets_info: dict,
                             random_asset: bool = True):
    def task_data_generator():
        for one_building_edges, candidate_ids in zip(all_buildings_vertices, selected_buildings, strict=True):
            yield one_building_edges, candidate_ids, assets_info, random_asset

    my_pool = Pool(NUM_WORKERS)
    result = my_pool.imap(match_one_building, task_data_generator())
    building_transforms_list = list(tqdm(result, total=len(all_buildings_vertices)))
    my_pool.close()
    my_pool.join()

    return building_transforms_list


def save_blender_project(
        target_file: str,
        pkl_v1: str = None,
        pkl_v2: str = None,
        citygen_version: int = None,
        use_roadcurve_py: bool = False,
        bash_runner: str = "bash",
        blender_path: str = "../blender-4.0.2-linux-x64/blender",
        placing_timeout: int = 3600 * 3  # seconds
):
    if Path(target_file).is_file():
        print(f"{target_file} exists!!!, do nothing")
        return

    args = f" --output_file '{target_file}'"
    if pkl_v1 is not None:
        args += f" --pickle_file1 '{pkl_v1}'"
    if pkl_v2 is not None:
        args += f" --pickle_file2 '{pkl_v2}'"
    if citygen_version is not None:
        args += f" --citygen_version {citygen_version}"
    if use_roadcurve_py:
        args += " --use_roadcurve_py"

    # get the command to run
    command = f"{blender_path} --background --python blender4_script_visualization.py -- {args}"
    print(command)

    # render the object
    subprocess.run(
        [bash_runner, "-c", command],
        timeout=placing_timeout,
        check=True,
        #cwd=Path.cwd()/Path("render_scene"),
        cwd=Path.cwd(),
    )


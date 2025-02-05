import os
import json
import pickle
from pathlib import Path
import argparse
import numpy as np
from render_scene_utils import *


def step_edge(image_path: Path, all_vertices_path: Path, compress_edge: bool = True):
    image_rgb = load_image(image_path, visualize=False)
    print(image_rgb.shape)
    ideal_size = image_rgb.shape[0] if image_rgb.shape[0] > image_rgb.shape[1] else image_rgb.shape[1]
    image_rgb = scale_image(image_rgb, ideal_size)
    print(image_rgb.shape)
    onehot = rgb_to_onehot(image_rgb)
    label: np.ndarray = np.argmax(onehot, axis=2)
    print_class_info(label)

    palette = get_palette()
    masks = []
    for i in range(len(palette)):
        masks.append(label == i)

    all_vertices_dict = seperate_instances(masks, compress_edge)
    with open(all_vertices_path, 'wb') as fw:
        pickle.dump(all_vertices_dict, fw)

    for k, v in all_vertices_dict.items():
        print(k, len(v), [len(e) for e in v])
    
    return all_vertices_dict


def step_match(all_vertices_dict: dict, building_transforms_path: Path, selected_buildings_path: Path,
               assets_folder: Path, assets_renders_folder: Path, random_asset: bool = True):
    
    with open(selected_buildings_path, 'rb') as fr:
        selected_buildings_dict: dict = pickle.load(fr)
        assert len(selected_buildings_dict) == len(
            all_vertices_dict["building"]), f"{len(selected_buildings_dict)} != {len(all_vertices_dict['building'])}"

    selected_buildings, assets_info = handle_planning(
        selected_buildings_dict,
        assets_folder=assets_folder,
        assets_renders_folder=assets_renders_folder
    )

    building_transforms_list = find_building_transforms(all_vertices_dict["building"], selected_buildings,
                                                        assets_info, random_asset)
    with open(building_transforms_path, 'wb') as fw:
        pickle.dump(building_transforms_list, fw)
    return building_transforms_list


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Path):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def main(args):
    os.makedirs(args.output_dir, exist_ok=True)
    layout_img_path = Path(args.layout_img_path)
    selected_pkl_path = Path(args.selected_pkl_path)
    target_file = Path(args.output_dir) / f"{layout_img_path.stem}.blend"
    
    if target_file.is_file():
        print(f"File {target_file.name} exists!!!, do nothing")
        return
    print(f"Processing {layout_img_path.name}...")

    all_vertices_dir = layout_img_path.parent / Path(f"{layout_img_path.stem}_all_vertices.pkl")
    building_transforms_dir = layout_img_path.parent / Path(f"{layout_img_path.stem}_building_transforms.pkl")
    all_vertices_dict = step_edge(layout_img_path, all_vertices_dir, True)
    building_transforms_list = step_match(
        all_vertices_dict, 
        building_transforms_dir, 
        selected_pkl_path,
        Path(args.assets_folder),
        Path(args.assets_renders_folder),
        True
    )

    with open(target_file.parent / Path(f"{target_file.stem}_building_transforms.json"),
              'w', encoding='utf-8') as fw:
        json.dump(building_transforms_list, fw, ensure_ascii=False, indent=4, cls=MyEncoder)

    save_blender_project(
        target_file=str(target_file),
        pkl_v1=str(all_vertices_dir),
        pkl_v2=str(building_transforms_dir),
        use_roadcurve_py=True,
        blender_path=args.blender_path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create meshes from layout images')
    parser.add_argument('--layout_img_path', type=str, required=True,
                       help='Path to the layout image')
    parser.add_argument('--selected_pkl_path', type=str, required=True,
                       help='Path to the selected buildings pickle file')
    parser.add_argument('--output_dir', type=str, 
                       default="./rendered_scenes",
                       help='Directory for output blend files')
    parser.add_argument('--blender_path', type=str,
                       default="../Blender/blender-4.0.2-linux-x64/blender",
                       help='Path to Blender executable')
    parser.add_argument('--assets_folder', type=str,
                       default="../dataset/CityCraft_Buildings/assets/assets_filtered",
                       help='Directory containing the asset files')
    parser.add_argument('--assets_renders_folder', type=str,
                       default="../dataset/CityCraft_Buildings/assets/assets_renders",
                       help='Directory containing the asset renders')
        
    args = parser.parse_args()
    
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    main(args)


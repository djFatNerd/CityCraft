# generated image might have some noisy pixels, for example, a building which has only a few pixels
# use this program to refine the layout, remove isolated irregular pixels

import os
import numpy as np
import cv2
import scipy.ndimage as ndimage
import pickle
import argparse 
from image_process import *
from tqdm import tqdm
import logging

# debugging
import pdb

# Add this line to disable PIL debug logging
logging.getLogger('PIL').setLevel(logging.INFO)

# global parameters
LAYOUT_ORIGINAL_SIZE = 768
LAYOUT_RESIZED_SIZE = 512
PIXEL_SIZE = 0.5 # 0.5 meters per pixel
NOISE_THRESHOLD = 5    # minimum number of pixels for a noise
MIN_BUILDING_WIDTH = 3 # minimum width of a building (3 meters)
MIN_BUILDING_LENGTH = 5 # minimum length of a building (5 meters)


def main(args):
    # Ensure the output directory exists
    os.makedirs(args.output_layouts_folder, exist_ok=True)

    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(args.output_layouts_folder, 'layout_refinement.log')),
            logging.StreamHandler()
        ]
    )
    
    layout_paths = os.listdir(args.input_layouts_folder)
    palette = get_palette()
    
    logging.info(f"Starting layout refinement for {len(layout_paths)} images")
    for layout_path in tqdm(layout_paths, desc="Processing layouts"):
        logging.info(f"Processing {layout_path}")
        image = Image.open(os.path.join(args.input_layouts_folder, layout_path)).convert("RGB").resize((LAYOUT_RESIZED_SIZE, LAYOUT_RESIZED_SIZE), Image.Resampling.NEAREST)
        image_rgb = np.array(image)               
        original_image = image_rgb.copy() # save a copy of the original image
        onehot = rgb_to_onehot(image_rgb)
        label = np.argmax(onehot, axis=2)   
        masks = get_masks(label)
        
        # refine
        refined_image = remove_noise(masks, original_image)
        
        # save
        refined_image = Image.fromarray(refined_image)
        refined_image.save(os.path.join(args.output_layouts_folder, layout_path))
         
def remove_noise(masks, original_image):
    # get minimum width and height of a building
    min_building_width = MIN_BUILDING_WIDTH / PIXEL_SIZE * LAYOUT_RESIZED_SIZE / LAYOUT_ORIGINAL_SIZE # in pixels
    min_building_length = MIN_BUILDING_LENGTH / PIXEL_SIZE * LAYOUT_RESIZED_SIZE / LAYOUT_ORIGINAL_SIZE # in pixels
    
    palette = get_palette()
    for i, mask in enumerate(masks):
        # ground
        if i != 0: # not ground
            labeled_mask, num_features = ndimage.label(mask, structure=np.ones((3, 3)))
            instances = get_object_locations(labeled_mask, num_features)
            if i !=2: # not buildings, general test on number of pixels
                for instance in instances:
                    if len(instance) < NOISE_THRESHOLD:
                        logging.debug(f"Irregular instance detected: {len(instance)} pixels")
                        for idx in instance:
                            original_image[idx] = palette[0] # replace noisy pixel with ground color
                                              
            else: # buildings, impose strircter test on dimensions
                for instance in instances: # [(x,y), ...]
                    instance = np.array(instance)
                    mins, maxs = instance.T.min(axis=1), instance.T.max(axis=1)
                    min_x, min_y = mins
                    max_x, max_y = maxs
                    x_diff = max_x - min_x
                    y_diff = max_y - min_y
                    width = min(x_diff, y_diff)
                    length = max(x_diff, y_diff)
                    if width < min_building_width or length < min_building_length:
                        logging.debug(f"Small building detected: width={width:.2f}m, length={length:.2f}m")
                        for idx in instance:
                            original_image[idx[0], idx[1]] = palette[0] # replace noisy pixel with ground color
    return original_image
                    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_layouts_folder", type=str, default="./layouts_raw")
    parser.add_argument("--output_layouts_folder", type=str, default="./layouts_refined")
    args = parser.parse_args() 
    main(args)
    
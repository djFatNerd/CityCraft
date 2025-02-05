# post process the generated image
import os
from PIL import Image
import numpy as np
import scipy.ndimage as ndimage
import logging
from tqdm import tqdm


# in pixels
NOISE_THRESHOLD = 50

# minimum number of buildings for a valid layout
MIN_BUILDING_COUNT = 20


# irregular building
MIN_BUILDING_WIDTH = 6
MIN_BUILDING_LENGTH = 10
MAX_BUILDING_WIDTH = 100
MAX_BUILDING_LENGTH = 100

# irregular rail
MAX_RAIL_AREA = 100


# irregular vegetation
def post_process(input_dir, output_dir):
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('post_process.log'),
            logging.StreamHandler()
        ]
    )
    
    # Get list of PNG files
    png_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]
    logging.info(f"Found {len(png_files)} PNG files to process")
    
    # Process files with progress bar
    qualified_count = 0
    for file_name in tqdm(png_files, desc="Post-processing images"):
        image = Image.open(os.path.join(input_dir, file_name))
        qualified, image = process(image)
        if qualified:
            image.save(os.path.join(output_dir, file_name))
            qualified_count += 1
        else:
            logging.warning(f"Image {file_name} did not meet quality requirements")
    
    logging.info(f"Processing complete. {qualified_count}/{len(png_files)} images qualified")


def process(image):
    image_array = np.array(image)
    
    # match color
    image_array = match_color(image_array)
    
    # remove noise
    onehot = rgb_to_onehot(image_array)
    label = np.argmax(onehot, axis=2) 
    masks = get_masks(label)
    qualified, image_array = remove_noise(masks, image_array)
    processed_image = Image.fromarray(image_array.astype('uint8'))
    return qualified, processed_image



def get_palette():
    palette = [
        [85, 107, 47],  # ground -> OliveDrab   
        [0, 255, 0],  # vegetation -> Green
        [255, 165, 0],  # building -> orange
        [255, 0, 255],  # rail -> Magenta
        [200, 200, 200],  # traffic Roads ->  grey
        [255, 255, 0],  # Footpath  ->  deeppink
        [0, 191, 255]  # water ->  skyblue
    ]
    return palette


def match_color(image_array):
    palette = np.array(get_palette())
    image_reshaped = image_array.reshape((-1, 3))
    distances = np.linalg.norm(image_reshaped[:, :3, None] - palette.T, axis=1)
    closest_colors = np.argmin(distances, axis=1)
    image_array[:, :, :3] = palette[closest_colors].reshape((768, 768, 3))
    target_color = [255, 165, 0]
    replacement_color = [255, 255, 0]
    target_color2 = [200, 200, 200]
    replacement_color2 = [255, 0, 255]
    mask1 = np.all(image_array[:, :, :3] == target_color, axis=2)
    neighbor_counts_yell = np.all(image_array[:, :, :3] == replacement_color, axis=2)
    neighbor_counts_orga = mask1
    mask2 = np.all(image_array[:, :, :3] == target_color2, axis=2)
    neighbor_counts_rail = np.all(image_array[:, :, :3] == replacement_color2, axis=2)
    neighbor_counts_road = mask2
    
    kernel = np.array([[1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1]])
    
    neighbor_counts_165 = np.zeros_like(mask1, dtype=int)
    neighbor_counts_255 = np.zeros_like(mask1, dtype=int)
    
    neighbor_counts_200 = np.zeros_like(mask2, dtype=int)
    neighbor_counts_2552 = np.zeros_like(mask2, dtype=int)
    
    for y in range(2, image_array.shape[0] - 2):
        for x in range(2, image_array.shape[1] - 2):
            if mask1[y, x]:
                neighborhood_yel = neighbor_counts_yell[y - 2:y + 3, x - 2:x + 3]
                neighborhood_org = neighbor_counts_orga[y - 2:y + 3, x - 2:x + 3]
                neighbor_counts_165[y, x] = np.sum(neighborhood_org * kernel)
                neighbor_counts_255[y, x] = np.sum(neighborhood_yel * kernel)
            if mask2[y, x]:
                neighborhood_rail = neighbor_counts_rail[y - 2:y + 3, x - 2:x + 3]
                neighborhood_road = neighbor_counts_road[y - 2:y + 3, x - 2:x + 3]
                neighbor_counts_200[y, x] = np.sum(neighborhood_road * kernel)
                neighbor_counts_2552[y, x] = np.sum(neighborhood_rail * kernel)

    for y in range(2, image_array.shape[0] - 2):
        for x in range(2, image_array.shape[1] - 2):
            if mask1[y, x] and neighbor_counts_255[y, x] >= 6 and 0 <= neighbor_counts_165[y, x] < 8:
                image_array[y, x, :3] = replacement_color
            elif mask1[y, x] and 0 <= neighbor_counts_165[y, x] <= 5:
                image_array[y, x, :3] = [85, 107, 47]
            if mask2[y, x] and neighbor_counts_2552[y, x] >= 6 and 0 <= neighbor_counts_200[y, x] < 8:
                image_array[y, x, :3] = replacement_color2
            elif mask2[y, x] and 0 <= neighbor_counts_200[y, x] <= 5:
                image_array[y, x, :3] = [85, 107, 47]
        
    return image_array


# remove noise from the image
def remove_noise(masks, original_image):
    # get minimum width and height of a building
    min_building_width = MIN_BUILDING_WIDTH
    min_building_length = MIN_BUILDING_LENGTH
    
    qualified = True
    
    palette = get_palette()
    for i, mask in enumerate(masks):
        # ground
        if i != 0: # not ground
            labeled_mask, num_features = ndimage.label(mask, structure=np.ones((3, 3)))
            instances = get_object_locations(labeled_mask, num_features)
            if i !=2: # not buildings, general test on number of pixels
                for instance in instances:
                    if len(instance) < NOISE_THRESHOLD:
                        for idx in instance:
                            original_image[idx] = palette[0] # replace noisy pixel with ground color
                                              
            else: # buildings, impose strircter test on dimensions
                if len(instances) < MIN_BUILDING_COUNT:
                    qualified = False
                    break
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
                        for idx in instance:
                            original_image[idx[0], idx[1]] = palette[0] # replace noisy pixel with ground color
    
    return qualified, original_image



def get_object_locations(labeled_mask, num_features):
    objects = []
    for i in range(1, num_features + 1):
        indices = np.where(np.array(labeled_mask) == i)
        # print(indices)
        objects.append(list(zip(indices[0], indices[1])))

    return objects


def verify_image(image_array):
    # check if the image is qualified
    # if containing more than 10 buildings
    # if no irregular connected buildings      
    
    return 


def get_masks(label):
    palette = get_palette() 
    masks = []
    for i in range(len(palette)):
        masks.append(label==i)
    
    return masks


def rgb_to_onehot(rgb):
    semantic_map = []
    palette = get_palette()
    
    for colour in palette:
        equality = np.equal(rgb, colour)
        class_map = np.all(equality, axis=-1)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=-1).astype(np.float32)
    return semantic_map


input_dir = "../samples_raw/"
output_dir = "../samples/"
os.makedirs(output_dir, exist_ok=True)
post_process(input_dir, output_dir)

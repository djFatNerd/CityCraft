import numpy as np
import itertools
import statistics
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.neighbors import KDTree
from math import sqrt


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

def print_class_info(label):
    class_names = [
        'ground',
        'vegetation',
        'building',
        'rail',
        ' traffic Roads',
        'footpath',
        'water'
    ]
    
    for i in range(len(class_names)):
        print('class: ', class_names[i], ', total points: ', (label==i).sum())

"""
    converts a RGB semantic field mask (H, W, 3) to (H, W, C) where the last dim is a one
    hot encoding vector of C classes
"""
def rgb_to_onehot(rgb):
    semantic_map = []
    palette = get_palette()
    
    for colour in palette:
        equality = np.equal(rgb, colour)
        class_map = np.all(equality, axis=-1)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=-1).astype(np.float32)
    return semantic_map

'''
    converts a H x W input label to a H x W x 3 RGB array
'''

def label_to_image(label):
    palette = get_palette()
    new_image = np.zeros((label.shape[0], label.shape[1], 3), dtype=np.uint8)
    for i in range(len(palette)):
        new_image[label==i] = palette[i]
    
    return new_image 

# adjust color to make it more esay for VLM understanding
def label_to_image_color_adjusted(label):
    palette = [
        [0,0,0],  # ground -> black
        [0, 255, 0],  # vegetation -> green
        [0, 255, 255],  # building -> cyan
        [255, 0, 255],  # rail -> magenta
        [255,255,255],  # traffic Roads ->  white
        [255, 255, 0],  # Footpath  ->  yellow
        [0, 0, 255]  # water ->  blue
    ]
    
    new_image = np.zeros((label.shape[0], label.shape[1], 3), dtype=np.uint8)
    for i in range(len(palette)):
        new_image[label==i] = palette[i]
    
    return new_image 


def get_masks(label):
    palette = get_palette() 
    masks = []
    for i in range(len(palette)):
        masks.append(label==i)
    
    return masks

# get locations of points where mask == 1 and on the edge
# apply this function to the building mask we can get edges of the buildings
def get_edge_points(mask, target=1, reverse_bool=False):
    mask = np.array(mask)
    target = np.array(target)
    if len(mask.shape) == 3:
        h, w, dim = mask.shape
        assert dim == len(target)
    elif len(mask.shape) == 2:
        h, w = mask.shape
    else:
        raise ValueError(f"mask shape {mask.shape} not supported")

    def at_boundary(i, j):
        return i == 0 or i == h - 1 or j == 0 or j == w - 1

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

    edge_points = []
    for i, j in itertools.product(range(h), range(w)):
        if reverse_bool:
            if not np.array_equal(mask[i, j], target) and (at_boundary(i, j) or at_intersection(i, j)):
                edge_points.append((i, j))
        else:
            if np.array_equal(mask[i, j], target) and (at_boundary(i, j) or at_intersection(i, j)):
                edge_points.append((i, j))
    return edge_points


def get_object_locations(labeled_mask, num_features):
    objects = []
    for i in range(1, num_features + 1):
        indices = np.where(np.array(labeled_mask) == i)
        # print(indices)
        objects.append(list(zip(indices[0], indices[1])))

    return objects


# test if all buildings are isolated correctly, return a binary mask
def test_masks(buildings, img_size=512):
    img = np.zeros((img_size, img_size))
    indices = [index for sublist in buildings for index in sublist]
    for idx in indices:
        x, y = idx
        img[x,y] = 1
        
    # plt.imsave('isolated_buildings.png', img, cmap='gray') 
    return img
    
# test if all builidng edges have been isolated correctly, return a binary mask
def test_edge_points(buildings_edges, img_size=512):
    img = np.zeros((img_size, img_size))
    for idx in buildings_edges:
        x, y = idx
        img[x,y] = 1
        
    plt.imsave('buildings_edges.png', img, cmap='gray') 
    return img
    
# input a list of buildings, each building has a list of points
# output a list of bounding boxes (x,y,w,h), each bouding boxes represents the rough locations of the corresponding input building.
def get_buildings_boxes(buildings):
    building_boxes = []
    qualified_buildings = []  # qualified buildings, buildings that has smallest edge > 5 meters
    for building in buildings:
        x_min = min(building, key=lambda x: x[0])[0]
        x_max = max(building, key=lambda x: x[0])[0]
        y_min = min(building, key=lambda x: x[1])[1]
        y_max = max(building, key=lambda x: x[1])[1]
        
        # Calculate height and width
        h = x_max - x_min
        w = y_max - y_min
        
        building_box = (x_min, y_min, h, w)
        building_boxes.append(building_box)
        qualified_buildings.append(building)  # Keep the building if it meets the condition
    
    return qualified_buildings, building_boxes


'''
    test functions
'''
def draw_buildings_boxes(image, buildings_boxes):
    box_color = 'red'
    label_color = 'blue'
    font = ImageFont.load_default(size=12)
    draw = ImageDraw.Draw(image)
    for idx, building_box in enumerate(buildings_boxes):
        x, y, w, h = building_box
        draw.rectangle(((y, x), (y+h, x+w)), outline=box_color)
        draw.text((y+h/2, x+w/2), str(idx), fill=label_color, font=font)
    
    return image


def mark_buildings(image, buildings_boxes, buildings, building_ids, target):
    label_color = 'red'
    draw = ImageDraw.Draw(image)
    
    # If target is specified, fill that building's pixels with red
    if target is not None:
        pixels = image.load()  # Get pixel access object
        for x, y in buildings[target]:
            pixels[y, x] = (160, 32, 240)  # Set to red (R,G,B)
    
    # Use Ubuntu Bold font which we know exists on the system
    UBUNTU_BOLD = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
    
    for idx, (building_box, building_points) in enumerate(zip(buildings_boxes, buildings)):
        
        # only mark the buildings that are in the building_ids list
        if idx not in building_ids:
            continue
        
        x, y, w, h = building_box
        # Determine font size based on region size
        font_size = min(w, h) // 2  # Scale font to 1/2 of smallest dimension
        font_size = max(12, min(font_size, 20))  # Constrain between 12 and 20
        
        try:
            font = ImageFont.truetype(UBUNTU_BOLD, size=font_size)
        except OSError:
            print("Warning: Falling back to default font")
            font = ImageFont.load_default()
        
        # Get text dimensions
        text = str(idx)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Rest of positioning logic...
        x_coords = [p[0] for p in building_points]
        y_coords = [p[1] for p in building_points]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        margin_x = (x_max - x_min) * 0.4
        margin_y = (y_max - y_min) * 0.4
        
        interior_points = [p for p in building_points 
                         if x_min + margin_x <= p[0] <= x_max - margin_x 
                         and y_min + margin_y <= p[1] <= y_max - margin_y]
        
        if interior_points:
            text_y = statistics.median(p[0] for p in interior_points)
            text_x = statistics.median(p[1] for p in interior_points)
        else:
            text_y = x + w/2
            text_x = y + h/2
        
        text_x -= text_width/2
        text_y -= text_height/2
        
        # Draw text with outline for better visibility
        outline_color = 'white'
        offset = 1
        
        # Draw outline
        for off_x, off_y in [(-offset,-offset), (-offset,offset), (offset,-offset), (offset,offset)]:
            draw.text((text_x + off_x, text_y + off_y), text, fill=outline_color, font=font)
        
        # Draw main text
        draw.text((text_x, text_y), text, fill=label_color, font=font)
    
    return image

def mark_all_buildings(image, buildings_boxes, buildings):
    label_color = 'red'
    draw = ImageDraw.Draw(image)
    
    # Use Ubuntu Bold font which we know exists on the system
    UBUNTU_BOLD = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
    
    for idx, (building_box, building_points) in enumerate(zip(buildings_boxes, buildings)):
        x, y, w, h = building_box
        # Determine font size based on region size
        font_size = min(w, h) // 2  # Scale font to 1/2 of smallest dimension
        font_size = max(12, min(font_size, 20))  # Constrain between 12 and 20
        
        try:
            font = ImageFont.truetype(UBUNTU_BOLD, size=font_size)
        except OSError:
            print("Warning: Falling back to default font")
            font = ImageFont.load_default()
        
        # Get text dimensions
        text = str(idx)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate text position using interior points
        x_coords = [p[0] for p in building_points]
        y_coords = [p[1] for p in building_points]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        margin_x = (x_max - x_min) * 0.4
        margin_y = (y_max - y_min) * 0.4
        
        interior_points = [p for p in building_points 
                         if x_min + margin_x <= p[0] <= x_max - margin_x 
                         and y_min + margin_y <= p[1] <= y_max - margin_y]
        
        if interior_points:
            text_y = statistics.median(p[0] for p in interior_points)
            text_x = statistics.median(p[1] for p in interior_points)
        else:
            text_y = x + w/2
            text_x = y + h/2
        
        text_x -= text_width/2
        text_y -= text_height/2
        
        # Draw text with outline for better visibility
        outline_color = 'white'
        offset = 1
        
        # Draw outline
        for off_x, off_y in [(-offset,-offset), (-offset,offset), (offset,-offset), (offset,offset)]:
            draw.text((text_x + off_x, text_y + off_y), text, fill=outline_color, font=font)
        
        # Draw main text
        draw.text((text_x, text_y), text, fill=label_color, font=font)
    
    return image


# Function to calculate the Euclidean distance between two points
def distance(point1, point2):
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# Function to find the center of a bounding box
def center_of_box(box):
    x, y, w, h = box
    return (x + w / 2, y + h / 2)

# use buildingh edge points and road edge points
# find distance from buildings to roads
# add to input dictionary
def find_building_to_road_distances(buildings_data, building_edge_points, road_edge_points):
    # building a tree with road edge points
    tree = KDTree(road_edge_points)
    
    for i in range(len(building_edge_points)):
        building_edge = building_edge_points[i]
        dist, _ = tree.query(building_edge)
        min_dist = min(dist)
        buildings_data[i]['distance_to_roads'] = min_dist
        
    return buildings_data
    

# input: a list of buildings as bounding boxes, number of neighbors we want
# output: a dictionary of:  key : building ID, val:  closest neightbors
def build_buildings_data(buildings_boxes, num_of_neighbors=5):
    buildings_data = {}
    for i, box in enumerate(buildings_boxes):
        # Calculate the center for the current bounding box
        center = center_of_box(box)
        # caculate estimated width and length, x is the longer edge
        l1, l2 = box[2], box[3]
        x = max(l1,l2) * 0.5
        y = min(l1,l2) * 0.5
        # Calculate the distance to every other building
        distances = []
        for j, other_box in enumerate(buildings_boxes):
            if i != j:
                other_center = center_of_box(other_box)
                dist = distance(center, other_center)
                distances.append((j, dist))
        
        # Sort the list of distances and select the five closest neighbors
        distances.sort(key=lambda x: x[1])
        closest_neighbors = [idx for idx, dist in distances[:num_of_neighbors]]
        
        # Update the dictionary with the current building and its five closest neighbors
        buildings_data[i] = {
            'location': box,
            'x': x, # longer edge (length)
            'y': y, # smaller edge (width)
            'neighbors': closest_neighbors, 
            'description': None, 
            'function_primary': None, 
            'function_secondary': None,
            'scale': None, 
            'style': None, 
            'num_floor':0, 
            'reason': None
        }
    
    return buildings_data
    

# for each building
# 1: only keep edge points
# 2: keep points in order for later mesh creation
def intersection_of_tuples(list1, list2):
    # Convert lists to sets and find intersection
    intersection_set = set(list1).intersection(set(list2))
    # Convert back to a list
    return list(intersection_set)

def create_edges_vertices(buildings, edge_points):
    buildings_edges = []
    for building in tqdm(buildings):
        # print(building)
        building_edge_points = intersection_of_tuples(building, edge_points)
        buildings_edges.append(building_edge_points)
    return buildings_edges

# input: img_path
# output: a dictionary which contains all data needed for LLM planning
def get_buildings_data(img_path):
    # image = Image.open(img_path).convert("RGB").resize((512, 512), Image.Resampling.NEAREST)
    image = Image.open(img_path).convert("RGB")
    image_rgb = np.array(image)
    
    onehot = rgb_to_onehot(image_rgb)
    label = np.argmax(onehot, axis=2)
    # original_image = label_to_image(label)
    
    color_adjusted_image = label_to_image_color_adjusted(label)
    color_adjusted_image = Image.fromarray(color_adjusted_image)

    masks = get_masks(label)
    building_mask = masks[2]
    labeled_mask, num_features = ndimage.label(building_mask)
    buildings = get_object_locations(labeled_mask, num_features)
    
    # get all building locations(bounding boxes), and remove all irregular buildings
    buildings, buildings_boxes = get_buildings_boxes(buildings)
    # test_buildings_boxes(image, buildings_boxes) # test if the boxes matches locations
    
    building_img_binary = test_masks(buildings)
    # all edges points of buildings
    building_edge_points = get_edge_points(building_img_binary)
    # building_edge_binary = test_edge_points(building_edge_points)
    
    # still buildings, but only keep edge points for each
    building_edges = create_edges_vertices(buildings, building_edge_points)
    # building initial buildings data, including positions as bounding boxes, neightbors, and empty descriptions
    buildings_data = build_buildings_data(buildings_boxes, num_of_neighbors=5)

    # get road edge points
    road_mask = masks[4]
    road_edge_points = get_edge_points(road_mask)
    
    # update the building information, add each building's closet distance to traffic roads
    buildings_data = find_building_to_road_distances(buildings_data, building_edges, road_edge_points)
    
    # marked_image = mark_buildings(color_adjusted_image, buildings_boxes, buildings)

    return buildings_data, buildings,buildings_boxes, color_adjusted_image    
    
    
def convert_int64_to_float32(obj):
    """
    Recursively convert all np.int64 values in the given object (dictionary, list, or nested structure) to np.float32.
    """
    if isinstance(obj, dict):
        return {key: convert_int64_to_float32(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_int64_to_float32(element) for element in obj]
    elif isinstance(obj, np.int64):
        return np.float32(obj)
    else:
        return obj

def convert_keys_to_int(d):
    new_d = {}
    for key, value in d.items():
        try:
            new_key = int(key)
        except ValueError:
            new_key = key  # Keep as is if not an integer string
        if isinstance(value, dict):
            value = convert_keys_to_int(value)
        new_d[new_key] = value
    return new_d
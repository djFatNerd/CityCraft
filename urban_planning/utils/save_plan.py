import json
import os
import numpy as np

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

def save_plan(buildings_data, img_data_path, iteration):
    # Convert numpy data types to native Python types
    buildings_data_clean = convert_numpy_types(buildings_data)
    
    # Save the plan as a JSON file
    with open(os.path.join(img_data_path, f'plan_iteration_{iteration}.json'), 'w') as f:
        json.dump(buildings_data_clean, f, indent=4)


def convert_numpy_types(obj):
    """
    Recursively convert NumPy data types in the given object to native Python types.
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(element) for element in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(element) for element in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def convert_numpy_to_native(buildings_data):
    # Convert any numpy data types to native Python types for JSON serialization
    for building in buildings_data.values():
        for key, value in building.items():
            if isinstance(value, (np.integer, np.int64)):
                building[key] = int(value)
            elif isinstance(value, (np.floating, np.float32, np.float64)):
                building[key] = float(value)
            elif isinstance(value, np.ndarray):
                building[key] = value.tolist()
            elif isinstance(value, dict):
                building[key] = convert_numpy_to_native(value)
    return buildings_data

def create_summary_report(img_data_path, args):
    report_lines = []
    report_lines.append(f"Layout Image: input_layout.png")
    report_lines.append(f"User Requirements: {args.user_input if args.user_input else 'None'}")
    report_lines.append(f"Total Iterations: {args.itr}")

    # You can add more details as needed
    with open(os.path.join(img_data_path, 'summary_report.txt'), 'w') as f:
        f.write('\n'.join(report_lines))


def generate_basic_info_prompt(basic_info):
    # Get the total number of buildings
    total_buildings = len(basic_info)
    
    # Start building the prompt
    prompt = f"There are a total of {total_buildings} buildings to be planned within a 768 x 768 grid. "
    prompt += "Each building is represented in a dictionary where:\n\n"
    prompt += "- The **key** is the building ID (as a string).\n"
    prompt += "- The **value** is a list of coordinates `[x, y, h, w]` defining a bounding box that encloses the building's region.\n\n"
    prompt += "**Parameters Explanation:**\n"
    prompt += "- **x**: The x-coordinate of the top-left corner of the bounding box.\n"
    prompt += "- **y**: The y-coordinate of the top-left corner of the bounding box.\n"
    prompt += "- **h**: The height of the bounding box.\n"
    prompt += "- **w**: The width of the bounding box.\n\n"
    prompt += "**Building Locations Dictionary:**\n\n"
    
    # Add the dictionary representation in a formatted string
    prompt += "{\n"
    for building_id, coords in basic_info.items():
        prompt += f"    '{building_id}': {coords},\n"
    prompt = prompt.rstrip(",\n") + "\n}"  # Remove trailing comma and newline, then close the dictionary
    
    return prompt
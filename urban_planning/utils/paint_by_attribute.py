# given a plan and a layout, paint buildings on the layout by the function

import cv2
import numpy as np
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from image_process import *

import argparse
import colorsys
from matplotlib.patches import Patch


def get_distinct_colors(n):
    """Generate n distinct colors with high contrast using HSV color space."""
    colors = []
    for i in range(n):
        # Distribute hues evenly around the color wheel
        hue = i / n
        # Use high saturation and value for vibrant, distinct colors
        saturation = 0.8
        value = 0.9
        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        # Convert to 8-bit RGB values
        color = tuple(int(c * 255) for c in rgb)
        colors.append(color)
    return colors

def paint_buildings_by_attribute(layout_path, plan_path, attribute_key="function_primary", output_suffix=None):
    """
    Paint buildings on a layout and show distribution based on a specified attribute.
    
    Args:
        layout_path (str): Path to the layout image
        plan_path (str): Path to the plan JSON file
        attribute_key (str): Key in the plan dictionary to use for coloring (e.g., "function_primary", "scale")
        output_suffix (str, optional): Custom suffix for output filename. If None, uses attribute_key
    
    Returns:
        str: Path to the saved output image
    """
    # Read plan and get unique values for the specified attribute
    with open(plan_path, 'r') as f:
        plan = json.load(f)
        unique_values = list(set([plan[key][attribute_key] for key in plan.keys()]))
        colors = get_distinct_colors(len(unique_values))
        color_map = {val: colors[i] for i, val in enumerate(unique_values)}
    
    # Calculate distribution correctly by counting buildings
    value_counts = {val: 0 for val in unique_values}  # Initialize all possible values to 0
    total_buildings = len(plan.keys())
    for building_id in plan.keys():
        val = plan[building_id][attribute_key]
        value_counts[val] += 1
    
    # Sort value_counts by keys for consistent ordering
    value_counts = dict(sorted(value_counts.items()))
    
    # Process and paint buildings (existing code)
    image = Image.open(layout_path).convert("RGB")
    image_rgb = np.array(image)               
    original_image = image_rgb.copy()
    onehot = rgb_to_onehot(image_rgb)
    label = np.argmax(onehot, axis=2)   
    masks = get_masks(label)
    building_mask = masks[2]
    labeled_mask, num_features = ndimage.label(building_mask, structure=np.ones((3, 3)))
    instances = get_object_locations(labeled_mask, num_features)
    
    painted_image = np.zeros_like(original_image)
    for building_id, instance in enumerate(instances):
        for idx in instance:
            painted_image[idx[0], idx[1]] = color_map[plan[str(building_id)][attribute_key]]

    
    
    # Create figure with smaller size
    fig = plt.figure(figsize=(16, 8))  # Reduced from (24, 12)
    gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.3)  # Added wspace for more space between subplots
    
    # Painted image subplot
    ax_painted = fig.add_subplot(gs[0])
    ax_painted.imshow(painted_image)
    ax_painted.set_title(f'Buildings Painted by {attribute_key.replace("_", " ").title()}', fontsize=16, pad=20)  # Added padding
    ax_painted.axis('off')
    
    # Create nested gridspec for the right side with more space
    right_gs = gs[1].subgridspec(2, 1, height_ratios=[1, 1.5], hspace=0.4)  # Added hspace
    
    # Legend subplot
    ax_legend = fig.add_subplot(right_gs[0])
    legend_elements = [Patch(facecolor=[c/255 for c in color_map[val]], 
                           label=f'{val} ({count}/{total_buildings})') 
                      for val, count in value_counts.items()]
    ax_legend.legend(handles=legend_elements, 
                    loc='center',
                    title=f'{attribute_key.replace("_", " ").title()} Legend',
                    title_fontsize=14,
                    fontsize=12,
                    bbox_to_anchor=(0.5, 0.5),  # Center the legend
                    bbox_transform=ax_legend.transAxes)
    ax_legend.axis('off')
    
    # Pie chart subplot with improved handling of small slices
    ax_pie = fig.add_subplot(right_gs[1])
    pie_colors = [[c/255 for c in color_map[val]] for val in value_counts.keys()]
    
    # Calculate percentages
    total = sum(value_counts.values())
    percentages = [count/total * 100 for count in value_counts.values()]
    
    # Custom autopct function to hide small slice percentages
    def make_autopct(values):
        def autopct(pct):
            if pct < 7:  # Only show percentage label if slice is >= 7%
                return ''
            return f'{pct:.1f}%'
        return autopct
    
    wedges, texts, autotexts = ax_pie.pie(percentages, 
                                         colors=pie_colors,
                                         autopct=make_autopct(percentages),
                                         textprops={'fontsize': 12},
                                         pctdistance=1.3,
                                         radius=0.8)
    
    # Remove the direct labels from pie chart
    plt.setp(texts, visible=False)      # Hide the original labels
    plt.setp(autotexts, size=12)
    
    # Add a legend instead of direct labels
    ax_pie.legend(wedges, value_counts.keys(),
                 title="Categories",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1),    # Position legend to the right
                 fontsize=12,
                 title_fontsize=14)
    
    ax_pie.set_title('Distribution', fontsize=14, pad=20)
    
    # Adjust layout
    plt.tight_layout()
    
    # Generate and save output
    if output_suffix is None:
        output_suffix = attribute_key
    output_path = os.path.join(os.path.dirname(layout_path), f"buildings_by_{output_suffix}.png")
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return output_path

def add_legend(layout_path, output_suffix="with_legend"):
    """
    Add a large, centered palette legend to the original layout image.
    """
    # Read original image
    image = Image.open(layout_path).convert("RGB")
    image_rgb = np.array(image)
    
    # Get palette colors
    palette = get_palette()
    palette_names = ["ground", "vegetation", "building", "rail", "traffic Roads", "footpath", "water"]
    
    # Create figure with smaller size
    fig = plt.figure(figsize=(16, 8))  # Reduced from (24, 12)
    gs = fig.add_gridspec(1, 2, width_ratios=[2, 1], wspace=0.3)  # Added wspace
    
    # Original image subplot
    ax_original = fig.add_subplot(gs[0])
    ax_original.imshow(image_rgb)
    ax_original.set_title('Original Layout', fontsize=16, pad=20)  # Added padding
    ax_original.axis('off')
    
    # Legend subplot with adjusted spacing
    ax_legend = fig.add_subplot(gs[1])
    ax_legend.axis('off')
    
    legend_elements = [Patch(facecolor=[c/255 for c in color], 
                           label=name,
                           linewidth=2) 
                      for color, name in zip(palette, palette_names)]
    
    ax_legend.legend(handles=legend_elements, 
                    loc='center',
                    title='Layout Elements',
                    title_fontsize=16,
                    fontsize=14,
                    frameon=True,
                    edgecolor='black',
                    bbox_to_anchor=(0.5, 0.5),
                    bbox_transform=ax_legend.transAxes,
                    labelspacing=1.2)
    
    # Adjust layout
    plt.tight_layout()
    
    # Generate and save output
    output_path = os.path.join(os.path.dirname(layout_path), f"original_layout_{output_suffix}.png")
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return output_path


def mark_with_building_id(layout_path):
    image = Image.open(layout_path).convert("RGB")
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

    marked_layout = mark_all_buildings(image, buildings_boxes, buildings)
    marked_layout.save(os.path.join(os.path.dirname(layout_path), f"marked_layout.png"))



def main(args):
    # Give original layout a legend
    add_legend(args.input_layout_path)
    
    # paint buildings by attributes
    paint_buildings_by_attribute(args.input_layout_path, args.input_plan_path, "function_primary")
    paint_buildings_by_attribute(args.input_layout_path, args.input_plan_path, "function_secondary")
    paint_buildings_by_attribute(args.input_layout_path, args.input_plan_path, "scale")
    paint_buildings_by_attribute(args.input_layout_path, args.input_plan_path, "style")

    # mark buildings with their ids
    mark_with_building_id(args.input_layout_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_layout_path", type=str, 
                       default="/data/jd_data/CityGen-LLM-Planning/planning/user_input_test_12_08/input_layout.png")
    parser.add_argument("--input_plan_path", type=str, 
                       default="/data/jd_data/CityGen-LLM-Planning/planning/user_input_test_12_08/plan_iteration_0.json")
    args = parser.parse_args() 
    main(args)

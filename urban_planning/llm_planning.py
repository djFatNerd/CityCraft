import numpy as np
import random
import os
import time
import glob
import json
import shutil

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.optimize import minimize, NonlinearConstraint, differential_evolution, basinhopping
from scipy.spatial.transform import Rotation as R
from shapely.geometry import Polygon
import pickle

from typing import Tuple
import itertools
from math import sqrt
from tqdm import tqdm
from io import BytesIO
import base64
from scipy.spatial import KDTree
# from langchain.llms import OpenAI
from langchain_core.prompts import PromptTemplate
import prompts
import pickle
from openai import OpenAI
from argparse import ArgumentParser
from json_tricks import load, dump
from tqdm import tqdm
from utils.image_process import *
from utils.save_plan import *

from abc import ABC, abstractmethod
from PIL import Image
import google.generativeai as genai

from llm_providers import OpenAIProvider, GeminiProvider


# City planner
class CityPlanner():
    def __init__(self, api_key, user_input, buildings_data, provider_name="openai", **kwargs):
        # Initialize the appropriate LLM provider
        if provider_name.lower() == "openai":
            self.llm_provider = OpenAIProvider(api_key, **kwargs)
        elif provider_name.lower() == "gemini":
            self.llm_provider = GeminiProvider(api_key, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
        # get basic info
        self.basic_info = self.get_basic_info(buildings_data)
        self.basic_info_prompt = generate_basic_info_prompt(self.basic_info)
        
        self.parsed_user_requirement = None
        self.required_buildings_status = None
        
        # parse user requirement (if any)
        if user_input:
            self.user_requirement_template = PromptTemplate(input_variables=["user_input"],
                                              template=prompts.parse_user_requirement_prompt)
            
            self.user_requirement = self.user_requirement_template.format(user_input=user_input+self.basic_info_prompt)
            self.parsed_user_requirement = self.parse_user_requirements(self.user_requirement)
            
        # prompt template for planning
        self.building_plan_template = PromptTemplate(input_variables=["input_location", 
                                                                      "length",
                                                                      "width",
                                                                      "distance_to_roads", 
                                                                      "neighbor _information", 
                                                                      "additional_requirements",
                                                                      "requirements_string"], 
                                                     template=prompts.building_plan_prompt)
        
        # prompt template for refining
        self.building_refine_template = PromptTemplate(input_variables=["input_location", 
                                                                        "length",
                                                                        "width", 
                                                                        "distance_to_roads", 
                                                                        "neighbor_information", 
                                                                        "self_information",
                                                                        "reason", 
                                                                        "additional_requirements",
                                                                        "requirements_string"], 
                                                       template=prompts.building_refine_prompt)

        # global state
        if self.parsed_user_requirement:
            self.required_buildings_status = {}
            
            self.overall_planning_status = {
                'total_buildings_to_plan': 0,
                'buildings_planned_so_far': 0
            }
                 
            self.additional_requirements = self.parsed_user_requirement.get('additional_requirements', [])
            
            # Initialize counts for required buildings              
            for item in self.parsed_user_requirement.get('quantified_requirements', []):
                building_type = item['item'].lower().strip()
                count = item['count']
                self.required_buildings_status[building_type] = {
                    'target': count,
                    'current_planned': 0
                }
        
    
    def get_basic_info(self, buildings_data):
        # get basic info, for intial user requirement parsing
        basic_info = {building_id: info['location'] for building_id, info in buildings_data.items()}
        return basic_info
        
    
    def LLM_planning(self, targets, buildings, buildings_boxes, buildings_data, color_adjusted_image):
        building_times = {}
        if self.parsed_user_requirement:
            self.overall_planning_status['total_buildings_to_plan'] = len(targets)
            self.overall_planning_status['buildings_planned_so_far'] = 0    
        
        while len(targets) != 0:
            target_idx = random.randrange(len(targets))
            target = targets.pop(target_idx)
            print("processing target building: " + str(target))
            
            start_time = time.time()
            
            building_info = buildings_data[target]
            building_location = building_info['location']
            building_neighbors = building_info['neighbors']
            marked_image = mark_buildings(color_adjusted_image, buildings_boxes, buildings, building_neighbors, target)
            # marked_image.save(os.path.join(args.output_dir, 'marked_image.png'))
            
            descriptions= building_info['description']
            length=building_info['x']
            width=building_info['y']            
            building_distance_to_roads = building_info['distance_to_roads']
            neighbor_information = self.summarize_neighbor_info(buildings_data, building_neighbors)
            
            if self.parsed_user_requirement:
                requirements_string = compose_requirements_string(self.required_buildings_status, self.overall_planning_status)
            else:
                requirements_string = ""
            
            building_plan_prompt = self.building_plan_template.format(
                                        input_location=building_location, 
                                        width=width,
                                        length=length,
                                        distance_to_roads=building_distance_to_roads, 
                                        neighbor_information=neighbor_information, 
                                        additional_requirements=self.additional_requirements if self.parsed_user_requirement else None,
                                        requirements_string=requirements_string,
                                    )
            
            plan = self.get_vision_chat_response(building_plan_prompt, marked_image, model=args.planning_model)
            
            # plan = self.get_chat_response(building_plan_prompt, model=args.planning_model)
            # test if resulting plan satisfy format requirements, if not, remind and regenerate
            while (not plan) or (len(plan.split("|")) != 6):
                error_remind_message = (
                    "Your last response was: " + plan + ", which doesn't match the required format. Please rethink and respond."
                )
                plan = self.get_vision_chat_response(building_plan_prompt + "\n\n" + error_remind_message, marked_image, model=args.planning_model)

            buildings_data = self.update_building_data(buildings_data, plan, target)
            end_time = time.time()
            building_times[target] = end_time - start_time
            
        return buildings_data, building_times
    
        
    # given an initial state where all buildings are planned and assigned, refine the given region according to planning
    # stopping criteria: total changes < threshold * num of buildings
    def LLM_refine(self, targets, buildings_data):
        changes = 0
        num_buildings = len(targets)
        if self.parsed_user_requirement:
            self.overall_planning_status['total_buildings_to_plan'] = num_buildings
            self.overall_planning_status['buildings_planned_so_far'] = 0
        
        # Dictionary to store time taken for each building
        building_times = {} 
        
        # start refinement
        while len(targets) != 0:
            target_idx = random.randrange(len(targets))
            target = targets.pop(target_idx)
            print("processing target building: " + str(target))
            start_time = time.time()  # Start timing for this building
            
            # convert string building id into intergers for easier access
            buildings_data = convert_keys_to_int(buildings_data)
            building_info = buildings_data[target]
            self_information = self.summarize_self_info(building_info) 
            building_location = building_info['location']
            building_length = building_info['x']
            building_width = building_info['y']
            building_neighbors = building_info['neighbors']
            # descriptions= building_info['description']
            building_distance_to_roads = building_info['distance_to_roads']
            # reason = building_info['reason']
            neighbor_information = self.summarize_neighbor_info(buildings_data, building_neighbors)
            
            if self.parsed_user_requirement:
                requirements_string = compose_requirements_string(self.required_buildings_status, self.overall_planning_status,refining=True)
            else:
                requirements_string = ""
            
            building_refine_prompt = self.building_refine_template.format(
                                        input_location=building_location, 
                                        length=building_length,
                                        width=building_width,
                                        distance_to_roads=building_distance_to_roads, 
                                        neighbor_information=neighbor_information, 
                                        self_information=self_information,
                                        additional_requirements=self.additional_requirements if self.parsed_user_requirement else None,
                                        requirements_string=requirements_string,
                                    )

            # get plan, should be "keep" or a new plan, or wrong format            
            plan = self.get_chat_response(building_refine_prompt, model=args.planning_model)                       
            # test if resulting plan satisfy format requirements, if not, remind and regenerate
            while not (plan == 'keep' or (len(plan.split("|")) == 6)):
                error_remind_message = (
                    f"Your last response was: {plan}, which doesn't match the required format. "
                    "You should output 'keep' to keep the old plan or output a new plan in the format: "
                    "description|primary function|secondary function|architectural style|building size|reason. "
                    "Please rethink and respond."
                )        
                plan = self.get_chat_response(building_refine_prompt + "\n\n" + error_remind_message, model=args.planning_model)
            
            # Compare the new plan with the existing information
            if plan != 'keep':
                new_plan_info = plan.split("|")
                existing_info = self_information.split("|")
                
                # Compare all elements except the last one (reason)
                if new_plan_info[:-1] == existing_info[:-1]:
                    print("No significant changes detected. Treating as 'keep'.")
                    plan = 'keep'

            # plan is correct                
            if plan == 'keep':
                print("Keeping the previous design")
            else:
                # (1) if previous type was a required type, delete
                if 'required_type' in building_info.keys():
                    required_type = building_info['required_type'].lower().strip()
                    self.required_buildings_status[required_type]['current_planned'] -= 1
                    # also delete required type in original dictionary
                    del buildings_data[target]['required_type']
                    
                # (2) update new plan
                buildings_data = self.update_building_data(buildings_data, plan, target)
                changes += 1
            
            end_time = time.time()
            building_times[target] = end_time - start_time  # Record time taken
            
        change_ratio = changes / num_buildings
        return change_ratio, buildings_data, building_times

    
    def summarize_neighbor_info(self, buildings_data, neighbors):
        neighbor_descriptions = []
        
        for neighbor_id in neighbors:
            neighbor_info = buildings_data[neighbor_id]
            base_info = f"building {neighbor_id} at: {neighbor_info['location']}"
            
            if neighbor_info['description']:  # building has been assigned / planned
                details = [
                    f"{neighbor_info['description']}",
                    f"primary function: {neighbor_info['function_primary']}",
                    f"secondary function: {neighbor_info['function_secondary']}",
                    f"style: {neighbor_info['style']}",
                    f"scale: {neighbor_info['scale']}"
                ]
                neighbor_descriptions.append(f"{base_info}, {', '.join(details)}.")
            else:
                neighbor_descriptions.append(f"{base_info}.")
        
        return "\n".join(neighbor_descriptions)
    
    # "description|primary function|secondary function|architectural style|building size|reason."
    def summarize_self_info(self, building_info):
        description = building_info['description']
        primary_function = building_info['function_primary']
        secondary_function = building_info['function_secondary']
        style = building_info['style']
        scale = building_info['scale']
        reason = building_info['reason']
        self_info = [description, primary_function, secondary_function, style, scale, reason]
        self_info = "|".join(self_info)
        return self_info
    
    
    def get_chat_response(self, prompt, model):
        return self.llm_provider.get_chat_response(prompt, model)
    
    
    def get_vision_chat_response(self, prompt, image, model):
        return self.llm_provider.get_vision_chat_response(prompt, image, model)
    
    
    def encode_image_base64(self, image):
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    
    def parse_user_requirements(self, user_input, max_retries=3):
        prompt = user_input
        error_message = ""
        for attempt in range(1, max_retries + 1):
            # Construct the prompt with any error message from previous attempts
            if error_message:
                prompt += f"\n\n**Error:** {error_message}\nPlease correct your output and ensure it is valid JSON."

            # parse user requirement with LLM assist, we used the best model
            answer = self.get_chat_response(prompt, model=args.parse_user_requirement_model)
            answer = extract_json_from_response(answer)
            # Try to parse the JSON output
            try:
                parsed_requirements = json.loads(answer)
                return parsed_requirements  # Successfully parsed
            except json.JSONDecodeError as e:
                error_message = f"Failed to parse your output as valid JSON. Error: {str(e)}"
                print(f"Attempt {attempt}: {error_message}")

        # If all attempts fail, return an empty dictionary or handle as appropriate
        print("Maximum retries reached. Unable to parse user requirements.")
        return {}

    
    def update_building_data(self, buildings_data, plan, idx):
        # update plan to buildings_data
        plan_info = plan.split("|")
        buildings_data[idx]['description'] = plan_info[0]
        buildings_data[idx]['function_primary'] = plan_info[1] 
        buildings_data[idx]['function_secondary'] = plan_info[2]
        buildings_data[idx]['style'] = plan_info[3]
        buildings_data[idx]['scale'] = plan_info[4]
        buildings_data[idx]['reason'] = plan_info[5]
        
        if self.parsed_user_requirement:
            required_types = self.required_buildings_status.keys()
            for required_type in required_types:
                if required_type.lower().strip() in plan: # LLM planned a required type
                    buildings_data[idx]['required_type'] = required_type
                    self.required_buildings_status[required_type]['current_planned'] += 1
                    break # found require type
                
            self.overall_planning_status['buildings_planned_so_far'] += 1  # Increment planned buildings
        return buildings_data


def extract_json_from_response(response):
    import re
    # Use regex to find the JSON content within code blocks
    pattern = r'```json\s*(\{.*?\})\s*```'
    match = re.search(pattern, response, re.DOTALL)
    if match:
        json_content = match.group(1)
    else:
        # If no code block is found, assume the entire response is JSON
        json_content = response

    return json_content.strip()


def compose_requirements_string(required_buildings_status, overall_planning_status, refining=None):
    requirements = []
    if required_buildings_status:
        for building_type, counts in required_buildings_status.items():
            remaining = counts['target'] - counts['current_planned']
            if remaining > 0:
                requirements.append(f"Still need {remaining} {building_type}(s)")
    total_remaining = overall_planning_status['total_buildings_to_plan'] - overall_planning_status['buildings_planned_so_far']
    if total_remaining > 0:
        if refining:
            requirements.append(f"{total_remaining} buildings left to be refined")
        else:
            requirements.append(f"{total_remaining} buildings left to be planned")
    return '; '.join(requirements)


# main        
def main():
    # Load image
    img_path = args.image_path
    img_data_path = args.output_dir # already has the image name when running exp
    os.makedirs(img_data_path, exist_ok=True)

    # Save the input layout image into the output folder
    shutil.copy(img_path, os.path.join(img_data_path, 'input_layout.png'))

    # Save user requirements
    if args.user_input:
        with open(os.path.join(img_data_path, 'user_requirements.txt'), 'w') as f:
            f.write(args.user_input)

    # Check for existing plan files to resume from the latest iteration
    plan_files = [f for f in os.listdir(img_data_path) if f.startswith('plan_iteration_') and f.endswith('.json')]
    iteration_numbers = [int(f[len('plan_iteration_'):-5]) for f in plan_files]

    if iteration_numbers:
        # Resume from the latest iteration
        latest_iteration = max(iteration_numbers)
        print(f"Found existing plans up to iteration {latest_iteration}. Resuming from iteration {latest_iteration + 1}")
        
        # Check if the plan is complete, if threshold is met, exit
        if os.path.exists(os.path.join(img_data_path, 'plan_complete.txt')):
            print("Plan is already complete. Exiting.")
            return  # Or sys.exit() if outside a function
        
        # Load the latest buildings_data
        with open(os.path.join(img_data_path, f'plan_iteration_{latest_iteration}.json'), 'r') as f:
            buildings_data = json.load(f)

        start_iteration = latest_iteration + 1
        
        # Load changes if they exist
        changes_file = os.path.join(img_data_path, 'changes.json')
        if os.path.exists(changes_file):
            with open(changes_file, 'r') as f:  
                changes = json.load(f)
        else:
            changes = []

        # Load time cost data if it exists
        time_cost_file = os.path.join(img_data_path, 'planning_time.json')
        if os.path.exists(time_cost_file):
            with open(time_cost_file, 'r') as f:
                planning_time = json.load(f)
        else:
            planning_time = {}
            
        # Initialize city planner
        city_planner = CityPlanner(args.api_key, args.user_input, buildings_data, args.provider)
            
    else:
        # Start from scratch
        # Empty dictionary, only keys and basic information, no data, and a color adjusted image for later vision model input
        buildings_data, buildings, buildings_boxes, color_adjusted_image = get_buildings_data(img_path)
        color_adjusted_image.save(os.path.join(img_data_path, 'color_adjusted_image.png'))
        
        # Initialize city planner
        city_planner = CityPlanner(args.api_key, args.user_input, buildings_data, args.provider)
        start_iteration = 0
        changes = []
        planning_time = {}

        # List of targets
        targets = list(range(len(buildings_data.keys())))

        # Initial round
        print("Starting initial planning...")
        building_times = {}
        start_time = time.time()
        buildings_data, building_times = city_planner.LLM_planning(targets, buildings, buildings_boxes, buildings_data, color_adjusted_image)
        total_time = time.time() - start_time
        planning_time['0'] = {'total_time': total_time, 'building_times': building_times}

        # Save initial plan
        save_plan(buildings_data, img_data_path, iteration=0)
        
        # Save required building's status
        required_buildings_status_file = os.path.join(img_data_path, 'required_buildings_status.json')
        if city_planner.required_buildings_status:  
            with open(required_buildings_status_file, 'w') as f:
                json.dump(city_planner.required_buildings_status, f, indent=4)
        
        # Save time cost data
        with open(os.path.join(img_data_path, 'planning_time.json'), 'w') as f:
            json.dump(planning_time, f, indent=4)
    
            
    # More rounds
    i = start_iteration
    while i < args.itr:
        print(f"Refining iteration: {i+1}")

        targets = list(range(len(buildings_data.keys())))
        building_times = {}
        start_time = time.time()
        # load required building's status if file exists
        required_buildings_status_file = os.path.join(img_data_path, 'required_buildings_status.json')
        
        
        if os.path.exists(required_buildings_status_file):
            with open(required_buildings_status_file, 'r') as f:
                city_planner.required_buildings_status = json.load(f)
        
        change_ratio, buildings_data, building_times = city_planner.LLM_refine(targets, buildings_data)
        total_time = time.time() - start_time

        print(f"For iteration {i}, the change ratio is: {change_ratio}")
        # Record change ratio of each round
        changes.append({'iteration': i, 'change_ratio': change_ratio})
        # Save result
        save_plan(buildings_data, img_data_path, iteration=i)
        # Save required building's status
        required_buildings_status_file = os.path.join(img_data_path, 'required_buildings_status.json')
        if city_planner.required_buildings_status:
            with open(required_buildings_status_file, 'w') as f:
                json.dump(city_planner.required_buildings_status, f, indent=4)  

        # Update time cost data
        planning_time[str(i)] = {'total_time': total_time, 'building_times': building_times}
        with open(os.path.join(img_data_path, 'planning_time.json'), 'w') as f:
            json.dump(planning_time, f, indent=4)
            
        
        # Check if change_ratio is less than change_threshold
        if change_ratio < args.change_threshold:
            print(f"Change ratio is less than {args.change_threshold}. Planning is complete.")
            # Save a flag indicating plan is complete
            with open(os.path.join(img_data_path, 'plan_complete.txt'), 'w') as f:
                f.write('Plan is complete.')
            
            break  # Exit the loop
        
        i += 1
    
    # Save changes
    with open(os.path.join(img_data_path, 'changes.json'), 'w') as f:
        json.dump(changes, f, indent=4)

    # Optionally, create a summary report
    create_summary_report(img_data_path, args)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--api_key", help="API key for the chosen provider", required=True)
    parser.add_argument("--provider", help="LLM provider (openai/gemini)", default="openai", choices=["openai", "gemini"])
    parser.add_argument("--base_url", help="Base URL for API (optional)", default=None)
    parser.add_argument("--parse_user_requirement_model", help="model used for parsing user requirement, we suggest to use the best model cause this step is critical for understanding user requirement", default=None, required=True)
    parser.add_argument("--planning_model", help="model used for planning", default=None, required=True)
    parser.add_argument("--change_threshold", help="change ratio threshold to determine if the plan is complete", type=float, default=0.1)
    parser.add_argument("--output-dir", type=str, default= 'planning')
    parser.add_argument("--image-path", type=str, default='/data/jd_data/CityGen-LLM-Planning/test_layouts/608_processed.png', help="input layout path")
    parser.add_argument("--itr", type=int, default=2)
    parser.add_argument("--user-input", type=str, default=None, help="user input requirements")
    args = parser.parse_args()
    
    # Pass provider-specific kwargs
    provider_kwargs = {}
    if args.base_url:
        provider_kwargs['base_url'] = args.base_url
    
    main()

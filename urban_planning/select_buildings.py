import os
import pickle
import glob
import json
import argparse

import torch
import numpy as np
from PIL import Image


import open_clip
from sentence_transformers import SentenceTransformer
from llm_planning import *
from tqdm import tqdm

class Building_Selector():
    def __init__(self, device):
        self.device = device
        self.clip_model, _, self.clip_preprocess = open_clip.create_model_and_transforms('ViT-L-14', pretrained='laion2b_s32b_b82k', device=device)
        self.clip_tokenizer = open_clip.get_tokenizer('ViT-L-14')
        self.sbert_model = SentenceTransformer('all-mpnet-base-v2', device=device)

        features_dir = os.path.join(args.asset_data_path, 'assets_features')
        self.clip_img_features_1 = self.get_features(features_dir, 'clip_img_features_1.pt').to(self.device)
        self.clip_img_features_2 = self.get_features(features_dir, 'clip_img_features_2.pt').to(self.device)
        self.clip_img_features_3 = self.get_features(features_dir, 'clip_img_features_3.pt').to(self.device)
        
        self.sbert_description_features = self.get_features(features_dir, 'sbert_description_features.pt').to(self.device)
        self.sbert_primary_function_features = self.get_features(features_dir, 'sbert_primary_function_features.pt').to(self.device)
        self.sbert_secondary_function_features = self.get_features(features_dir, 'sbert_secondary_function_features.pt').to(self.device)
        self.sbert_style_features = self.get_features(features_dir, 'sbert_style_features.pt').to(self.device)
        self.sbert_scale_features = self.get_features(features_dir, 'sbert_scale_features.pt').to(self.device)
        
        
        self.dimensions = self.get_dimensions(features_dir, 'estimated_dimensions.json')
        self.candidates_num = self.clip_img_features_1.shape[0]

        with open(os.path.join(features_dir, 'scales.json'), 'r') as f:
            self.scales = json.load(f)

    
    def get_dimensions(self, features_dir, dimensions_path):
        with open(os.path.join(features_dir, dimensions_path), 'r') as f:
            dimensions = json.load(f)
        return dimensions
    
    
    def get_features(self, features_dir, features_path):
        return torch.load(os.path.join(features_dir, features_path))
    

    def select(self, query, k=5, k_feature=20):
        description = query['description']
        primary_function = query['function_primary']
        secondary_function = query['function_secondary']
        style = query['style']
        scale = query['scale']
        
        # get clip text features
        clip_text = self.clip_tokenizer(description + "and the building is: " + primary_function + ", " + secondary_function + ", " + style + ", " + scale + ".").to(self.device)
        with torch.no_grad(), torch.cuda.amp.autocast():
            clip_text_features = self.clip_model.encode_text(clip_text)
        
        description_features = self.get_sbert_features(description, self.sbert_model)
        primary_function_features = self.get_sbert_features(primary_function, self.sbert_model)
        secondary_function_features = self.get_sbert_features(secondary_function, self.sbert_model)
        style_features = self.get_sbert_features(style, self.sbert_model)
    
        clip_feature_candidates = self.find_top_K_clip(clip_text_features, k_feature)    
        description_features_candidates = self.find_top_K_sbert(description_features, self.sbert_description_features, k_feature)
        primary_function_features_candidates = self.find_top_K_sbert(primary_function_features, self.sbert_primary_function_features, k_feature)
        secondary_function_candidates = self.find_top_K_sbert(secondary_function_features, self.sbert_secondary_function_features, k_feature)
        style_features_candidates = self.find_top_K_sbert(style_features, self.sbert_style_features, k_feature)
        
        # customized weights for all features
        w_clip = 1
        w_description = 1
        w_primary_function = 1
        w_secondary_fucntion = 1
        w_style = 1
        
        candidates_scores = np.zeros(self.candidates_num)
        
        candidates_scores[clip_feature_candidates] += w_clip
        candidates_scores[description_features_candidates] += w_description
        candidates_scores[primary_function_features_candidates] += w_primary_function
        candidates_scores[secondary_function_candidates] += w_secondary_fucntion
        candidates_scores[style_features_candidates] += w_style
        
        candidates = np.argsort(candidates_scores)[-k:][::-1].tolist()
        
        indices = [index for index, name in enumerate(self.scales) if name==scale.strip()] 
        candidates_scores[indices] += 100
        candidates = np.argsort(candidates_scores)[-k:][::-1].tolist()
        
        x = query['x']
        y = query['y']
        
        for candidate in candidates:
            candidate_width = self.dimensions[str(candidate)]['estimated_width']
            candidate_length = self.dimensions[str(candidate)]['estimated_length'] 
            
            if candidate_width * candidate_length > x * y * 1.5 or candidate_width * candidate_length < x * y * 0.5:
                candidates.remove(candidate)
        
        if len(candidates) < 1:
            print("not enough candidates, return all candidates")
            import pdb; pdb.set_trace();
        return candidates
        
        
    def get_sbert_features(self, text, model, N=768):
        if text:
            return model.encode(text, convert_to_tensor=True, show_progress_bar=False)
        else:
            return torch.zeros([N], device=self.device)
    
    def find_top_K_sbert(self, quert_feature_sbert, assets_features_sbert, k):
        sbert_similarities = quert_feature_sbert @ assets_features_sbert.T
        values, indices = torch.topk(sbert_similarities, k)
        return indices.tolist()

    def find_top_K_clip(self, query_feature_clip, k):
        query_feature_clip /= query_feature_clip.norm(dim=-1, keepdim=True)
        clip_similarities_1 = query_feature_clip.float() @ self.clip_img_features_1.T
        clip_similarities_2 = query_feature_clip.float() @ self.clip_img_features_2.T
        clip_similarities_3 = query_feature_clip.float() @ self.clip_img_features_3.T
        
        clip_similarities = torch.stack([clip_similarities_1, clip_similarities_2, clip_similarities_3]).mean(dim=0)
        _, indices = torch.topk(clip_similarities, k)
        return indices.tolist()[0]


def convert_building_format(building_data):
    converted_data = building_data.copy()
    converted_data['location'] = tuple(building_data['location'])
    converted_data['distance_to_roads'] = building_data['distance_to_roads'][0]
    return converted_data

def convert_all_buildings(json_data):
    converted_buildings = {}
    for building_id, building_data in json_data.items():
        converted_buildings[building_id] = convert_building_format(building_data)
    return converted_buildings


def main(args):   
    device = args.device
    assets_annotations_path = os.path.join(args.asset_data_path, 'assets_renders')
    assets_path = os.path.join(args.asset_data_path, 'assets_filtered')
    assets_renders_path = os.path.join(args.asset_data_path, 'assets_renders')
    estimated_dimensions_path = os.path.join(args.asset_data_path, 'assets_features', 'estimated_dimensions.json')
    
    buildings_data_path = args.buildings_data_path
    output_dir = os.path.dirname(buildings_data_path)
    buildings_data_output_path = os.path.join(output_dir, 'selected_buildings.pkl')
    
    if buildings_data_path.endswith('.pkl'):
        with open(buildings_data_path, 'rb') as f:
            buildings_data = pickle.load(f)
    else:
        with open(buildings_data_path, 'r') as f:
            buildings_data = json.load(f)
        buildings_data = convert_all_buildings(buildings_data)

    assets_num = len(os.listdir(assets_path))
    print(f"Total number of assets available: {assets_num}")
    
    with open(estimated_dimensions_path, 'r') as f:
        estimated_dimensions = json.load(f)
    
    assets_annotations = glob.glob(f'{assets_annotations_path}/*.glb')
    assets_annotations_num = len(assets_annotations)
    print("total numer of annotations available: " + str(assets_annotations_num))
    
    building_selector = Building_Selector(device)
    
    for i in tqdm(buildings_data.keys()):
        candidates = building_selector.select(buildings_data[i])
        buildings_data[i]['asset candidates'] = candidates
        
    output_txt_path = os.path.join(output_dir, 'output.txt')
    with open(output_txt_path, 'w') as file:
        for key, value in buildings_data.items():
            file.write(f'{key}: {value}\n')
            file.write('\n')
    
    with open(buildings_data_output_path, 'wb') as f:
        buildings_data = convert_int64_to_float32(buildings_data)
        pickle.dump(buildings_data, f)
   

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--buildings_data_path', type=str, default='./planning_result/layout_1/plan_iteration_0.json')
    parser.add_argument('--asset_data_path',type=str, default='../dataset/CityCraft_Buildings/assets')    
    parser.add_argument('--device', type=str, default='cuda:0')
    args = parser.parse_args()
    main(args)
"""
    Extract features for training data.
"""
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
from torchvision import transforms
import numpy as np
from PIL import Image
import argparse
import os

import h5py # save data as hdf5 format
from diffusers.models import AutoencoderKL
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

"""
    Class ratio counting dataset. 
    Input: Image directory
    Output: 1. VAE latents (tensor) 2. 1 x C class ratio (numpy array) 
"""
class RatioCountingDataset(Dataset):
    def __init__(self, img_dir):
        self.img_dir = img_dir
        self.image_names = sorted(os.listdir(img_dir))
        self.palette = self.get_palette()
        self.num_classes = len(self.palette)
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5], inplace=True),
        ])


    # predefined palette    
    def get_palette(self):
        palette = [
            [85, 107, 47],  # ground -> OliveDrab
            [0, 255, 0],  # vegetation -> Green
            [255, 165, 0],  # building -> orange
            [255, 0, 255],  # rail -> Magenta
            [200, 200, 200],  # traffic Roads ->  grey
            [255, 255, 0],  # Footpath  ->  yellow
            [0, 191, 255]  # water ->  skyblue
        ]
        return palette
        
        
    """
    converts a RGB semantic field mask (H, W, 3) to (H, W, C) where the last dim is a one-hot encoding vector of C classes
    """
    def rgb_to_onehot(self, rgb):
        semantic_map = []
        palette = self.palette
        
        for colour in palette:
            equality = np.equal(rgb, colour)
            class_map = np.all(equality, axis=-1)
            semantic_map.append(class_map)
        semantic_map = np.stack(semantic_map, axis=-1).astype(np.float32)
        return semantic_map

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        img_name = self.image_names[idx] # whole dataset
        img_path = os.path.join(self.img_dir, img_name)
        img = Image.open(img_path).convert("RGB")
        img_rgb = np.array(img)
        img_onehot = self.rgb_to_onehot(img_rgb) 
        img_label = np.argmax(img_onehot, axis=2)
        img_ratio = np.zeros((self.num_classes, 1))
        for i in range(self.num_classes):
            img_ratio[i] = (img_label==i).sum()
        
        # normalized class ratio
        img_ratio = img_ratio / (img_label.size)
         
        # normalized img tensor
        img = self.transform(img)
        return img, img_ratio


def main(args):
    """
        Extracting VAE latents features and class ratios of training images.
    """
    assert torch.cuda.is_available(), "Exrtacting requires at least one GPU."
       
    os.makedirs(args.features_path, exist_ok=True)
    
    vae = AutoencoderKL.from_pretrained(args.vae).to(args.device)
    
    dataset = RatioCountingDataset(args.data_path)
    
    loader = DataLoader(
        dataset, batch_size=1, shuffle=True, num_workers=8
    )
    
    # x: normalized image, no further process is needed
    # y: semantic ratio
    for i, (x, y) in tqdm(enumerate(loader), total=len(loader)):
        x = x.to(args.device)
        with torch.no_grad():
            x = vae.encode(x).latent_dist.sample().mul_(args.vae_scaling_factor) # scaling factor calculated from train set

        # save data as hdf5 format
        x = x.detach().cpu().numpy()
        y = y.detach().numpy()
            
        hdf_file_name = f'{args.features_path}/{i}.h5'
        with h5py.File(hdf_file_name, 'a') as hdf:
            hdf.create_dataset('vae_features', data=x)
            hdf.create_dataset('class_ratios', data=y)

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, default="../CityCraft_OSM/layouts")
    parser.add_argument("--features-path", type=str, default="../CityCraft_OSM/features/image_ratio_features")
    parser.add_argument("--vae", type=str, default="stabilityai/sdxl-vae")
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--vae-scaling-factor", type=float, default=0.11513489484786987)
    args = parser.parse_args()
    main(args)

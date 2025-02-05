# calculate the normalizing factor for a given dataset

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

class ImageSketchDataset(Dataset):
    def __init__(self, img_dir, sketch_dir):
        self.img_dir = img_dir
        self.sketch_dir = sketch_dir
        self.image_names = sorted(os.listdir(img_dir))
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5], inplace=True),
        ])

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        img_name = self.image_names[idx] # whole dataset
        img_path = os.path.join(self.img_dir, img_name)
        img = Image.open(img_path).convert("RGB")

        sketch_name = img_name.replace('original', 'processed')
        sketch_path = os.path.join(self.sketch_dir, sketch_name)
        sketch = Image.open(sketch_path).convert("RGB")

        # normalized img tensor
        img = self.transform(img)
        sketch = self.transform(sketch)
        return img, sketch


def main(args):
    device = "cuda:7"
    vae = AutoencoderKL.from_pretrained("stabilityai/sdxl-vae").to(device)
    vae.eval()

    dataset = ImageSketchDataset(args.image_dir, args.sketch_dir)
    loader = DataLoader(
        dataset, batch_size=1, shuffle=True, num_workers=8
    )
    
    all_latents_x = []
    all_latents_y = []

    for i, (x, y) in tqdm(enumerate(loader), total=len(loader)):
        x = x.to(device) # image
        y = y.to(device) # sketch
        with torch.no_grad():
            x = vae.encode(x).latent_dist.sample()
            y = vae.encode(y).latent_dist.sample()
            all_latents_x.append(x.cpu())
            all_latents_y.append(y.cpu())

    all_latents_tensor_x = torch.cat(all_latents_x)
    all_latents_tensor_y = torch.cat(all_latents_y)

    std_x = all_latents_tensor_x.std().item()
    std_y = all_latents_tensor_y.std().item()
    
    normalizer_x = 1 / std_x
    normalizer_y = 1 / std_y

    print(f'{normalizer_x = }')
    print(f'{normalizer_y = }')



if __name__ == "__main__":
    # Default args here will train DiT-XL/2 with the hyperparameters we used in our paper (except training iters).
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", type=str, default='/data/jd_data/fast-DiT/jd/osm_data_new/768/08_07/image_sketch/images')
    parser.add_argument("--sketch-dir",type=str,default='/data/jd_data/fast-DiT/jd/osm_data_new/768/08_07/image_sketch/sketches')
    args = parser.parse_args()
    main(args)

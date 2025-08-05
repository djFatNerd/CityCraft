# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""
A minimal training script for DiT.
"""
import torch
# the first flag below was False when we tested this script but True makes A100 training a lot faster:
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision.datasets import ImageFolder
from torchvision import transforms
import numpy as np
from collections import OrderedDict
from PIL import Image
from copy import deepcopy
from glob import glob
from time import time
import argparse
import logging
import os
from accelerate import Accelerator
import sys

from models import DiT_models
from utils.diffusion import create_diffusion
from diffusers.models import AutoencoderKL

from patch_conv import convert_model
import wandb
import h5py

#################################################################################
#                             Training Helper Functions                         #
#################################################################################

@torch.no_grad()
def update_ema(ema_model, model, decay=0.9999):
    """
    Step the EMA model towards the current model.
    """
    ema_params = OrderedDict(ema_model.named_parameters())
    model_params = OrderedDict(model.named_parameters())

    for name, param in model_params.items():
        name = name.replace("module.", "")
        # TODO: Consider applying only to params that require_grad to avoid small numerical changes of pos_embed
        ema_params[name].mul_(decay).add_(param.data, alpha=1 - decay)


def requires_grad(model, flag=True):
    """
    Set requires_grad flag for all parameters in a model.
    """
    for p in model.parameters():
        p.requires_grad = flag


def create_logger(logging_dir):
    """
    Create a logger that writes to a log file and stdout.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='[\033[34m%(asctime)s\033[0m] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(), logging.FileHandler(f"{logging_dir}/log.txt")]
    )
    logger = logging.getLogger(__name__)
    return logger


# read OSM data stored in HDF5 format
# return each item as (vae_latent_features, class_ratio)
class OSM_HDF5_Dataset(Dataset):
    def __init__(self, features_dir):
        self.features_dir = features_dir
        self.features_files = os.listdir(features_dir)

    def __len__(self):
        return len(self.features_files)

    def __getitem__(self, idx):
        feature_file_name = self.features_files[idx]
        # feature_file_name = self.features_files[0] # overfitting tests
        feature_file_path = os.path.join(self.features_dir, feature_file_name)
        
        with h5py.File(feature_file_path, 'r') as hdf:
            # Access each dataset by name
            vae_features = hdf['vae_features'][:]
            class_ratios = hdf['class_ratios'][:]
        
        return torch.from_numpy(vae_features), torch.from_numpy(class_ratios)
    
#################################################################################
#                                  Training Loop                                #
#################################################################################


# load pretrained model
def load_model(model_name):
        checkpoint = torch.load(model_name, map_location=lambda storage, loc: storage)
        model_dict = checkpoint["model"]
        ema_dict = checkpoint["ema"]
        return  model_dict , ema_dict


def main(args):
    """
    Trains a new DiT model.
    """
    assert torch.cuda.is_available(), "Training currently requires at least one GPU."

    # Setup accelerator:
    accelerator = Accelerator()
    device = accelerator.device    
    
    # Setup an experiment folder:
    if accelerator.is_main_process:        
        os.makedirs(args.results_dir, exist_ok=True)  # Make results folder (holds all experiment subfolders)
        experiment_index = len(glob(f"{args.results_dir}/*"))
        model_string_name = args.model.replace("/", "-")  # e.g., DiT-XL/2 --> DiT-XL-2 (for naming folders)
        experiment_dir = f"{args.results_dir}/{experiment_index:03d}-{model_string_name}"  # Create an experiment folder
        checkpoint_dir = f"{experiment_dir}/checkpoints"  # Stores saved model checkpoints
        os.makedirs(checkpoint_dir, exist_ok=True)
        logger = create_logger(experiment_dir)
        logger.info(f"New xperiment directory created at {experiment_dir}")
        
        if args.use_wandb:
            wandb.login(key='', timeout=30)
            wandb.init(entity='',
                       project='',
                       reinit=True,
                       settings=wandb.Settings(start_method='fork'))
        
        

    # Create model:
    assert args.image_size % 8 == 0, "Image size must be divisible by 8 (for the VAE encoder)."
    latent_size = args.image_size // 8
    model = DiT_models[args.model](
        input_size=latent_size,
    )
    # use wrap_model
    # Note that parameter initialization is done within the DiT constructor
    model = convert_model(model, splits=8).to(device)
    
    # if load pretrained model
    previous_epochs = 0
    if(args.ckpt):
        previous_epochs = int(args.ckpt.split("/")[-1].split(".")[0])
        ckpt_path = str(args.ckpt)
        model_dict, ema_dict = load_model(ckpt_path)
        model.load_state_dict(model_dict)
        if accelerator.is_main_process:
            logger.info(f"loading checkpoint from {ckpt_path}")
        
    
    ema = deepcopy(model).to(device)  # Create an EMA of the model for use after training
    requires_grad(ema, False)
    diffusion = create_diffusion(timestep_respacing="")  # default: 1000 steps, linear noise schedule
    
    if accelerator.is_main_process:
        logger.info(f"DiT Parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Setup optimizer (we used default Adam betas=(0.9, 0.999) and a constant learning rate of 1e-4 in our paper):
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0)

    # Setup data:
    features_dir = args.feature_path
    dataset = OSM_HDF5_Dataset(features_dir)
    loader = DataLoader(
        dataset,
        batch_size=int(args.global_batch_size // accelerator.num_processes),
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True,
        drop_last=True
    )
    if accelerator.is_main_process:
        logger.info(f"Dataset contains {len(dataset):,} images ({args.feature_path})")

    # Prepare models for training:
    update_ema(ema, model, decay=0)  # Ensure EMA is initialized with synced weights
    model.train()  # important! This enables embedding dropout for classifier-free guidance
    ema.eval()  # EMA model should always be in eval mode
    model, opt, loader = accelerator.prepare(model, opt, loader)

    # Variables for monitoring/logging purposes:
    train_steps = 0
    log_steps = 0
    running_loss = 0
    start_time = time()
    
    train_epochs = previous_epochs
    
    if accelerator.is_main_process:
        logger.info(f"Training for {args.epochs} epochs...")
    for epoch in range(train_epochs, args.epochs):
        if accelerator.is_main_process:
            logger.info(f"Beginning epoch {epoch}...")
            
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            x = x.squeeze(dim=1)
            y = y.squeeze(dim=1)
            t = torch.randint(0, diffusion.num_timesteps, (x.shape[0],), device=device)
            model_kwargs = dict(y=y)
            if args.condition:
                loss_dict = diffusion.training_losses(model, x, t, model_kwargs)
            else:       
                loss_dict = diffusion.training_losses(model, x, t)
            
            loss = loss_dict["loss"].mean()
            opt.zero_grad()
            accelerator.backward(loss)
            opt.step()
            update_ema(ema, model)

            # Log loss values:
            running_loss += loss.item()
            log_steps += 1
            train_steps += 1
            if train_steps % args.log_every == 0:
                # Measure training speed:
                torch.cuda.synchronize()
                end_time = time()
                steps_per_sec = log_steps / (end_time - start_time)
                # Reduce loss history over all processes:
                avg_loss = torch.tensor(running_loss / log_steps, device=device)
                avg_loss = avg_loss.item() / accelerator.num_processes
                if accelerator.is_main_process:
                    logger.info(f"(step={train_steps:07d}) Train Loss: {avg_loss:.4f}, Train Steps/Sec: {steps_per_sec:.2f}")
                    
                    # use_wandb
                    if args.use_wandb:
                        wandb.log({f'train Loss': avg_loss, f'Train Steps/Sec':steps_per_sec}, step=train_steps)
                # Reset monitoring variables:
                running_loss = 0
                log_steps = 0
                start_time = time()   
                
                    
        if train_epochs % args.ckpt_every_epoch == 0 and train_epochs > 0:
            if accelerator.is_main_process:
                    checkpoint = {
                        "model": model.module.state_dict(),
                        "ema": ema.state_dict(),
                        "opt": opt.state_dict(),
                        "args": args
                    }
                    checkpoint_path = f"{checkpoint_dir}/{train_epochs:07d}.pt"
                    torch.save(checkpoint, checkpoint_path)
                    logger.info(f"Saved checkpoint to {checkpoint_path}")
                    
        train_epochs+= 1

    model.eval()  # important! This disables randomized embedding dropout
    # do any sampling/FID calculation/etc. with ema (or model) in eval mode ...
    
    if accelerator.is_main_process:
        logger.info("Done!")
        if args.use_wandb:
            wandb.finish()


if __name__ == "__main__":
    # Default args here will train DiT-XL/2 with the hyperparameters we used in our paper (except training iters).
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", type=str, default=None) # training with condition or not

    # parser.add_argument("--feature-path", type=str, default="features")
    # parser.add_argument("--results-dir", type=str, default="results/OSM/h5_bf16/unconditional_60370/no_mixed_precision_overfitting")
    parser.add_argument("--results-dir", type=str, default="/data1/jd/DiT_OSM_Training_Results")
    # parser.add_argument("--model", type=str, choices=list(DiT_models.keys()), default="DiT-XL/2")
    parser.add_argument("--epochs", type=int, default=20000)
    # parser.add_argument("--global-batch-size", type=int, default=256)
    parser.add_argument("--global-seed", type=int, default=0)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--vae", type=str, choices=["ema", "mse"], default="ema")  # Choice doesn't affect training
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--log-every", type=int, default=1)
    parser.add_argument("--ckpt-every", type=int, default=50_000)
    
    # personal arguments
    parser.add_argument("--model", type=str, choices=list(DiT_models.keys()), default="DiT-B/2")
    parser.add_argument("--feature-path", type=str, default="/data/jd_data/data1/jd/osm_data_new/processed_features/04_07")
    parser.add_argument("--image-size", type=int, default=768)
    # parser.add_argument("--num-classes", type=int, default=1) # just do unconditional
    parser.add_argument("--global-batch-size", type=int, default=768)
    
    parser.add_argument("--ckpt", type=str, default=None) # pretrained model path
    parser.add_argument('--use-wandb', action='store_true', 
                    help='whether to use Weights & Biases for logging')
    
    parser.add_argument("--ckpt-every-epoch", type=int, default=10)
    
    args = parser.parse_args()
    main(args)
    
    '''
        To train, run:
            accelerate launch --multi_gpu --num_processes 8 --mixed_precision bf16 train.py --model DiT-S/8 --ckpt-every-epoch 10 --global-batch-size 256 --ckpt /data/jd_data/fast-DiT/results/OSM/h5_bf16/unconditional_16000/001-DiT-S-8/checkpoints/0005080.pt --lr 1e-5
    
    '''
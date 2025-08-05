"""
Sample new images unconditionally from a pre-trained DiT.

"""
import torch
import os
import sys

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
from torchvision.utils import save_image
from utils.diffusion import create_diffusion
from utils.download import find_model
from models import DiT_models

from diffusers.models import AutoencoderKL

import argparse
from torch.utils.data import Dataset, DataLoader
from patch_conv import convert_model

def main(args):
    # create output dir
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Setup PyTorch:
    torch.manual_seed(args.seed)
    torch.set_grad_enabled(False)
    device = args.device
    
    # Load model:
    latent_size = args.image_size // 8
    model = DiT_models[args.model](
        input_size=latent_size,
    )
    
    model = convert_model(model, splits=8)
    model = model.to(device)
    
    # load:
    state_dict = find_model(args.ckpt)
    model.load_state_dict(state_dict, strict=False)
    model.eval()  # important!
    
    # diffusion
    diffusion = create_diffusion(str(args.num_sampling_steps))
    
    # vae
    vae = AutoencoderKL.from_pretrained("stabilityai/sdxl-vae").to(device)
    # noise
    n = args.num_samples  # sample batch size
    z = torch.randn(n, 4, latent_size, latent_size, device=device)
    z = torch.cat([z, z], 0) # cfg
    model_kwargs = dict(y=None, cfg_scale=args.cfg_scale)
    
    # sample
    samples = diffusion.p_sample_loop(
        model.forward_with_cfg, z.shape, z, clip_denoised=False, model_kwargs=model_kwargs, progress=True, device=device
    )
    samples, _ = samples.chunk(2, dim=0)  # Remove null class samples
    samples = vae.decode(samples / args.vae_scale_factor).sample
    
    # save
    for i in range(args.num_samples):
        save_image(samples[i], args.output_dir + "/" + args.output_name + f"_{i}.png", normalize=True, value_range=(-1, 1))

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, default="cuda:7")
    parser.add_argument("--seed", type=int, default=2024)
    parser.add_argument("--vae_scale_factor", type=float, default=0.11513489484786987)
    parser.add_argument("--cfg-scale", type=float, default=4.0)
    parser.add_argument("--model", type=str, default="DiT-B/2")
    parser.add_argument("--image-size", type=int, default=768)
    parser.add_argument("--num-sampling-steps", type=int, default=1000)
    parser.add_argument("--ckpt", type=str, default='../pretrained_models/uncondition_generation.pt', help="path to a DiT checkpoint")
    parser.add_argument("--num-samples", type=int, default=8)
    parser.add_argument("--output-dir", type=str, default="./samples")
    parser.add_argument("--output-name", type=str, default="sample_uncondition")
    args = parser.parse_args()
    main(args)
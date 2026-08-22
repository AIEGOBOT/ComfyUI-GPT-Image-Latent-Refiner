# ComfyUI GPT Image Latent Refiner

`GPT Image Latent Refiner` is a ComfyUI post-processing node for reducing recurring
dot noise, stippling, grime, and tiled micro-textures while retaining the original
composition. It runs a compact residual network in one of three VAE latent spaces.

## Profiles

| Profile | Status | Intended behavior |
|---|---|---|
| `qwen` | Recommended default | Best observed cleanup/preservation balance |
| `flux2` | Stable alternative | Preserves more source detail with milder cleanup |
| `sdxl` | Experimental | Stronger reconstruction drift; use only after comparison |

The node exposes a `strength` control from `0.0` to `2.0`. A value of `1.0` is the
trained correction, `0.0` is a true bypass, and values above `1.0` extrapolate the
learned residual.

## Local installation

Place or link this repository under `ComfyUI/custom_nodes`, install the Python
dependencies into ComfyUI's environment, and restart ComfyUI.

```powershell
& '<ComfyUI>\venv\Scripts\python.exe' -m pip install -r requirements.txt
```

The project intentionally does not bundle checkpoints or VAE weights. Install the
files under the following paths:

```text
ComfyUI/models/gpt_image_latent_refiner/qwen/model.pt
ComfyUI/models/gpt_image_latent_refiner/flux2/model.pt
ComfyUI/models/gpt_image_latent_refiner/sdxl/model.pt

ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/diffusion_pytorch_model.safetensors
ComfyUI/models/vae/GPT-Image-Latent-Refiner/flux2/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/flux2/diffusion_pytorch_model.safetensors
ComfyUI/models/vae/GPT-Image-Latent-Refiner/sdxl/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/sdxl/diffusion_pytorch_model.safetensors
```

The node validates the selected profile, latent channel count, checkpoint metadata,
and VAE files before inference. It will not silently combine incompatible assets.

## Node

- Node ID: `indii.GPTImageLatentRefiner`
- Display name: `GPT Image Latent Refiner`
- Category: `GPT Image/refinement`
- Inputs: `image`, `profile`, `strength`, `device`, `tile_vae`
- Output: `image`

Start with `qwen`, `strength=1.0`, `device=auto`, and `tile_vae=true`. Process one
large image at a time on a 16 GB GPU.

## Repository scope

This repository contains only the ComfyUI runtime, dependency metadata, and one
portable example workflow. Training code, datasets, checkpoints, VAE weights,
generated images, and private experiment notes are intentionally excluded.

## Distribution status

No project-wide redistribution license has been selected yet. Until a license and
the model/VAE redistribution terms are reviewed, treat this repository and its
weights as private development material.

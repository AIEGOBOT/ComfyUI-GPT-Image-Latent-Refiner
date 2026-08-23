# ComfyUI GPT Image Latent Refiner

**English** | [한국어](README.ko.md)

`GPT Image Latent Refiner` is a ComfyUI post-processing node for reducing recurring
dot noise, stippling, grime, and tiled micro-textures while retaining the original
composition. It runs a compact residual network in one of three VAE latent spaces.

## Origin and scope

This project was inspired by Larryvrh's
[GPT Image 2 Artifact Cleaner](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner),
including its latent-residual approach to suppressing GPT Image 2 artifacts. The
refiner checkpoints in this repository were trained separately on a self-curated
dataset of 75 paired artifact/clean images. The original project's checkpoint is not
redistributed here.

The upstream project uses a FLUX.2-VAE pipeline. This project packages the
approach as a native ComfyUI node and provides three separately trained VAE profiles:
Qwen Image, FLUX.2, and SDXL. The upstream source is distributed under its own
[PolyForm Noncommercial License 1.0.0](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner/blob/main/LICENSE).

## Profiles

| Profile | Status | Intended behavior |
|---|---|---|
| `qwen` | Recommended default | Best observed cleanup/preservation balance |
| `flux2` | Stable alternative | Preserves more source detail with milder cleanup |
| `sdxl` | Portrait alternative | Stronger reconstruction drift, but may be more effective than Qwen or FLUX.2 on photorealistic portrait photos |

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

## Recommended SeedVR2 workflow

The refiner can be used by itself, but its benefit was most noticeable in the
author's tests when it was placed before SeedVR2. It first suppresses recurring
dots and unstable micro-textures so that SeedVR2 is less likely to reconstruct or
amplify them as image detail.

The included
[GPT Image Refiner + SeedVR2 workflow](example_workflows/GPT_Image_Refiner_SeedVR2.json)
uses this sequence:

```text
Input -> GPT Image Latent Refiner -> 0.5x area downscale -> SeedVR2 restoration
      -> wavelet color correction -> CAS -> final output
```

The example uses the `qwen` refiner profile and `seedvr2_7b_fp16.safetensors`.
Based on the author's comparative testing:

- **Recommended:** SeedVR2 7B FP16 for the best observed quality and artifact
  suppression in this workflow.
- **Low-VRAM alternative:** `seedvr2_7b_int8_convrot.safetensors`. It keeps the
  7B architecture with lower memory use, but may lose quality versus FP16.
- **Caution:** 3B or more aggressively quantized variants may reintroduce or
  emphasize artifacts. This is an observed workflow-specific tendency, not a
  universal result for every image.

The example also requires ComfyUI's native SeedVR2 nodes, ComfyUI Essentials,
ComfyUI-Easy-Use, and rgthree-comfy. Model weights and those optional node packs
are not bundled with this repository.

## Repository scope

This repository contains only the ComfyUI runtime, dependency metadata, and
portable example workflows. Training code, datasets, checkpoints, VAE weights,
generated images, and private experiment notes are intentionally excluded.

## Third-party models

VAE weights are not part of this repository or its license. Obtain them separately
from their official sources and follow their respective terms:

- [Qwen/Qwen-Image](https://huggingface.co/Qwen/Qwen-Image) — Apache License 2.0
- [FLUX.2 autoencoder](https://github.com/black-forest-labs/flux2#flux2-autoencoder) — Apache License 2.0
- [Stable Diffusion XL Base 1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) — CreativeML Open RAIL++-M

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the complete attribution and
distribution boundary.

## License

Unless a specific file states otherwise, this repository's code and residual
checkpoints released by this project are available under the
[PolyForm Noncommercial License 1.0.0](LICENSE). You may use, modify, and share them
for permitted noncommercial purposes under that license. Commercial use is not
granted.

The 75-pair training dataset, source images, third-party VAE weights, and the original
GPT Image 2 Artifact Cleaner checkpoint are not distributed by this repository. See
[NOTICE](NOTICE) for project attribution.

## Documentation languages

Public-facing documentation for this project is maintained in both English and
Korean. When legal translations differ, the English legal files and the authoritative
upstream license texts control.

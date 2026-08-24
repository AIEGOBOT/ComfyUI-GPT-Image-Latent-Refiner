# ComfyUI GPT Image Latent Refiner

<img src="assets/registry-banner.png" width="100%" alt="Abstract GPT Image Latent Refiner banner showing noisy tiled texture becoming clean flowing detail through a latent cube lattice">

[![CI](https://github.com/AIEGOBOT/ComfyUI-GPT-Image-Latent-Refiner/actions/workflows/ci.yml/badge.svg)](https://github.com/AIEGOBOT/ComfyUI-GPT-Image-Latent-Refiner/actions/workflows/ci.yml)

**English** | [한국어](README.ko.md)

`GPT Image Latent Refiner` is a ComfyUI post-processing node—not an image
generator—for reducing recurring dot noise, stippling, grime, and tiled
micro-textures in GPT Image-family outputs. It requires no OpenAI API key and runs
the models and images locally.

## Key features and cautions

- The repository bundles all three project-trained `qwen`, `flux2`, and `sdxl`
  refiner checkpoints. The node discovers them automatically; no separate refiner
  checkpoint download is required.
- Third-party Qwen Image, FLUX.2, and SDXL VAEs are not bundled. Download them from
  their official sources and install them in the documented directories.
- The refiner works on its own, but the change may be subtle. In the author's
  testing, its benefit was much more visible when used as a preprocessing stage
  before SeedVR2.
- The model was trained to retain the source composition where possible, but real
  details may still change depending on `strength`, profile, and input. Compare at
  a lower strength first for important images.
- This node targets a specific family of GPT Image artifacts. It is not a general
  denoiser or a replacement for an image-generation model.

## Profiles

| Profile | Status | Intended behavior |
|---|---|---|
| `qwen` | Recommended default | Best observed cleanup/preservation balance |
| `flux2` | Stable alternative | Preserves more source detail with milder cleanup |
| `sdxl` | Portrait alternative | Stronger reconstruction drift, but may be more effective than Qwen or FLUX.2 on photorealistic portrait photos |

The node exposes a `strength` control from `0.0` to `2.0`. A value of `1.0` is the
trained correction, `0.0` is a true bypass, and values above `1.0` extrapolate the
learned residual.

## Install with ComfyUI Manager

Open **ComfyUI Manager**, search for **GPT Image Latent Refiner**, and select
**Install**. Restart ComfyUI after installation.

The Manager package includes the Qwen, FLUX.2, and SDXL refiner checkpoints. The
third-party VAEs are not bundled, so download them separately using the paths in
[Required VAEs and paths](#required-vaes-and-paths).

## Manual Windows installation

Restart ComfyUI after installation. The following commands are for PowerShell.

### ComfyUI Portable

Run these commands from the Portable root. The repository will be installed at
`ComfyUI_windows_portable/ComfyUI/custom_nodes/ComfyUI-GPT-Image-Latent-Refiner`.

```powershell
Set-Location 'C:\ComfyUI_windows_portable'
git clone https://github.com/AIEGOBOT/ComfyUI-GPT-Image-Latent-Refiner.git '.\ComfyUI\custom_nodes\ComfyUI-GPT-Image-Latent-Refiner'
& '.\python_embeded\python.exe' -m pip install -r '.\ComfyUI\custom_nodes\ComfyUI-GPT-Image-Latent-Refiner\requirements.txt'
```

### ComfyUI Desktop

Do not install into the Desktop application's internal `resource\ComfyUI` folder.
Desktop manages that folder and may reset its contents during an update. Use the
`custom_nodes` folder under the user data location selected during Desktop setup.

Open the built-in **Terminal** from Desktop's bottom panel and confirm that the
current location contains `custom_nodes`, then run the commands below. The
Terminal's `python` points to Desktop's Python environment, so the dependencies are
installed into the same environment that runs ComfyUI.

```powershell
git clone https://github.com/AIEGOBOT/ComfyUI-GPT-Image-Latent-Refiner.git '.\custom_nodes\ComfyUI-GPT-Image-Latent-Refiner'
python -m pip install -r '.\custom_nodes\ComfyUI-GPT-Image-Latent-Refiner\requirements.txt'
```

### General Windows venv installation

Use this variant when ComfyUI has a manually created `venv`.

```powershell
Set-Location '<ComfyUI>\custom_nodes'
git clone https://github.com/AIEGOBOT/ComfyUI-GPT-Image-Latent-Refiner.git
& '<ComfyUI>\venv\Scripts\python.exe' -m pip install -r '.\ComfyUI-GPT-Image-Latent-Refiner\requirements.txt'
```

## Required VAEs and paths

All three refiner `model.pt` files are bundled and loaded automatically. For each
third-party VAE, download both `config.json` and
`diffusion_pytorch_model.safetensors` from the official folder below. Keep the file
names unchanged.

| Profile | Official VAE source | Destination directory |
|---|---|---|
| `qwen` | [Qwen Image VAE](https://huggingface.co/Qwen/Qwen-Image/tree/main/vae) | `ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/` |
| `flux2` | [FLUX.2 Small Decoder](https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/tree/main) | `ComfyUI/models/vae/GPT-Image-Latent-Refiner/flux2/` |
| `sdxl` | [SDXL Base 1.0 VAE](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main/vae) | `ComfyUI/models/vae/GPT-Image-Latent-Refiner/sdxl/` |

The final layout must contain all six files:

```text
ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/diffusion_pytorch_model.safetensors
ComfyUI/models/vae/GPT-Image-Latent-Refiner/flux2/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/flux2/diffusion_pytorch_model.safetensors
ComfyUI/models/vae/GPT-Image-Latent-Refiner/sdxl/config.json
ComfyUI/models/vae/GPT-Image-Latent-Refiner/sdxl/diffusion_pytorch_model.safetensors
```

To override a bundled checkpoint, place another compatible `model.pt` at
`ComfyUI/models/gpt_image_latent_refiner/<profile>/model.pt`. External checkpoints
take priority over bundled files. See [models/README.md](models/README.md) for sizes
and [models/SHA256SUMS](models/SHA256SUMS) for the recorded SHA-256 checksums. The
node validates the selected profile, latent channel count, checkpoint metadata, and
VAE files rather than silently mixing incompatible assets.

## Basic usage and node settings

- Node ID: `indii.GPTImageLatentRefiner`
- Display name: `GPT Image Latent Refiner`
- Category: `GPT Image/refinement`
- Inputs: `image`, `profile`, `strength`, `device`, `tile_vae`
- Output: `image`

The minimal graph is `Load Image -> GPT Image Latent Refiner -> Preview/Save Image`.
Start with `qwen`, `strength=1.0`, `device=auto`, and `tile_vae=true`.

| Setting | Meaning |
|---|---|
| `profile` | Qwen, FLUX.2, or SDXL latent profile appropriate for the input |
| `strength` | Learned residual amount. `0.0` bypasses; `1.0` applies the trained correction |
| `device` | `auto` is recommended; explicitly select CUDA or CPU when needed |
| `tile_vae` | Memory-saving tiled encode/decode for the refiner's internal Diffusers VAE |

On CUDA, the runtime checks for native BF16 and safely selects
`BF16 -> FP16 -> FP32`. CPU uses FP32. The Qwen VAE follows the selected CUDA dtype,
while the FLUX.2 and SDXL VAEs remain FP32 for compatibility.

## VRAM and VAE tiling

### Standalone refiner

The profile values—about `7.5 GiB` for Qwen and `4.0 GiB` for FLUX.2 or SDXL—are
conservative free-memory targets passed to ComfyUI's
`model_management.free_memory()` before loading. They do not reserve that amount
of VRAM and are not measured minimum requirements. Actual use varies with image
resolution, batch size, VAE implementation, other loaded models, and offloading
state. Process one large image at a time first.

`tile_vae` affects only the VAE inside this refiner node. Enable it for large inputs
or to avoid an OOM during the refiner VAE stage. With sufficient VRAM, disabling it
is generally faster. Tiling trades lower memory use for additional processing time
and can rarely make tile boundaries visible.

### Refiner + SeedVR2

Standalone refiner use and the combined SeedVR2 workflow have very different
memory requirements. SeedVR2 7B FP16 is substantially heavier than the refiner and
can be replaced by 7B INT8 ConvRot when VRAM is insufficient. Actual use varies
with resolution, GPU, ComfyUI memory offloading, and VAE mode. Test one large image
at a time first.

The included SeedVR2 example uses regular `VAEEncode` and `VAEDecode` nodes for the
SeedVR2 stage. This is separate from the refiner's `tile_vae` option. Replace those
SeedVR2 nodes with ComfyUI's tiled VAE encode/decode nodes only when that stage is
memory-constrained.

## Before / after examples

Each comparison places the unprocessed input on the **left** and the complete
workflow output on the **right**. These are results from the full Refiner + SeedVR2
workflow, not from the refiner node alone.

The SDXL portrait and two cropped dossier details also include Image Comparer-style
animations. Each GIF appears below its static comparison, holds on the input,
reveals the processed result from left to right, and then holds on the final output.

Common settings were refiner `device=auto`, refiner `tile_vae=true`, SeedVR2 7B FP16
with `ema_vae_fp16.safetensors`, regular `VAEEncode`/`VAEDecode`, bicubic target
resizing, wavelet color correction, and CAS `0.35`. The profile and resolution
settings that differ by example are shown below.

| Example | Refiner profile | Strength | Area pre-scale | Target long edge |
|---|---:|---:|---:|---:|
| Photoreal portrait | `sdxl` | `1.0` | `0.5x` | `1920 px` |
| Environment | `qwen` | `1.0` | `0.5x` | `1920 px` |
| Anime illustration | `qwen` | `1.0` | `0.5x` | `1920 px` |
| Night rescue dossier | `flux2` | `1.0` | `1.0x` (no reduction) | `3840 px` |

### Photoreal portrait — SDXL

**Static side-by-side**

[![Static photoreal portrait before and after](assets/examples/example-01-photoreal-portrait-compare.png)](assets/examples/example-01-photoreal-portrait-compare.png)

[Before](assets/examples/example-01-photoreal-portrait-before.jpg) ·
[After](assets/examples/example-01-photoreal-portrait-after-sdxl.png)

**Animated wipe**

[![Animated photoreal portrait before and after](assets/examples/example-01-photoreal-portrait-wipe.gif)](assets/examples/example-01-photoreal-portrait-wipe.gif)

### Environment — Qwen

**Static side-by-side**

[![Static environment before and after](assets/examples/example-02-environment-compare.png)](assets/examples/example-02-environment-compare.png)

[Before](assets/examples/example-02-environment-before.png) ·
[After](assets/examples/example-02-environment-after-qwen.png)

### Anime illustration — Qwen

**Static side-by-side**

[![Static anime illustration before and after](assets/examples/example-03-anime-compare.png)](assets/examples/example-03-anime-compare.png)

[Before](assets/examples/example-03-anime-before.png) ·
[After](assets/examples/example-03-anime-after-qwen.png)

### Night rescue dossier — FLUX.2

**Static side-by-side**

[![Static night rescue dossier before and after](assets/examples/example-04-night-rescue-compare.png)](assets/examples/example-04-night-rescue-compare.png)

[Before](assets/examples/example-04-night-rescue-before.png) ·
[After](assets/examples/example-04-night-rescue-after-flux2.png)

**Cropped animated details**

| Hands, equipment, and boots | Body detail below the face |
|:---:|:---:|
| [![Animated comparison of the dossier hand, equipment, and boot panels](assets/examples/example-04-night-rescue-hands-boots-wipe.gif)](assets/examples/example-04-night-rescue-hands-boots-wipe.gif) | [![Animated comparison of the dossier body below the face](assets/examples/example-04-night-rescue-body-wipe.gif)](assets/examples/example-04-night-rescue-body-wipe.gif) |

The renamed before/after assets are byte-for-byte copies, so their original embedded
metadata is unchanged. Each comparison PNG also carries the processed image's
ComfyUI `prompt` and `workflow` fields plus a `comparison_manifest` field. Exact
settings, GIF animation parameters, dimensions, and SHA-256 hashes are recorded in
[assets/examples/metadata.json](assets/examples/metadata.json).

## Recommended SeedVR2 workflow

The refiner can be used by itself, but its benefit was most noticeable in the
author's tests when it was placed before SeedVR2. It first suppresses recurring
dots and unstable micro-textures so that SeedVR2 is less likely to reconstruct or
amplify them as image detail.

The included
[GPT Image Refiner + SeedVR2 workflow](example_workflows/GPT_Image_Refiner_SeedVR2.json)
uses this sequence:

```text
Input -> GPT Image Latent Refiner -> 0.5x area downscale -> target resize
      -> SeedVR2 restoration -> wavelet color correction -> CAS -> final output
```

The bicubic node sets the target pixel dimensions before SeedVR2 reconstructs and
restores the image at that size. The example JSON uses regular `VAEEncode` and
`VAEDecode` for the SeedVR2 VAE. If that stage runs out of memory, replace those
two nodes with ComfyUI's tiled VAE variants. They are independent of the refiner
node's `tile_vae` switch.

The `0.5x` downscale is intentional but optional. Area downsampling averages fragile
high-frequency patterns before SeedVR2 rebuilds the image. This can reduce the
chance of dot noise and grid-like texture being preserved as detail, but it can
also remove real fine detail or small text. Set the scale to `1.0` or bypass that
node when source preservation matters more.

### SeedVR2 models and dependencies

The example uses the `qwen` refiner profile and SeedVR2 7B FP16.

- **Recommended:** SeedVR2 7B FP16 for the best observed quality and artifact
  suppression in this workflow.
- **Low-VRAM alternative:** `seedvr2_7b_int8_convrot.safetensors`. It keeps the
  7B architecture with lower memory use, but may lose quality versus FP16.
- **Caution:** 3B or more aggressively quantized variants may reintroduce or
  emphasize artifacts. This is an observed workflow-specific tendency, not a
  universal result for every image.

| File | Source / status | Destination |
|---|---|---|
| Qwen, FLUX.2, and SDXL refiner `model.pt` files | Bundled project-trained checkpoints; loaded automatically | `models/gpt_image_latent_refiner/<profile>/model.pt` in this repository |
| SeedVR2 7B FP16 | [Download](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_fp16.safetensors) | `ComfyUI/models/diffusion_models/` |
| SeedVR2 7B INT8 ConvRot | [Download](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_int8_convrot.safetensors) | `ComfyUI/models/diffusion_models/` |
| SeedVR2 VAE FP16 | [Download](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/vae/ema_vae_fp16.safetensors) | `ComfyUI/models/vae/` |

SeedVR2 itself uses the
[native ComfyUI nodes](https://docs.comfy.org/tutorials/utility/seedvr2) in this
example. Update ComfyUI if those nodes are missing. The exact distributed graph
also uses:

| Node pack | Nodes used | Purpose |
|---|---|---|
| [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials) | `ImageCASharpening+` | Final CAS sharpening |
| [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use) | `easy cleanGpuUsed`, `easy clearCacheAll` | GPU-memory and cache cleanup between heavy stages |
| [rgthree-comfy](https://github.com/rgthree/rgthree-comfy) | `Image Comparer (rgthree)` | Interactive comparisons; optional if comparison nodes are removed |

### Difference from Hires Fix / latent upscale

| | Conventional Hires Fix / latent upscale | This SeedVR2 workflow |
|---|---|---|
| Main purpose | Continue diffusion generation at a larger size | Remove recurring artifacts, then restore at the target size |
| Process | Resize a pixel image or latent, then run a second diffusion sampling pass | Latent cleanup, optional downsample, target resize, then one-step SeedVR2 restoration |
| With weak reconstruction | Existing artifacts and softness can remain and become larger | The refiner reduces targeted texture before restoration |
| With strong reconstruction | Face, identity, text, composition, or shapes may change | SeedVR2 can still reinterpret detail, but it is conditioned as a restoration stage |
| Best suited for | Prompt-driven detail expansion and continued generation | Cleanup and reconstruction of an existing image |

Hires Fix is not inherently worse; it is designed for a different goal. For this
artifact-cleaning task, its denoise tradeoff can either preserve unwanted texture
or recompose too much of the image. This workflow separates cleanup from
reconstruction so those roles are easier to control.

See the [full SeedVR2 workflow guide](docs/SEEDVR2_WORKFLOW.md) for a more detailed
stage and memory guide.

## Attribution, third-party components, and license

### Origin and repository scope

This project was inspired by Larryvrh's
[GPT Image 2 Artifact Cleaner](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner),
including its latent-residual approach. The refiner checkpoints in this repository
were trained independently on a self-curated dataset of 75 paired artifact/clean
images. The original project's checkpoint is not included or redistributed here.

The upstream project uses a FLUX.2-VAE pipeline. This project packages the approach
as a native ComfyUI node and provides separately trained Qwen Image, FLUX.2, and
SDXL VAE profiles. The upstream project remains under its own
[PolyForm Noncommercial License 1.0.0](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner/blob/main/LICENSE).
The three bundled `model.pt` files are inference-only releases containing EMA
residual weights and checkpoint metadata; training optimizer state is not included.

This repository contains the ComfyUI runtime, three project-trained inference
checkpoints, dependency metadata, portable example workflows, and the four public
before/after documentation pairs above. Training code, the complete training
dataset, third-party VAE weights, other generated images, and private experiment
notes are intentionally excluded.

### Third-party components

VAE weights and SeedVR2 are not part of this repository or its project license.
Obtain them separately from their official sources and follow their respective
terms:

- [Qwen Image VAE](https://huggingface.co/Qwen/Qwen-Image/tree/main/vae) — Apache License 2.0
- [FLUX.2 Small Decoder](https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/tree/main) — Apache License 2.0
- [Stable Diffusion XL Base 1.0 VAE](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main/vae) — CreativeML Open RAIL++-M
- [ByteDance SeedVR2](https://github.com/ByteDance-Seed/SeedVR) — Apache License 2.0

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the complete attribution and
distribution boundary.

### License

Unless a specific file states otherwise, this repository's code and residual
checkpoints released by this project are available under the
[PolyForm Noncommercial License 1.0.0](LICENSE). You may use, modify, and share them
for permitted noncommercial purposes under that license. Commercial use is not
granted.

The 75-pair training dataset, source images, third-party VAE weights, and the original
GPT Image 2 Artifact Cleaner checkpoint are not distributed by this repository. See
[NOTICE](NOTICE) for project attribution.

### Documentation languages

Public-facing documentation for this project is maintained in both English and
Korean. When legal translations differ, the English legal files and the
authoritative upstream license texts control.

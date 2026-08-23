# GPT Image Latent Refiner + SeedVR2 workflow

**English** | [한국어](SEEDVR2_WORKFLOW.ko.md)

This document explains the design choices behind the included
[example workflow](../example_workflows/GPT_Image_Refiner_SeedVR2.json). The quality
recommendations are based on the author's comparative tests rather than a formal
benchmark, so evaluate important images with the comparison nodes before saving.

## Pipeline overview

```text
Input image
  -> GPT Image Latent Refiner (Qwen profile)
  -> optional 0.5x area downscale
  -> bicubic resize to a 1920 px maximum dimension
  -> native ComfyUI SeedVR2 preprocessing and restoration
  -> wavelet color correction
  -> CAS sharpening
  -> final output
```

### 1. Latent refinement

The Qwen refiner reduces recurring dots, stippling, dirty-looking texture, and
unstable micro-patterns before generative restoration. Its standalone change can
look subtle. Its main role in this graph is to prevent SeedVR2 from treating those
artifacts as valid detail that should be reconstructed and sharpened.

### 2. Optional 0.5x area downscale

Area downsampling combines neighboring pixels. Fine patterns that occupy only one
or two pixels are therefore weakened or averaged out. This deliberately discards
some information and gives SeedVR2 room to rebuild a more coherent texture.

Potential benefits:

- reduces brittle high-frequency dot and grid patterns before reconstruction;
- prevents existing contaminated detail from being enlarged unchanged;
- gives the restoration model a simpler, more coherent structure to rebuild;
- can make the difference between the refined and final image more visible.

The step is optional. Set `ImageScaleBy` to `1.0` or bypass it when:

- the source is already clean or low resolution;
- exact small text, UI elements, product labels, line art, or fabric patterns matter;
- identity-critical facial micro-detail must be preserved;
- the downscaled result loses more real detail than unwanted texture.

The `0.5x` step is not primarily a VRAM control. The following resize establishes a
1920 px maximum dimension, and that actual SeedVR2 processing resolution is the
larger factor in memory use.

### 3. Target resize and SeedVR2 restoration

The bicubic resize establishes the working resolution before native ComfyUI
SeedVR2 preprocessing. SeedVR2 then performs a one-step, restoration-oriented
generative pass. Unlike a simple interpolation filter, it can reconstruct plausible
edges and texture, but it can also invent or reinterpret detail.

Strictly speaking, the bicubic node changes the pixel dimensions and SeedVR2
restores the image at that target size. The complete process is therefore best
described as a **downsample-resize-restore pipeline**, rather than SeedVR2 simply
stretching the image by a fixed scale factor.

The workflow uses `seedvr2_7b_fp16.safetensors`. It produced the best observed
artifact suppression and final texture in the author's tests. Use
`seedvr2_7b_int8_convrot.safetensors` when FP16 creates excessive memory pressure.
The 3B and more aggressively quantized variants were more likely to expose or
emphasize artifacts in these tests; this is a workflow-specific observation, not a
universal ranking of SeedVR2 models.

### 4. SeedVR2 VAE encode/decode and memory

The example JSON loads `ema_vae_fp16.safetensors` and uses regular `VAEEncode` and
`VAEDecode` nodes for the SeedVR2 stage. The default graph does not use tiled VAE
nodes there.

The refiner node's `tile_vae` switch affects only its internal Diffusers VAE. The
later SeedVR2 VAE encode/decode is a separate stage and is not controlled by that
switch. If the SeedVR2 VAE stage runs out of memory, replace the regular nodes with
ComfyUI's tiled VAE encode and decode nodes. Tiling reduces memory use but can be
slower and can rarely make tile boundaries visible.

Judge standalone refiner memory and the combined 7B SeedVR2 workflow separately.
The combined graph is strongly affected by target resolution, SeedVR2 model
precision, offloading state, and VAE mode. Validate with a batch of one at a lower
target resolution first.

### 5. Color correction and CAS

Wavelet color correction references the resized input to reduce color drift from
the restoration pass. CAS then restores restrained local contrast at edges after
the refiner, resizing, and restoration stages. CAS does not create semantic detail;
too much sharpening can reveal residual noise or halos.

## Difference from a conventional Hires Fix

A typical Hires Fix or latent upscale enlarges a generated image or latent and runs
another diffusion sampling pass. It is useful when prompt-driven detail expansion
is desired, but it has an awkward tradeoff for artifact cleanup:

| | Conventional Hires Fix / latent upscale | This workflow |
|---|---|---|
| Primary goal | Continue generation at a larger size | Clean artifacts, then restore the image |
| Control | Prompt, sampler, steps, and denoise strength | Refiner profile, optional downscale, restoration model |
| Low reconstruction strength | Existing artifacts and softness can survive | Refiner removes targeted texture before restoration |
| High reconstruction strength | Face, identity, text, layout, or shapes may change | SeedVR2 can still reinterpret detail, but is used as a restoration model |
| Detail source | A second sampling pass from the generation model | SeedVR2 restoration conditioned on the processed image |

Hires Fix is not inherently inferior. It is simply solving a different problem.
For recurring GPT Image texture artifacts, a second general diffusion pass may
enlarge the artifacts at low denoise or recompose the image at high denoise. The
refiner-plus-SeedVR2 pipeline separates cleanup from reconstruction, which makes
that tradeoff easier to control.

## Dependencies

The SeedVR2 preprocessing, conditioning, and post-processing nodes in this graph
are native ComfyUI nodes. See the
[official native SeedVR2 guide](https://docs.comfy.org/tutorials/utility/seedvr2).
The exact example also uses these external packs:

| Package | Role | Required for the exact graph |
|---|---|---|
| [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials) | CAS sharpening | Yes |
| [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use) | GPU-memory and cache cleanup | Yes |
| [rgthree-comfy](https://github.com/rgthree/rgthree-comfy) | Image comparison | Optional if comparison nodes are removed |

## Models and paths

| Model | Link | Destination |
|---|---|---|
| Qwen refiner checkpoint | Bundled with this repository and loaded automatically | `models/gpt_image_latent_refiner/qwen/model.pt` in this repository |
| Qwen Image VAE | [Official files](https://huggingface.co/Qwen/Qwen-Image/tree/main/vae) | `ComfyUI/models/vae/GPT-Image-Latent-Refiner/qwen/` |
| SeedVR2 7B FP16 | [Download](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_fp16.safetensors) | `ComfyUI/models/diffusion_models/` |
| SeedVR2 7B INT8 ConvRot | [Download](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_int8_convrot.safetensors) | `ComfyUI/models/diffusion_models/` |
| SeedVR2 VAE FP16 | [Download](https://huggingface.co/Comfy-Org/SeedVR2/resolve/main/vae/ema_vae_fp16.safetensors) | `ComfyUI/models/vae/` |

The Qwen VAE destination must contain both `config.json` and
`diffusion_pytorch_model.safetensors`.

The Qwen, FLUX.2, and SDXL refiner checkpoints are bundled as inference-only files.
An external compatible checkpoint at
`ComfyUI/models/gpt_image_latent_refiner/<profile>/model.pt` overrides its bundled
counterpart.

## Limitations

- SeedVR2 is generative restoration, not lossless recovery. It may hallucinate or
  alter detail that is unclear in the source.
- The official SeedVR2 project notes that lightly degraded inputs can occasionally
  receive excessive generated detail or oversharpening. See the
  [official SeedVR2 repository](https://github.com/ByteDance-Seed/SeedVR).
- The `0.5x` downscale can permanently remove real micro-detail before restoration.
- CAS can sharpen remaining noise if its amount is pushed too high.
- Process one large image at a time first, especially with 7B FP16.

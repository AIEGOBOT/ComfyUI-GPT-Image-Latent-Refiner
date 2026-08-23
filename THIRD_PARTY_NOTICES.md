# Third-party notices

**English** | [한국어](THIRD_PARTY_NOTICES.ko.md)

Third-party checkpoints and VAE weights are not bundled with this repository. They
remain subject to their own licenses and must be obtained separately from their
official sources.

## Upstream inspiration and implementation reference

- Project: [GPT Image 2 Artifact Cleaner](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner)
- Author and copyright: Larryvrh, Copyright (c) 2026
- Role: latent-residual artifact-cleaning approach and compact residual-network
  design reference
- License: [PolyForm Noncommercial License 1.0.0](https://github.com/Larryvrh/gpt-image-2-artifact-cleaner/blob/main/LICENSE)
- Bundled asset status: the upstream checkpoint is not included or redistributed

## VAE dependencies

| Profile | Upstream model | License | Bundled here |
|---|---|---|---|
| Qwen Image | [Qwen Image VAE](https://huggingface.co/Qwen/Qwen-Image/tree/main/vae) | Apache License 2.0 | No |
| FLUX.2 | [FLUX.2 Small Decoder](https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/tree/main) | Apache License 2.0 | No |
| SDXL | [SDXL Base 1.0 VAE](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main/vae) | CreativeML Open RAIL++-M | No |

The licenses above apply to the respective third-party components, not to the
original code or residual checkpoints of GPT Image Latent Refiner.

## Optional SeedVR2 example

The included combined workflow references the
[ByteDance SeedVR2 project](https://github.com/ByteDance-Seed/SeedVR), licensed
under Apache License 2.0, and ComfyUI-packaged weights from
[Comfy-Org/SeedVR2](https://huggingface.co/Comfy-Org/SeedVR2). SeedVR2 code and
weights are not included in this repository and remain subject to their own terms.

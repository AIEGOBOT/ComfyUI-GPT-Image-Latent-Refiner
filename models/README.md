# Bundled refiner checkpoints

**English** | [한국어](README.ko.md)

These inference-only checkpoints were trained by this project on the self-curated
75-pair dataset described in the repository README. Each file contains the EMA
residual weights and checkpoint metadata required by the ComfyUI node. Training
optimizer state and redundant non-EMA weights are intentionally omitted.

The released `R_ema` tensors were verified to be identical to the corresponding
training checkpoints before publication.

| Profile | File | Size | SHA-256 |
|---|---|---:|---|
| Qwen | `gpt_image_latent_refiner/qwen/model.pt` | 1,855,465 bytes | `f56de83b01c18c890aa4948393f9029d69596744d711505ac8d581c7dd9af02d` |
| FLUX.2 | `gpt_image_latent_refiner/flux2/model.pt` | 1,929,193 bytes | `32744454f52a32a2e2c8d1a77175f97005b51868ef93c48530eb506b6170d517` |
| SDXL | `gpt_image_latent_refiner/sdxl/model.pt` | 1,800,169 bytes | `5724a88ee116d41bc6dac804eda29fa61d400473079a294585ec771427574142` |

The node uses these files automatically. A compatible checkpoint installed at
`ComfyUI/models/gpt_image_latent_refiner/<profile>/model.pt` takes priority and can
be used as an override.

These project-trained checkpoints are distributed under the repository's
[PolyForm Noncommercial License 1.0.0](../LICENSE). Third-party VAE weights are not
included and remain subject to their respective licenses.

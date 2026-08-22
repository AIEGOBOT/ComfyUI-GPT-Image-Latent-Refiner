"""Memory-aware ComfyUI inference runtime."""

from __future__ import annotations

from contextlib import nullcontext
from threading import RLock

import torch
from torch.nn import functional as F

import comfy.model_management as model_management

from .model import ResidualLatentNet
from .profiles import Profile, get_profile, load_residual_checkpoint
from .vae import VAEAdapter, load_vae


_CACHE_LOCK = RLock()
_RESIDUAL_CACHE: dict[str, ResidualLatentNet] = {}
_VAE_CACHE: dict[str, VAEAdapter] = {}


def _resolve_device(mode: str) -> torch.device:
    if mode == "auto":
        return model_management.get_torch_device()
    if mode == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but PyTorch cannot access a CUDA device")
        return torch.device("cuda:0")
    if mode == "cpu":
        return torch.device("cpu")
    raise ValueError(f"Unsupported device mode: {mode}")


def _autocast_context(device: torch.device):
    if device.type == "cuda":
        return torch.autocast(device_type="cuda", dtype=torch.bfloat16)
    return nullcontext()


def _load_cached(profile: Profile) -> tuple[ResidualLatentNet, VAEAdapter]:
    with _CACHE_LOCK:
        residual = _RESIDUAL_CACHE.get(profile.name)
        if residual is None:
            residual, _metadata = load_residual_checkpoint(profile)
            _RESIDUAL_CACHE[profile.name] = residual

        adapter = _VAE_CACHE.get(profile.name)
        if adapter is None:
            adapter = load_vae(profile, profile.vae_path)
            _VAE_CACHE[profile.name] = adapter
    return residual, adapter


def _pad_to_multiple(image: torch.Tensor, multiple: int = 32) -> tuple[torch.Tensor, int, int]:
    height, width = image.shape[-2:]
    pad_height = (-height) % multiple
    pad_width = (-width) % multiple
    if not pad_height and not pad_width:
        return image, height, width
    mode = "reflect" if height > pad_height and width > pad_width else "replicate"
    return F.pad(image, (0, pad_width, 0, pad_height), mode=mode), height, width


def _configure_tiling(adapter: VAEAdapter, enabled: bool) -> None:
    if enabled and hasattr(adapter.vae, "enable_tiling"):
        adapter.vae.enable_tiling()
    elif not enabled and hasattr(adapter.vae, "disable_tiling"):
        adapter.vae.disable_tiling()


@torch.no_grad()
def refine_images(
    image: torch.Tensor,
    profile_name: str,
    strength: float,
    device_mode: str,
    tile_vae: bool,
) -> torch.Tensor:
    if image.ndim != 4 or image.shape[-1] != 3:
        raise ValueError(f"Expected ComfyUI IMAGE with shape [B,H,W,3], got {tuple(image.shape)}")
    if image.shape[1] < 64 or image.shape[2] < 64:
        raise ValueError("Images must be at least 64x64 pixels")
    if strength == 0.0:
        return image.clone()

    profile = get_profile(profile_name)
    device = _resolve_device(device_mode)
    if device.type == "cuda":
        required = int(profile.estimated_vram_gib * 1024**3)
        model_management.free_memory(required, device)

    residual, adapter = _load_cached(profile)
    vae_dtype = torch.bfloat16 if profile.name == "qwen" and device.type == "cuda" else torch.float32
    residual = residual.to(device=device, dtype=torch.float32).train(False)
    adapter.vae = adapter.vae.to(device=device, dtype=vae_dtype).train(False)
    _configure_tiling(adapter, tile_vae)

    outputs: list[torch.Tensor] = []
    try:
        for sample in image:
            source = sample.permute(2, 0, 1).unsqueeze(0).to(
                device=device,
                dtype=torch.float32,
            )
            source = source.mul(2.0).sub(1.0)
            padded, height, width = _pad_to_multiple(source)
            latent = adapter.encode(padded)
            with _autocast_context(device):
                refined = latent + float(strength) * residual(latent.float())
            decoded = adapter.decode(refined)
            decoded = decoded[:, :, :height, :width]
            output = decoded.add(1.0).mul(0.5).clamp(0.0, 1.0)
            outputs.append(output.permute(0, 2, 3, 1).cpu())
    finally:
        residual.to("cpu")
        adapter.vae.to("cpu")
        if device.type == "cuda":
            model_management.soft_empty_cache()

    return torch.cat(outputs, dim=0)

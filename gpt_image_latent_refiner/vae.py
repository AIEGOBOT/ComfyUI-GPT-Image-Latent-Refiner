"""Local Diffusers VAE loading and profile-specific latent normalization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from .profiles import Profile


@dataclass
class VAEAdapter:
    profile: Profile
    vae: Any

    @property
    def dtype(self) -> torch.dtype:
        return next(self.vae.parameters()).dtype

    def _channel_tensor(self, values: list[float], latent: torch.Tensor) -> torch.Tensor:
        return torch.tensor(values, device=latent.device, dtype=latent.dtype).view(
            1, self.profile.latent_channels, 1, 1
        )

    @torch.no_grad()
    def encode(self, images: torch.Tensor) -> torch.Tensor:
        images = images.to(dtype=self.dtype)
        if self.profile.name == "qwen":
            raw = self.vae.encode(images.unsqueeze(2)).latent_dist.mode()
            if raw.shape[2] != 1:
                raise RuntimeError(f"Qwen VAE returned {raw.shape[2]} latent frames")
            raw = raw.squeeze(2)
            mean = self._channel_tensor(list(self.vae.config.latents_mean), raw)
            std = self._channel_tensor(list(self.vae.config.latents_std), raw)
            return (raw - mean) / std

        raw = self.vae.encode(images).latent_dist.mode()
        if self.profile.name == "sdxl":
            return raw * float(self.vae.config.scaling_factor)
        return raw

    @torch.no_grad()
    def decode(self, latents: torch.Tensor) -> torch.Tensor:
        latents = latents.to(dtype=self.dtype)
        if self.profile.name == "qwen":
            mean = self._channel_tensor(list(self.vae.config.latents_mean), latents)
            std = self._channel_tensor(list(self.vae.config.latents_std), latents)
            decoded = self.vae.decode((latents * std + mean).unsqueeze(2)).sample
            if decoded.shape[2] != 1:
                raise RuntimeError(f"Qwen VAE decoded {decoded.shape[2]} frames")
            return decoded.squeeze(2).float().clamp(-1.0, 1.0)

        raw = latents
        if self.profile.name == "sdxl":
            raw = raw / float(self.vae.config.scaling_factor)
        return self.vae.decode(raw).sample.float().clamp(-1.0, 1.0)


def load_vae(profile: Profile, path: Path) -> VAEAdapter:
    if profile.name == "flux2":
        from diffusers import AutoencoderKLFlux2

        vae = AutoencoderKLFlux2.from_pretrained(path, local_files_only=True)
        latent_channels = int(vae.config.latent_channels)
    elif profile.name == "qwen":
        from diffusers import AutoencoderKLQwenImage

        vae = AutoencoderKLQwenImage.from_pretrained(
            path,
            local_files_only=True,
            torch_dtype=torch.float32,
        )
        latent_channels = int(vae.config.z_dim)
    elif profile.name == "sdxl":
        from diffusers import AutoencoderKL

        vae = AutoencoderKL.from_pretrained(
            path,
            local_files_only=True,
            torch_dtype=torch.float32,
        )
        latent_channels = int(vae.config.latent_channels)
    else:
        raise ValueError(f"Unsupported VAE profile: {profile.name}")

    if latent_channels != profile.latent_channels:
        raise ValueError(
            f"{profile.name} VAE has {latent_channels} latent channels; "
            f"expected {profile.latent_channels}"
        )

    vae = vae.to("cpu").train(False)
    vae.requires_grad_(False)
    if hasattr(vae, "enable_slicing"):
        vae.enable_slicing()
    return VAEAdapter(profile=profile, vae=vae)

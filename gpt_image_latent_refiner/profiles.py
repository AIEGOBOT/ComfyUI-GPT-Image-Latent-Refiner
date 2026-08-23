"""Profile definitions and checkpoint validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import folder_paths
import torch

from .model import ResidualLatentNet


MODEL_DIRECTORY = "gpt_image_latent_refiner"
VAE_DIRECTORY = "GPT-Image-Latent-Refiner"


@dataclass(frozen=True)
class Profile:
    name: str
    latent_channels: int
    normalization: str
    recommendation: str
    estimated_vram_gib: float

    @property
    def checkpoint_path(self) -> Path:
        return Path(folder_paths.models_dir) / MODEL_DIRECTORY / self.name / "model.pt"

    @property
    def vae_path(self) -> Path:
        return Path(folder_paths.models_dir) / "vae" / VAE_DIRECTORY / self.name


PROFILES: dict[str, Profile] = {
    "qwen": Profile(
        name="qwen",
        latent_channels=16,
        normalization="(posterior_mode-latents_mean)/latents_std",
        recommendation="recommended balance",
        estimated_vram_gib=7.5,
    ),
    "flux2": Profile(
        name="flux2",
        latent_channels=32,
        normalization="raw_posterior_mode",
        recommendation="source-preserving alternative",
        estimated_vram_gib=4.0,
    ),
    "sdxl": Profile(
        name="sdxl",
        latent_channels=4,
        normalization="posterior_mode*scaling_factor",
        recommendation="photorealistic portrait alternative",
        estimated_vram_gib=4.0,
    ),
}


def get_profile(name: str) -> Profile:
    try:
        return PROFILES[name]
    except KeyError as error:
        supported = ", ".join(PROFILES)
        raise ValueError(f"Unsupported profile '{name}'. Expected one of: {supported}") from error


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} was not found: {path}")


def validate_profile_files(profile: Profile) -> None:
    _require_file(profile.checkpoint_path, f"{profile.name} checkpoint")
    _require_file(profile.vae_path / "config.json", f"{profile.name} VAE config")
    _require_file(
        profile.vae_path / "diffusion_pytorch_model.safetensors",
        f"{profile.name} VAE weights",
    )


def load_residual_checkpoint(profile: Profile) -> tuple[ResidualLatentNet, dict[str, Any]]:
    validate_profile_files(profile)
    checkpoint = torch.load(profile.checkpoint_path, map_location="cpu", weights_only=True)
    if not isinstance(checkpoint, dict):
        raise ValueError(f"Checkpoint is not a mapping: {profile.checkpoint_path}")

    metadata = checkpoint.get("meta")
    state_dict = checkpoint.get("R_ema")
    if not isinstance(metadata, dict) or not isinstance(state_dict, dict):
        raise ValueError("Checkpoint must contain 'meta' and 'R_ema' mappings")

    architecture = metadata.get("architecture")
    if architecture != "ResidualLatentNet-v1":
        raise ValueError(f"Unsupported checkpoint architecture: {architecture!r}")

    latent_channels = int(metadata.get("latent_channels", -1))
    if latent_channels != profile.latent_channels:
        raise ValueError(
            f"{profile.name} expects {profile.latent_channels} latent channels, "
            f"but the checkpoint declares {latent_channels}"
        )

    declared_vae = metadata.get("vae_type")
    if declared_vae is None and profile.name == "flux2" and latent_channels == 32:
        declared_vae = "flux2"
    if declared_vae != profile.name:
        raise ValueError(
            f"Checkpoint VAE type {declared_vae!r} does not match profile {profile.name!r}"
        )

    declared_normalization = metadata.get("latent_normalization")
    if declared_normalization is not None and declared_normalization != profile.normalization:
        raise ValueError(
            f"Checkpoint normalization {declared_normalization!r} does not match "
            f"{profile.normalization!r}"
        )

    model = ResidualLatentNet(profile.latent_channels).train(False)
    model.load_state_dict(state_dict, strict=True)
    model.requires_grad_(False)
    return model, metadata

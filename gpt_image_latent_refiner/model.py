"""Compact latent residual network used by all supported profiles."""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class ConvNormAct(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.norm = nn.GroupNorm(8, out_channels)
        self.act = nn.SiLU()

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        return self.act(self.norm(self.conv(tensor)))


class ResidualLatentNet(nn.Module):
    """Predict a correction that is added to the input VAE latent."""

    def __init__(self, latent_channels: int) -> None:
        super().__init__()
        self.enc_high = ConvNormAct(latent_channels, 64)
        self.enc_mid = ConvNormAct(64, 128)
        self.bottleneck = ConvNormAct(128, 128)
        self.dec_mid = ConvNormAct(256, 64)
        self.dec_high = ConvNormAct(128, 64)
        self.to_residual = nn.Conv2d(64, latent_channels, kernel_size=3, padding=1)

    def forward(self, latent: torch.Tensor) -> torch.Tensor:
        high = self.enc_high(latent)
        mid = self.enc_mid(F.avg_pool2d(high, kernel_size=2))
        low = self.bottleneck(F.avg_pool2d(mid, kernel_size=2))

        up_mid = F.interpolate(low, size=mid.shape[-2:], mode="nearest")
        up_mid = self.dec_mid(torch.cat((up_mid, mid), dim=1))
        up_high = F.interpolate(up_mid, size=high.shape[-2:], mode="nearest")
        up_high = self.dec_high(torch.cat((up_high, high), dim=1))
        return self.to_residual(up_high)

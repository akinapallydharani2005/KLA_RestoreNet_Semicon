"""Lightweight hybrid super-resolution/denoising model for the KLA restoration challenge.

The network is intentionally small so the full inference script remains fast on GPU.
It upsamples the NoisyLR input with bicubic interpolation and predicts a bounded
residual to recover high-frequency detail while suppressing speckle/Gaussian noise.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class DepthwiseSeparableBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.depth = nn.Conv2d(channels, channels, 3, padding=1, groups=channels)
        self.point = nn.Conv2d(channels, channels, 1)
        self.act = nn.GELU()
        self.norm = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.depth(x)
        y = self.point(y)
        y = self.norm(y)
        return x + self.act(y)


class KLAHybridRestorer(nn.Module):
    """Fast residual CNN for 2x image restoration.

    Input:  Bx1xHxW degraded low-resolution image in approximately [-0.25, 1.25]
    Output: Bx1x(2H)x(2W) restored image, unclipped. Final clipping is done by inference.py.
    """

    def __init__(self, channels: int = 32, depth: int = 6, scale: int = 2, residual_scale: float = 0.20):
        super().__init__()
        self.scale = scale
        self.residual_scale = residual_scale
        self.head = nn.Conv2d(1, channels, 3, padding=1)
        self.blocks = nn.Sequential(*[DepthwiseSeparableBlock(channels) for _ in range(depth)])
        self.tail = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.GELU(),
            nn.Conv2d(channels, 1, 3, padding=1),
        )
        self._init_tail_zero()

    def _init_tail_zero(self) -> None:
        # Makes the initial network behave like bicubic upsampling; training learns a safe residual.
        last = self.tail[-1]
        nn.init.zeros_(last.weight)
        nn.init.zeros_(last.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_lr = torch.clamp(x, -0.25, 1.25)
        up = F.interpolate(x_lr, scale_factor=self.scale, mode="bicubic", align_corners=False)
        f = self.head(up)
        f = self.blocks(f)
        residual = torch.tanh(self.tail(f)) * self.residual_scale
        return up + residual


def build_model(config: dict | None = None) -> KLAHybridRestorer:
    config = config or {}
    return KLAHybridRestorer(
        channels=int(config.get("channels", 32)),
        depth=int(config.get("depth", 6)),
        scale=int(config.get("scale", 2)),
        residual_scale=float(config.get("residual_scale", 0.20)),
    )

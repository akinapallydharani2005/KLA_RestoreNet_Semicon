from __future__ import annotations

import math
from typing import Optional

import numpy as np
from skimage.metrics import structural_similarity as ssim_fn


def psnr(pred: np.ndarray, target: np.ndarray, data_range: float = 1.0) -> float:
    pred = np.clip(pred.astype(np.float32), 0.0, 1.0)
    target = np.clip(target.astype(np.float32), 0.0, 1.0)
    mse = float(np.mean((pred - target) ** 2))
    if mse <= 1e-12:
        return 99.0
    return 20.0 * math.log10(data_range) - 10.0 * math.log10(mse)


def ssim(pred: np.ndarray, target: np.ndarray, data_range: float = 1.0) -> float:
    pred = np.clip(pred.astype(np.float32), 0.0, 1.0)
    target = np.clip(target.astype(np.float32), 0.0, 1.0)
    return float(ssim_fn(target, pred, data_range=data_range))


def lpips_optional(pred: np.ndarray, target: np.ndarray) -> float | None:
    """LPIPS if the optional package is available; otherwise None."""
    try:
        import torch
        import lpips  # type: ignore
        loss_fn = lpips.LPIPS(net="alex")
        p = torch.from_numpy(pred).float()[None, None].repeat(1, 3, 1, 1) * 2 - 1
        t = torch.from_numpy(target).float()[None, None].repeat(1, 3, 1, 1) * 2 - 1
        with torch.no_grad():
            return float(loss_fn(p, t).item())
    except Exception:
        return None

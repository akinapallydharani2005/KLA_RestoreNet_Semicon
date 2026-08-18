from __future__ import annotations

import numpy as np
import cv2


def robust_clip_for_model(x: np.ndarray) -> np.ndarray:
    """Keep intentional NoisyLR out-of-range values, but suppress extreme file artifacts."""
    x = x.astype(np.float32)
    if not np.isfinite(x).all():
        x = np.nan_to_num(x, nan=0.0, posinf=1.25, neginf=-0.25)
    return np.clip(x, -0.25, 1.25)


def classical_restore(x: np.ndarray, scale: int = 2) -> np.ndarray:
    """Fast deterministic fallback: clip, denoise LR, bicubic upsample, mild unsharp mask."""
    x0 = robust_clip_for_model(x)
    clipped = np.clip(x0, 0.0, 1.0)
    # Median handles sparse outliers/speckle without excessive blurring.
    if clipped.shape[0] >= 5 and clipped.shape[1] >= 5:
        med = cv2.medianBlur((clipped * 65535).astype(np.uint16), 3).astype(np.float32) / 65535.0
        pre = 0.70 * clipped + 0.30 * med
    else:
        pre = clipped
    out = cv2.resize(pre, (pre.shape[1] * scale, pre.shape[0] * scale), interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(out, (0, 0), sigmaX=0.7)
    sharp = np.clip(out + 0.18 * (out - blur), 0.0, 1.0)
    return sharp.astype(np.float32)

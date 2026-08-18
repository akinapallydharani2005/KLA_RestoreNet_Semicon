from __future__ import annotations

from pathlib import Path
import numpy as np
import cv2
from PIL import Image


def _normalize(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.float32)
    x -= x.min()
    x /= (x.max() + 1e-8)
    return x


def make_gt(seed: int, size: int = 256) -> np.ndarray:
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    img = np.zeros((size, size), np.float32)
    mode = seed % 5
    if mode == 0:  # texture-like rings and granularity
        for _ in range(18):
            cx, cy = rng.uniform(0, size, 2)
            r = np.sqrt((xx-cx)**2 + (yy-cy)**2)
            img += rng.uniform(0.03, 0.12) * np.cos(r / rng.uniform(5, 16) + rng.uniform(0, 6.28))
        img += rng.normal(0, 0.05, img.shape)
    elif mode == 1:  # dendrite-like branching
        img += rng.normal(0, 0.025, img.shape)
        center = np.array([rng.uniform(0.25, 0.75)*size, rng.uniform(0.25,0.75)*size])
        for a in np.linspace(0, 2*np.pi, 16, endpoint=False):
            length = rng.uniform(0.25, 0.55)*size
            end = center + length*np.array([np.cos(a), np.sin(a)])
            cv2.line(img, tuple(center.astype(int)), tuple(np.clip(end,0,size-1).astype(int)), rng.uniform(0.45,0.9), int(rng.integers(1,3)))
            for _ in range(3):
                t = rng.uniform(0.25, 0.85)
                p = center*(1-t) + end*t
                aa = a + rng.choice([-1,1])*rng.uniform(0.35, 0.9)
                q = p + rng.uniform(0.05,0.18)*size*np.array([np.cos(aa), np.sin(aa)])
                cv2.line(img, tuple(p.astype(int)), tuple(np.clip(q,0,size-1).astype(int)), rng.uniform(0.35,0.8), 1)
        img = cv2.GaussianBlur(img, (0,0), 1.0)
    elif mode == 2:  # wafer-like periodic lines
        img += 0.15*rng.normal(size=img.shape)
        pitch = rng.integers(18, 34)
        for x in range(-pitch, size+pitch, pitch):
            cv2.line(img, (x+rng.integers(-2,3), 0), (x+rng.integers(-2,3), size-1), rng.uniform(0.35,0.85), int(rng.integers(2,5)))
        for y in range(-pitch*2, size+pitch*2, pitch*2):
            cv2.line(img, (0, y+rng.integers(-2,3)), (size-1, y+rng.integers(-2,3)), rng.uniform(0.25,0.65), int(rng.integers(2,4)))
        img = cv2.GaussianBlur(img, (0,0), 0.7)
    elif mode == 3:  # blob microscopy-like
        for _ in range(60):
            cx, cy = rng.uniform(0, size, 2)
            sx, sy = rng.uniform(4,18), rng.uniform(4,18)
            amp = rng.uniform(0.1,0.6)
            img += amp*np.exp(-(((xx-cx)/sx)**2+((yy-cy)/sy)**2)/2)
        img += 0.15*np.sin(xx/rng.uniform(12,34)+yy/rng.uniform(20,40))
    else:  # mixed edges
        img += rng.normal(0,0.05,img.shape)
        for _ in range(14):
            pts = rng.integers(0, size, (rng.integers(3,7),2)).astype(np.int32)
            cv2.polylines(img, [pts], False, rng.uniform(0.35,0.9), int(rng.integers(1,3)))
        img = cv2.GaussianBlur(img, (0,0), 0.6)
    img = _normalize(img)
    img = np.clip(0.08 + 0.88*img, 0, 1)
    return img.astype(np.float32)


def degrade(gt: np.ndarray, seed: int, scale: int = 2) -> np.ndarray:
    rng = np.random.default_rng(seed + 10000)
    h, w = gt.shape
    # Blur before downsampling to mimic resolution loss.
    sigma = rng.uniform(0.25, 1.20)
    blurred = cv2.GaussianBlur(gt, (0,0), sigmaX=sigma)
    lr = cv2.resize(blurred, (w//scale, h//scale), interpolation=cv2.INTER_AREA)
    # Speckle and additive Gaussian; allow mild out-of-range values.
    speckle = lr * rng.normal(0, rng.uniform(0.04,0.16), lr.shape)
    gaussian = rng.normal(0, rng.uniform(0.008,0.045), lr.shape)
    noisy = lr + speckle + gaussian
    if rng.random() < 0.35:
        noisy += rng.normal(0,0.03,(noisy.shape[0],1))  # row/column bias-like artifact
    return noisy.astype(np.float32)


def write_image(path: Path, arr: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    arr_clip = np.clip(arr, 0, 1)
    Image.fromarray((arr_clip*65535+0.5).astype(np.uint16)).save(path)


def create_dataset(out_root: str | Path, n_train: int = 80, n_val: int = 20, size: int = 256, seed: int = 123) -> None:
    out_root = Path(out_root)
    for split, count, offset in [("train", n_train, 0), ("val", n_val, 100000)]:
        for i in range(count):
            s = seed + offset + i
            gt = make_gt(s, size=size)
            lr = degrade(gt, s, scale=2)
            write_image(out_root / split / "gt" / f"sample_{i:04d}.png", gt)
            # For noisy LR, out-of-range is clipped by image format; npy copy preserves true range.
            write_image(out_root / split / "noisy_lr" / f"sample_{i:04d}.png", lr)
            np.save(out_root / split / "noisy_lr" / f"sample_{i:04d}.npy", lr.astype(np.float32))

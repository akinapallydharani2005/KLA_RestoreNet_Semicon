from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Tuple

import numpy as np
from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".npy"}


def list_images(input_dir: str | Path) -> list[Path]:
    root = Path(input_dir)
    files = [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    return sorted(files)


def read_image(path: str | Path) -> tuple[np.ndarray, dict]:
    """Read image as float32 HxW. Preserves raw float range for .npy input."""
    path = Path(path)
    meta = {"suffix": path.suffix.lower(), "stem": path.stem}
    if path.suffix.lower() == ".npy":
        arr = np.load(path).astype(np.float32)
        if arr.ndim == 3:
            arr = arr[..., 0]
        meta["format"] = "npy"
        return arr, meta

    img = Image.open(path)
    meta["format"] = img.format or path.suffix.lower().replace(".", "")
    arr = np.array(img)
    if arr.ndim == 3:
        arr = arr[..., :3].mean(axis=2)
    if np.issubdtype(arr.dtype, np.integer):
        info = np.iinfo(arr.dtype)
        arr = arr.astype(np.float32) / float(info.max)
        meta["dtype"] = str(info.dtype)
    else:
        arr = arr.astype(np.float32)
    return arr.astype(np.float32), meta


def save_image(path: str | Path, image: np.ndarray, source_meta: dict | None = None) -> None:
    """Save output after clipping to [0,1]. For .npy inputs, save float32 .npy."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image = np.asarray(image, dtype=np.float32)
    image = np.clip(image, 0.0, 1.0)
    if path.suffix.lower() == ".npy":
        np.save(path, image.astype(np.float32))
        return
    # PNG/TIFF: use 16-bit to avoid throwing away restored detail; JPEG/BMP: use 8-bit.
    if path.suffix.lower() in {".png", ".tif", ".tiff"}:
        out = (image * 65535.0 + 0.5).astype(np.uint16)
        Image.fromarray(out).save(path)
    else:
        out = (image * 255.0 + 0.5).astype(np.uint8)
        Image.fromarray(out).save(path)


def output_path_for(input_path: Path, input_root: Path, output_root: Path) -> Path:
    rel = input_path.relative_to(input_root)
    # Preserve extension/name; if evaluator expects exact names, this is safest.
    return output_root / rel

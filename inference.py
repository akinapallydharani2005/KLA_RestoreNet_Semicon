#!/usr/bin/env python3
"""Standalone evaluator-facing inference script for KLA image restoration.

Usage:
    python inference.py <input_dir> <output_dir>

The script restores every supported degraded image file in input_dir and writes an output
with the same relative name under output_dir. It supports GPU execution when available.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from src.io_utils import list_images, read_image, save_image, output_path_for
from src.model import build_model
from src.preprocess import classical_restore, robust_clip_for_model


def load_config(config_path: str | Path | None) -> dict:
    if not config_path:
        return {"model": {"channels": 32, "depth": 6, "scale": 2, "residual_scale": 0.20}}
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text())
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text())
    except Exception:
        # The default config is JSON-compatible YAML, so this fallback keeps dependencies light.
        return json.loads(path.read_text())


def load_model(weights_path: str | Path | None, config: dict, device: torch.device):
    model = build_model(config.get("model", {})).to(device)
    if weights_path is None:
        return model, False
    path = Path(weights_path)
    if not path.exists():
        return model, False
    ckpt = torch.load(path, map_location=device)
    state = ckpt.get("model", ckpt)
    model.load_state_dict(state, strict=False)
    model.eval()
    return model, True


def restore_one(arr: np.ndarray, model, device: torch.device, use_model: bool, scale: int) -> np.ndarray:
    if not use_model:
        return classical_restore(arr, scale=scale)
    x = robust_clip_for_model(arr)
    t = torch.from_numpy(x[None, None].astype(np.float32)).to(device, non_blocking=True)
    with torch.no_grad():
        y = model(t).squeeze(0).squeeze(0).detach().cpu().numpy()
    # Stable post-processing: clip exactly inside the submitted pipeline as requested.
    return np.clip(y, 0.0, 1.0).astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description="KLA RestoreNet-Hybrid inference")
    parser.add_argument("input_dir", type=str, help="Directory containing degraded NoisyLR test images")
    parser.add_argument("output_dir", type=str, help="Directory where restored images will be written")
    parser.add_argument("--weights", type=str, default="weights/kla_hybrid_restorer.pt", help="Model checkpoint path")
    parser.add_argument("--config", type=str, default="configs/default.yaml", help="Model config path")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu", help="cuda or cpu")
    parser.add_argument("--scale", type=int, default=2, help="Super-resolution scale factor. Official NoisyLR->GT is 2x.")
    args = parser.parse_args()

    input_root = Path(args.input_dir)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    files = list_images(input_root)
    if not files:
        raise SystemExit(f"No supported image files found in {input_root}")

    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
    config = load_config(args.config)
    config.setdefault("model", {})["scale"] = args.scale
    model, use_model = load_model(args.weights, config, device)

    t0 = time.perf_counter()
    for p in files:
        arr, meta = read_image(p)
        restored = restore_one(arr, model, device, use_model=use_model, scale=args.scale)
        out_path = output_path_for(p, input_root, output_root)
        # npy stays npy; images keep their original extension.
        save_image(out_path, restored, source_meta=meta)
    if device.type == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - t0
    print(f"Restored {len(files)} files to {output_root}")
    print(f"Model checkpoint used: {use_model}; device={device}; total_time_sec={elapsed:.4f}; avg_ms_per_image={elapsed*1000/len(files):.2f}")


if __name__ == "__main__":
    main()

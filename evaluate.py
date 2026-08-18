#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from src.dataset import find_pairs
from src.io_utils import read_image
from src.metrics import psnr, ssim, lpips_optional
from src.preprocess import classical_restore


def resize_to(a: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    if a.shape == shape:
        return a
    return cv2.resize(a, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate restored outputs against GT")
    parser.add_argument("--data-root", default="data/synthetic/val", help="Root containing gt and noisy_lr folders")
    parser.add_argument("--output-dir", default="results/val_restored")
    parser.add_argument("--run-inference", action="store_true", help="Run inference.py before scoring")
    parser.add_argument("--write-csv", default="results/metrics.csv")
    args = parser.parse_args()

    data_root = Path(args.data_root)
    output_dir = Path(args.output_dir)
    if args.run_inference:
        cmd = [sys.executable, "inference.py", str(data_root / "noisy_lr"), str(output_dir)]
        print("Running:", " ".join(cmd))
        t0 = time.perf_counter()
        subprocess.check_call(cmd)
        elapsed = time.perf_counter() - t0
    else:
        elapsed = 0.0

    pairs = find_pairs(data_root)
    rows = []
    baseline_rows = []
    for lr_path, gt_path in pairs:
        gt, _ = read_image(gt_path)
        pred_path = output_dir / lr_path.name
        if not pred_path.exists():
            pred_path = pred_path.with_suffix(".png")
        pred, _ = read_image(pred_path)
        pred = resize_to(pred, gt.shape)
        lr, _ = read_image(lr_path)
        base = classical_restore(lr, scale=2)
        base = resize_to(base, gt.shape)
        rows.append({
            "file": lr_path.name,
            "psnr": psnr(pred, gt),
            "ssim": ssim(pred, gt),
            "lpips": lpips_optional(pred, gt),
        })
        baseline_rows.append({"psnr": psnr(base, gt), "ssim": ssim(base, gt)})

    out_csv = Path(args.write_csv); out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "psnr", "ssim", "lpips"])
        writer.writeheader(); writer.writerows(rows)

    mean_psnr = float(np.mean([r["psnr"] for r in rows])); mean_ssim = float(np.mean([r["ssim"] for r in rows]))
    base_psnr = float(np.mean([r["psnr"] for r in baseline_rows])); base_ssim = float(np.mean([r["ssim"] for r in baseline_rows]))
    summary = f"""KLA RestoreNet-Hybrid validation summary
Images: {len(rows)}
Final PSNR: {mean_psnr:.3f} dB
Final SSIM: {mean_ssim:.4f}
Baseline classical PSNR: {base_psnr:.3f} dB
Baseline classical SSIM: {base_ssim:.4f}
Inference elapsed seconds: {elapsed:.4f}
CSV: {out_csv}
"""
    Path("results").mkdir(exist_ok=True)
    Path("results/summary.txt").write_text(summary)
    print(summary)


if __name__ == "__main__":
    main()

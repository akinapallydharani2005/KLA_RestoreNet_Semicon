#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from src.dataset import find_pairs
from src.io_utils import read_image


def main() -> None:
    parser = argparse.ArgumentParser(description="Create before/after visualization panels")
    parser.add_argument("--data-root", default="sample_data")
    parser.add_argument("--output-dir", default="sample_data/output")
    parser.add_argument("--figure", default="results/figures/restoration_examples.png")
    parser.add_argument("--max-images", type=int, default=3)
    args = parser.parse_args()
    pairs = find_pairs(args.data_root)[:args.max_images]
    if not pairs:
        raise SystemExit("No pairs found")
    fig, axes = plt.subplots(len(pairs), 3, figsize=(9, 3*len(pairs)))
    if len(pairs) == 1:
        axes = np.array([axes])
    for r, (lr_path, gt_path) in enumerate(pairs):
        gt, _ = read_image(gt_path)
        lr, _ = read_image(lr_path)
        pred_path = Path(args.output_dir) / lr_path.name
        if not pred_path.exists():
            pred_path = pred_path.with_suffix(".png")
        pred, _ = read_image(pred_path)
        for ax, img, title in zip(axes[r], [lr, pred, gt], ["NoisyLR input", "Restored output", "Ground truth"]):
            ax.imshow(np.clip(img, 0, 1), cmap="gray", vmin=0, vmax=1)
            ax.set_title(title); ax.axis("off")
    Path(args.figure).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(args.figure, dpi=160)
    print(f"Saved {args.figure}")


if __name__ == "__main__":
    main()

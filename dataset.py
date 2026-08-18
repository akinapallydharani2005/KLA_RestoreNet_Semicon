from __future__ import annotations

from pathlib import Path
import random

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

from .io_utils import read_image


def find_pairs(data_root: str | Path, gt_dir: str = "gt", lr_dir: str = "noisy_lr") -> list[tuple[Path, Path]]:
    root = Path(data_root)
    gt_root = root / gt_dir
    lr_root = root / lr_dir
    gt_map = {p.stem: p for p in gt_root.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".npy"}}
    pairs = []
    for lr in lr_root.rglob("*"):
        if lr.suffix.lower() not in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".npy"}:
            continue
        if lr.stem in gt_map:
            pairs.append((lr, gt_map[lr.stem]))
    return sorted(pairs)


class PairedRestorationDataset(Dataset):
    def __init__(self, pairs: list[tuple[Path, Path]], patch_size: int = 128, augment: bool = True):
        self.pairs = pairs
        self.patch_size = patch_size
        self.augment = augment

    def __len__(self) -> int:
        return len(self.pairs)

    def _crop_pair(self, lr: np.ndarray, gt: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # Make sure GT is exactly 2x LR for training.
        target_h, target_w = lr.shape[0] * 2, lr.shape[1] * 2
        if gt.shape != (target_h, target_w):
            gt = cv2.resize(gt, (target_w, target_h), interpolation=cv2.INTER_AREA)
        ps = min(self.patch_size, target_h, target_w)
        if target_h > ps and target_w > ps:
            y = random.randint(0, target_h - ps)
            x = random.randint(0, target_w - ps)
            # Align LR crop to GT crop.
            y_lr, x_lr = y // 2, x // 2
            ps_lr = ps // 2
            gt = gt[y_lr * 2:y_lr * 2 + ps_lr * 2, x_lr * 2:x_lr * 2 + ps_lr * 2]
            lr = lr[y_lr:y_lr + ps_lr, x_lr:x_lr + ps_lr]
        return lr, gt

    def __getitem__(self, idx: int):
        lr_path, gt_path = self.pairs[idx]
        lr, _ = read_image(lr_path)
        gt, _ = read_image(gt_path)
        lr = lr.astype(np.float32)
        gt = np.clip(gt.astype(np.float32), 0.0, 1.0)
        lr, gt = self._crop_pair(lr, gt)
        if self.augment:
            if random.random() < 0.5:
                lr = np.fliplr(lr).copy(); gt = np.fliplr(gt).copy()
            if random.random() < 0.5:
                lr = np.flipud(lr).copy(); gt = np.flipud(gt).copy()
            k = random.randint(0, 3)
            lr = np.rot90(lr, k).copy(); gt = np.rot90(gt, k).copy()
        return torch.from_numpy(lr[None]), torch.from_numpy(gt[None])

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.dataset import find_pairs, PairedRestorationDataset
from src.metrics import psnr, ssim
from src.model import build_model


def set_seed(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)


def charbonnier(pred, target, eps=1e-3):
    return torch.mean(torch.sqrt((pred - target) ** 2 + eps ** 2))


def gradient_loss(pred, target):
    pred_dx = pred[..., :, 1:] - pred[..., :, :-1]
    pred_dy = pred[..., 1:, :] - pred[..., :-1, :]
    tgt_dx = target[..., :, 1:] - target[..., :, :-1]
    tgt_dy = target[..., 1:, :] - target[..., :-1, :]
    return F.l1_loss(pred_dx, tgt_dx) + F.l1_loss(pred_dy, tgt_dy)


def load_config(path: str | Path) -> dict:
    import yaml
    return yaml.safe_load(Path(path).read_text())


def evaluate_model(model, loader, device):
    model.eval()
    vals = []
    with torch.no_grad():
        for lr, gt in loader:
            lr, gt = lr.to(device), gt.to(device)
            pred = torch.clamp(model(lr), 0, 1)
            for p, t in zip(pred.cpu().numpy(), gt.cpu().numpy()):
                vals.append((psnr(p[0], t[0]), ssim(p[0], t[0])))
    return float(np.mean([v[0] for v in vals])), float(np.mean([v[1] for v in vals]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Train KLA RestoreNet-Hybrid")
    parser.add_argument("--data-root", default="data/synthetic", help="Dataset root containing train/val gt and noisy_lr folders")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--patch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--save-dir", default="weights")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    cfg = load_config(args.config)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_pairs = find_pairs(Path(args.data_root) / "train")
    val_pairs = find_pairs(Path(args.data_root) / "val")
    if not train_pairs:
        raise SystemExit("No training pairs found. Expected data_root/train/gt and data_root/train/noisy_lr")
    if not val_pairs:
        val_pairs = train_pairs[:max(1, min(8, len(train_pairs)))]

    train_ds = PairedRestorationDataset(train_pairs, patch_size=args.patch_size, augment=True)
    val_ds = PairedRestorationDataset(val_pairs, patch_size=args.patch_size, augment=False)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0, pin_memory=torch.cuda.is_available())
    val_loader = DataLoader(val_ds, batch_size=max(1, min(args.batch_size, 8)), shuffle=False, num_workers=0)

    model = build_model(cfg.get("model", {})).to(device)
    optim = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    best_psnr = -1.0
    save_dir = Path(args.save_dir); save_dir.mkdir(parents=True, exist_ok=True)
    history = []
    t0 = time.perf_counter()

    for epoch in range(1, args.epochs + 1):
        model.train(); losses = []
        for lr_img, gt_img in tqdm(train_loader, desc=f"epoch {epoch}/{args.epochs}"):
            lr_img, gt_img = lr_img.to(device), gt_img.to(device)
            pred = model(lr_img)
            loss = cfg.get("loss", {}).get("l1", 1.0) * charbonnier(pred, gt_img)
            loss = loss + cfg.get("loss", {}).get("gradient", 0.10) * gradient_loss(pred, gt_img)
            optim.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim.step()
            losses.append(float(loss.item()))
        val_psnr, val_ssim = evaluate_model(model, val_loader, device)
        rec = {"epoch": epoch, "loss": float(np.mean(losses)), "val_psnr": val_psnr, "val_ssim": val_ssim}
        history.append(rec)
        print(json.dumps(rec, indent=2))
        if val_psnr > best_psnr:
            best_psnr = val_psnr
            torch.save({"model": model.state_dict(), "config": cfg, "epoch": epoch, "val_psnr": val_psnr, "val_ssim": val_ssim}, save_dir / "kla_hybrid_restorer.pt")

    (save_dir / "training_history.json").write_text(json.dumps({"elapsed_sec": time.perf_counter()-t0, "history": history}, indent=2))
    print(f"Saved best checkpoint to {save_dir / 'kla_hybrid_restorer.pt'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from src.synthetic import create_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic paired GT/NoisyLR data for pipeline sanity checks")
    parser.add_argument("--out", default="data/synthetic", help="Output dataset root")
    parser.add_argument("--train", type=int, default=80)
    parser.add_argument("--val", type=int, default=20)
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()
    create_dataset(args.out, n_train=args.train, n_val=args.val, size=args.size, seed=args.seed)
    print(f"Synthetic dataset written to {args.out}")


if __name__ == "__main__":
    main()

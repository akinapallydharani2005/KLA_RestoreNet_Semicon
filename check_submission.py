#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    required = ["README.md", "requirements.txt", "inference.py", "train.py", "configs/default.yaml", "src/model.py"]
    missing = [p for p in required if not Path(p).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")
    out = Path("results/smoke_outputs")
    subprocess.check_call([sys.executable, "inference.py", "sample_data/noisy_lr", str(out), "--device", "cpu"])
    if not any(out.rglob("*")):
        raise SystemExit("Smoke inference wrote no outputs")
    print("Submission smoke check passed.")


if __name__ == "__main__":
    main()

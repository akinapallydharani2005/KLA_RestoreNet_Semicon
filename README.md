# KLA RestoreNet-Hybrid

**Problem:** AI-based restoration of degraded images for semiconductor inspection. The pipeline maps degraded low-resolution noisy inputs (**NoisyLR**) to clean higher-resolution restored images close to the ground truth (**GT**).

**Challenge degradations handled:**
- speckle noise,
- additive Gaussian noise,
- spatial downsampling.

**Core solution idea:** a lightweight 2x super-resolution and denoising CNN with a safe bicubic residual path. The model first upsamples the degraded image and then learns a bounded residual correction so it can recover fine details without hallucinating unrealistic structures.

> Important: the included checkpoint is a self-contained synthetic sanity-check checkpoint because the official KLA training dataset was not included in this chat. For final leaderboard-quality submission, train the same code on the official paired KLA dataset and replace `weights/kla_hybrid_restorer.pt`.

## Folder structure

```text
KLA_RestoreNet_Submission/
  README.md
  requirements.txt
  inference.py
  train.py
  evaluate.py
  visualize.py
  generate_synthetic_data.py
  check_submission.py
  configs/default.yaml
  src/
  weights/kla_hybrid_restorer.pt
  sample_data/
  results/
  solution_presentation.pptx
```

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

For official LPIPS reporting, install the optional package:

```bash
pip install lpips
```

## Inference contract

The evaluator-facing script is standalone and accepts exactly:

```bash
python inference.py <input_test_images_dir> <output_dir>
```

Example:

```bash
python inference.py sample_data/noisy_lr sample_data/output
```

Behavior:
- reads every `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, or `.npy` in the input folder,
- restores each degraded image,
- writes outputs to the output directory,
- preserves relative filenames and extensions,
- clips final scored output to `[0,1]` inside the pipeline,
- uses CUDA automatically when available, otherwise CPU.

## Training on the official KLA dataset

Expected official-style folder layout:

```text
data/kla_official/
  train/
    gt/
    noisy_lr/
  val/
    gt/
    noisy_lr/
```

The GT and NoisyLR files should share the same stem name, for example:

```text
train/gt/img_001.png
train/noisy_lr/img_001.png
```

Train:

```bash
python train.py --data-root data/kla_official --config configs/default.yaml --epochs 80 --batch-size 8 --patch-size 128 --save-dir weights
```

Evaluate:

```bash
python evaluate.py --data-root data/kla_official/val --output-dir results/val_restored --run-inference
```

Visualize examples:

```bash
python visualize.py --data-root data/kla_official/val --output-dir results/val_restored --figure results/figures/restoration_examples.png
```

## Synthetic sanity check

Generate demo data:

```bash
python generate_synthetic_data.py --out data/synthetic --train 80 --val 20 --size 256
```

Train demo checkpoint:

```bash
python train.py --data-root data/synthetic --epochs 3 --batch-size 8 --patch-size 128
```

Run smoke test:

```bash
python check_submission.py
```

## Model design

`KLAHybridRestorer` uses:
- bicubic 2x upsampling as a stable base path,
- lightweight depthwise-separable residual CNN,
- bounded residual prediction using `tanh`,
- clipped output `[0,1]` at inference.

This design targets the challenge trade-off: high PSNR/SSIM/LPIPS quality while keeping end-to-end throughput strong on NVIDIA GPU.

## Losses

The training script combines:
- Charbonnier/L1 reconstruction loss for pixel fidelity,
- gradient loss for edge/detail preservation.

The config reserves a place for SSIM/perceptual loss weighting. LPIPS is intentionally optional to keep the evaluator environment simple unless the team decides to use it.

## Results reporting

The `evaluate.py` script reports:
- PSNR,
- SSIM,
- optional LPIPS if installed,
- baseline comparison against the fast classical restoration path,
- inference runtime if `--run-inference` is used.

## Notes for final portal submission

Before uploading:
1. Train on the official KLA paired dataset.
2. Replace the demo checkpoint in `weights/`.
3. Re-run `python check_submission.py` from a clean environment.
4. Update `results/summary.txt`, `results/metrics.csv`, and the solution PPT with official validation numbers.
5. Add your GitHub repository link and team name where required.

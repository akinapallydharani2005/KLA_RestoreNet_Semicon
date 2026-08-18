# Failure analysis

The included validation results are from the bundled synthetic sanity-check dataset, not the official hidden KLA test set.

## Observed weaknesses

1. **Very strong speckle on thin structures**  
   When a line or dendrite edge is thinner than two pixels in the NoisyLR input, the model may smooth it while suppressing noise.

2. **Out-of-distribution texture frequency**  
   Extremely high-frequency textures can be restored with good global PSNR while still losing some visually sharp micro-patterns.

3. **Edge oversharpening risk**  
   The bounded residual path reduces hallucination, but aggressive gradient-loss weighting can create mild ringing near high-contrast edges.

## Direct improvement plan

- Train on the official KLA paired GT/NoisyLR dataset.
- Add stronger frequency-diverse augmentations generated from official GT images.
- Add SSIM and optional LPIPS/perceptual loss after the L1/gradient baseline stabilizes.
- Evaluate separate validation splits for in-distribution and out-of-distribution content.
- Tune batch size and image saving format on the same GPU class used by the evaluator.

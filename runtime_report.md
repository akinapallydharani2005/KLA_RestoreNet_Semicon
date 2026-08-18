# Runtime report

Smoke-test environment used for the packaged demo:

- Device: CPU in the ChatGPT container runtime
- Sample inference: 3 images, average ~80 ms/image on CPU
- Synthetic validation inference: 32 image files, average ~90 ms/image on CPU
- Official benchmark target: NVIDIA H100 GPU end-to-end runtime

The challenge timing definition includes script startup, model initialization, image I/O, CPU/GPU transfers, model execution, post-processing and output saving. The final command to benchmark is:

```bash
python inference.py <hidden_test_input_dir> <output_dir>
```

For H100 benchmarking, use CUDA and increase batch processing only if the official evaluator permits it. The current script processes images one by one for maximum robustness and simple file-name preservation.

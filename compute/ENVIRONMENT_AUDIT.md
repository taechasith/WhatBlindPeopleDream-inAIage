# Dedicated VLM inference environment audit

**Captured:** 2026-10-06 (Asia/Bangkok)  
**Environment:** `.env_vlm/` — separate from the existing analysis environment.

## Platform

- OS: Windows-10-10.0.26200-SP0, 64-bit.
- Python: 3.10.4, 64-bit.
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU.
- Total VRAM reported by PyTorch: 8,585,216,000 bytes; NVIDIA-SMI reports
  8,188 MiB.
- NVIDIA driver: 592.82; NVIDIA-SMI CUDA capability: 13.1.
- CUDA-enabled PyTorch: `2.11.0+cu128`; `torch.version.cuda == "12.8"`.

## CUDA verification

`torch.cuda.is_available()` returned `True`. A CUDA tensor operation created an
input and result on `cuda:0` and returned the expected scalar value (1240.0).
This was a hardware check only, not research inference.

## Installation basis

The command was selected from the current official PyTorch Windows/Pip CUDA
selector after confirming Python 3.10 support:

```powershell
.\.env_vlm\Scripts\python.exe -m pip install torch torchvision `
  --index-url https://download.pytorch.org/whl/cu128
```

The full environment package record is `compute/pip_freeze_vlm.txt`; the GPU
driver snapshot is `compute/nvidia_smi.txt`.

`pandas` 2.3.3 was added to the dedicated environment before study execution
solely for deterministic local reading/checkpointing of the frozen CSV sample;
it is not used by the model or processor.

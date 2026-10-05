# VLM candidate feasibility record

**Selection boundary:** candidate selection used repository metadata, licensing,
local hardware feasibility, and synthetic non-study preflight only. No locked
VizWiz item, output, or RQ2--RQ5 result was inspected before the primary freeze.

| Candidate | Immutable revision | License | Architecture / processor | Decision |
| --- | --- | --- | --- | --- |
| `Qwen/Qwen2.5-VL-3B-Instruct` | `66285546d2b821cf421d4f5eb2576359d3770cd3` | Qwen Research License (non-commercial research/evaluation use) | `Qwen2_5_VLForConditionalGeneration` / `Qwen2_5_VLProcessor` | Primary: technical preflight passed in fixed FP16 configuration. |
| `HuggingFaceTB/SmolVLM2-2.2B-Instruct` | `482adb537c021c86670beed01cd58990d01e72e4` | Apache-2.0 | `SmolVLMForConditionalGeneration` / AutoProcessor | Fallback only; not run on study inputs and not selected because Qwen passed the predeclared feasibility rule. |

## Primary candidate local artifact

- Download date: 2026-10-06.
- Source: official Hugging Face repository, pinned to the immutable SHA above.
- Weight files / SHA-256:
  - `model-00001-of-00002.safetensors` (3,982,649,232 bytes):
    `41a8895c164b4d32bae6b302f4603fcbc1797f32dafa45c7e9bcda23c6755df8`
  - `model-00002-of-00002.safetensors` (3,526,688,744 bytes):
    `365531ff8752420e89dee707b79d021fb2d6e25abafe486f080555a4fe6972e4`
- Runtime: Transformers 5.18.0, PyTorch 2.11.0+cu128, `qwen-vl-utils` 0.0.14.
- Precision: CUDA FP16; quantization: none; attention backend: eager/default.
- Image policy: Qwen processor receives `min_pixels=200704` and
  `max_pixels=501760` (256--640 visual tokens, respectively, at 28x28 pixels
  per token). This fixed cap controls memory; it is not adapted per condition.
- Generation: deterministic greedy decoding, `do_sample=false`,
  `max_new_tokens=128`, seed 20261006, no temperature/top-p/top-k sampling.

The cached weight directory is ignored by Git. Reproduction requires a fresh
download from the stated repository/revision and verification against hashes.

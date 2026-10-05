# Technical preflight: primary VLM

**Status:** `PASS_TECHNICAL_ONLY_NOT_STUDY_DATA`

## Scope

`compute/preflight_qwen.py` created a researcher-generated synthetic PNG with
simple geometric shapes and text. It never opened a VizWiz image, question,
answer, caption, DreamBank report, or any locked-study data.

## Checks passed

- Pinned Qwen weights loaded on CUDA in FP16.
- All three frozen prompt conditions returned nonempty UTF-8 output.
- Prompt template hashes were recorded and no prompt text was modified.
- Greedy decoding completed without an out-of-memory error.
- Peak allocated VRAM was 7,713,738,752 bytes under the fixed image/token and
  generation settings; the model was unloaded when the process ended.
- Outputs were coherent for the synthetic test and contained no parser failure.

## Frozen technical settings

`do_sample=false`, `max_new_tokens=128`, `seed=20261006`, FP16, no
quantization, image pixels 200704--501760. Full machine-readable non-study
record: `compute/preflight_qwen_result.json`.

This is a runtime feasibility check, not candidate outcome comparison and not
scientific evidence.

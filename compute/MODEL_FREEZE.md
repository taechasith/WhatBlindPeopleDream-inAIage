# Primary VLM freeze

**Date frozen:** 2026-10-06 (Asia/Bangkok)  
**Study data inspected before selection:** **NO**

- **PRIMARY_VLM:** `Qwen/Qwen2.5-VL-3B-Instruct`
- **Immutable revision:** `66285546d2b821cf421d4f5eb2576359d3770cd3`
- **License:** Qwen Research License Agreement, non-commercial
  research/evaluation use. Model weights and source-linked output text will not
  be redistributed in the anonymous review package.
- **Precision / quantization:** CUDA float16; no quantization.
- **Processor / model:** `Qwen2_5_VLProcessor` /
  `Qwen2_5_VLForConditionalGeneration` from Transformers 5.18.0.
- **Attention backend:** Transformers eager/default; no FlashAttention setting.
- **Image policy:** `min_pixels=200704`, `max_pixels=501760`; fixed for all
  items/conditions.
- **Generation:** `do_sample=false`, `max_new_tokens=128`, seed 20261006;
  temperature, top-p, top-k, and repetition penalty are not supplied because
  sampling is disabled.
- **Prompt SHA-256:** Generic
  `ba18ef928fade0b30b7b8d4aa400a607c32fe61ebb88c60f633207e78804e2be`;
  Intent `6b44ddd2106e7ad5cf4b352eab0ae85d53fccd0667d0e5b12d0f08c9f57f970b`;
  Accessibility `d412a8c312c362de48242fb0f85788ecdba49dbc7f387f69317775eaae89532e`.
- **System prompt:** none supplied by this study. The processor's pinned Qwen
  chat template emits its repository-default helpful-assistant system turn;
  `chat_template.json` SHA-256 is
  `ad60d90252ed0b0705ba14e2d0ad0fec0beac1ea955642b54059b36052d8bc96`.
- **Model configuration hashes:** `config.json`
  `7ed3eed5be6924cc800e8a5e53fc405c1aab1aaf36bad65c33403b36c56827f5`;
  `generation_config.json`
  `533f191cc257b7de37a4fccd0a7a1706d75e1aa660f93efaa54e5a2a9f9aace9`;
  study settings override the repository generation configuration as listed
  above.

## Selection reason

The protocol's preferred Qwen candidate loaded and generated valid,
deterministic output for all three frozen prompt forms on a non-study synthetic
image within the available GPU memory. Selection was based only on reproducible
local execution, documented noncommercial license, pinned public revision, and
prompt compatibility. No study outcome or desired effect was examined.

The secondary candidate remains unselected unless a later, explicitly reported
model-robustness run becomes feasible after primary results are frozen.

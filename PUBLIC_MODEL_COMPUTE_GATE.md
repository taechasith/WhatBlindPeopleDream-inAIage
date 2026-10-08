# Public computational-intervention model/compute gate

**Status:** `PASSED_FOR_PRIMARY_OUTPUT_GENERATION; MEASUREMENT_VALIDATION_PENDING`
as of 2026-10-08 (Asia/Bangkok).

## Observed local environment and primary run

- Hardware detection reports an NVIDIA GeForce RTX 4060 Laptop GPU with 8,188
  MiB reported memory.
- The dedicated `.env_vlm/` environment has CUDA-enabled PyTorch 2.11.0+cu128;
  `torch.cuda.is_available()` was `True` on the RTX 4060 Laptop GPU.
- The frozen primary model is `Qwen/Qwen2.5-VL-3B-Instruct` at immutable
  revision `66285546d2b821cf421d4f5eb2576359d3770cd3`, documented in
  [compute/MODEL_FREEZE.md](compute/MODEL_FREEZE.md).
- A deterministic local run completed the locked 1,000-item by 3-condition
  primary design with 3,000 valid outputs and zero logged primary-inference
  technical failures. [MODEL_OUTPUT_FREEZE.md](MODEL_OUTPUT_FREEZE.md) and
  `data/model_outputs/` preserve the output manifest and checksums.

This is a compute/provenance audit, not condition-level analysis. Passing this
gate neither estimates RQ2--RQ5 nor establishes any substantive result.

## Requirements met before accepting primary generation

The frozen primary run records:

1. a provider/checkpoint identifier and immutable revision;
2. model license and permitted research-use boundary;
3. runtime/package versions, hardware, deterministic settings, and image policy;
4. frozen prompt-template identifiers and hashes;
5. local input/output manifests and checksums; and
6. an executable, credential-free local inference command.

The protocol targets a later independently frozen model as a robustness
replication if feasible. Until that replication is performed and analyzed under
the frozen plan, cross-model generalization remains `NOT_ESTIMABLE`.

## Current consequence

The compute gate is satisfied, but the blinded measurement-validation gate
remains binding. RQ2--RQ5 cannot be run until the synthetic panel is technically
frozen; three genuine human coder files are locked; pre-adjudication reliability,
adjudication, same-item synthetic validation, Alt-Test decisions where
applicable, construct eligibility, and separate external validation are frozen
in `CODED_DATA_FREEZE.md`.

No placeholder, synthetic fixture, or model-derived label substitutes for those
records. The private condition mapping remains unopened until that gate is
complete.

# Public computational-intervention model/compute gate

**Status:** BLOCKED — no frozen, executable VLM configuration as of 2026-10-06.

## Observed local environment

- Hardware detection reports an NVIDIA GeForce RTX 4060 Laptop GPU with 8,188
  MiB reported memory.
- The active Python interpreter has CPU-only PyTorch 2.2.2; `cuda_available`
  is `False`.
- `transformers` and Pillow are installed, but `accelerate`, `bitsandbytes`,
  and a supported local VLM runtime are absent. No qualifying vision-language
  model checkpoint is present in the inspected local Hugging Face cache.

This is a capability audit, not a model run. No images were sent to a provider,
no model text was generated, and no empirical result follows from it.

## Gate required before generation

Before any output is accepted, an authorized researcher must record each model
in `config/public_vlm_models.json` with:

1. provider or local checkpoint identifier and immutable revision;
2. model license and permitted research use;
3. runtime and package versions, hardware, and deterministic settings;
4. prompt-template identifiers and image-preprocessing policy;
5. date/time, local input manifest hash, and output checksum; and
6. an executable command that can be rerun without exposing credentials.

The protocol requires at least one frozen model to estimate a model-specific
effect. It targets two or more independently frozen models for replication. If
only one is executed, model-generalization claims are `NOT_ESTIMABLE`.

## Current consequence

The project can validate sources, freeze prompts, and test the analysis
pipeline with explicitly synthetic fixtures. It cannot generate intervention
outputs, estimate RQ2--RQ5, validate automated labels, or draft final findings
until this gate is satisfied. No placeholder text may be substituted for VLM
outputs.

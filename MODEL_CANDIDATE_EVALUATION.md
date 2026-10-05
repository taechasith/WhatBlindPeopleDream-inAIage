# Study 1 non-human model-candidate evaluation

**Status:** `SMOLVLM2_REJECTED_PREEXPOSURE; NO_REPLACEMENT_OUTPUT_AVAILABLE`
**Date:** 2026-10-05

## Candidate evaluated

- `HuggingFaceTB/SmolVLM2-2.2B-Instruct`
- Revision: `482adb537c021c86670beed01cd58990d01e72e4`
- Inputs: the four local, original `*_v2.svg` scenes rendered to PNG
- Prompt: `prompts/default_ai_prompt.txt`
- Decoding: deterministic (`do_sample=false`, `max_new_tokens=130`)
- Runtime: local CPU; no network inference, participant input, or participant
  exposure

## Result

All four candidate descriptions failed the required 60--85-word range, returning
12--14 words. The fail-closed lexical audit found substantial missing marker
coverage in every scene, including zero registered-marker matches for S04. The
model also substituted unsupported objects in some scenes. Full candidate text
and audit rows remain under `private/study1_model_candidates/` and are excluded
from review/public releases.

## Decision

This model is **rejected for Study 1 exposure**. It must not be used for DAI or
SAI merely because its artifact is locally reproducible. The failure is a
non-human stimulus-quality observation, not a result about blind participants,
dream incorporation, accessibility effectiveness, or AI generally.

The original candidate artifact, command, environment, output, and audit are
retained privately to prevent selection-history loss. A replacement must repeat
the same deterministic generation and fail-closed grounding screen before it can
be considered for ethics materials or final system freeze.

## Replacement status

The pinned Qwen2.5-VL candidate artifact was locally checksum-verified, but two
CPU-only generation attempts were intentionally stopped before a complete output
file was written. No Qwen text was inspected, screened, selected, or exposed.
The reason is computational feasibility in the present local execution window,
not a finding about model quality. A complete deterministic run on suitable
hardware remains a required pre-exposure technical gate.

# Synthetic Annotation Panel Freeze v1

**Status:** `FROZEN_BEFORE_HUMAN_LABELS_AND_CONDITION_UNBLINDING`
**Purpose:** blinded, model-derived annotation only; not human-equivalent
coding and not confirmatory ground truth before same-item validation.

## Frozen input and blinding

- Input packet: frozen 3,000-row blinded packet only.
- Visible fields: blind item ID, BLV-originating question, generated output.
- Withheld fields: condition, prompt type, generator model ID, source image,
  original order, hypotheses, human labels, and other judge labels.
- No condition mapping was used to select or interpret synthetic labels.

## Frozen configuration

- Panel config: `config/synthetic_annotation_panel_v1.json`
- Config SHA-256: `c9492dd4cd901bfea0ab837bd01fe4edf42fd01c9191371a2525d7b999a3b98a`
- Prompt: `annotation_public/SYNTHETIC_PANEL_PROMPT_v1.md`
- Prompt SHA-256: `8c27086973eef2ce514b48eac337cbf277cca9a730031366f7d1b53b18910e11`
- Decoding: deterministic (`do_sample=false`), seed `20261008`, maximum 1,400
  generated tokens.
- Retry policy: technical process failures only; no retries for inconvenient,
  malformed, or substantively poor labels.
- Output schema: one machine-auditable record per row/judge/construct with
  label, abstention, evidence span, reason code, and parser status.

## Judges

| Role | Judge | Immutable revision | Family | License | Precision |
| --- | --- | --- | --- | --- | --- |
| Primary | `microsoft/Phi-3.5-mini-instruct` | `2fe192450127e6a83f7441aef6e3ca586c338b77` | Phi-3 | MIT | 4-bit NF4, float16 compute |
| Secondary sensitivity judge | `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | Qwen2 | Apache-2.0 | float16 |

The generator checkpoint `Qwen2.5-VL-3B-Instruct` is not a synthetic judge.
The secondary Qwen-family judge is retained as a separate, explicitly labelled
sensitivity judge and cannot alone certify or dominate consensus.

## Technical preflight

Both judges ran on a researcher-created, non-analytic fixture; no frozen
VizWiz output, mapping, or outcome was used. Phi returned ten parseable
construct records. Qwen returned ten parseable records and the validator
correctly marked PRESENT labels lacking a supporting span as
`EVIDENCE_SPAN_INVALID`. SmolLM2-1.7B failed schema preflight and is rejected
in `compute/SYNTHETIC_JUDGE_CANDIDATE_AUDIT.md`.

## Interpretation boundary

Run outputs remain individual synthetic annotations with preserved disagreement.
They may be compared with the same-item adjudicated human subset only after
human coding exists. Until then they are `MODEL_DERIVED_UNVALIDATED` and cannot
be unblinded, aggregated by condition, or used for RQ2-RQ5.

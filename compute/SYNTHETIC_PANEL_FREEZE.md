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
- Config file SHA-256: `c9492dd4cd901bfea0ab837bd01fe4edf42fd01c9191371a2525d7b999a3b98a`
- Config canonical-JSON SHA-256: `7e3464a2048afafea813adf291852a7fde857eb22816ff87ce83f16f477679e9`
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

## Post-run technical output freeze

After both frozen judges complete, run the fail-closed technical gate below
without reading a condition map or interpreting labels:

```powershell
& .\.env_vlm\Scripts\python.exe code/16_freeze_synthetic_panel_outputs.py `
  --config config/synthetic_annotation_panel_v1.json `
  --prompt annotation_public/SYNTHETIC_PANEL_PROMPT_v1.md `
  --packet annotation_public/private/blinded_packet_primary_v1.csv `
  --panel-dir annotation_public/private/synthetic_panel_v1 `
  --outdir annotation_public/private/synthetic_panel_v1/freeze
```

The gate requires exactly 3,000 raw records and 30,000 construct records per
judge; matching prompt/config/revision hashes; unique blinded IDs; valid parser
states; and no duplicate raw IDs that could indicate an unexplained retry. It
creates a blinded per-item/construct disagreement map, manifest, checksums, and
technical output-freeze record. Those artifacts remain `MODEL_DERIVED_UNVALIDATED`
until the independent human reference gate is complete.

The only accepted parser states are `PARSED`, `EVIDENCE_SPAN_INVALID`,
`PARSE_ERROR:JSONDecodeError`, and `PARSE_ERROR:ValueError`. The latter two are
preserved technical failures rather than semantic labels. Any other status fails
the technical freeze; technical failures and evidence-span-invalid positives
remain in coverage accounting but are excluded from measurement comparison.

`code/15_run_synthetic_annotation_panel.py` embeds the canonical-JSON config
hash in output records, whereas this document also records the byte-level
config-file hash. Both identifiers are retained to make their distinct roles
explicit; neither is a condition label or outcome statistic.

After a successful private output freeze, append a redacted technical-completion
receipt to this tracked file before committing: judge IDs/revisions, raw and
construct counts, parser-status/coverage counts, input and artifact hashes,
freeze command, and runtime environment. Do not include label text, prevalence,
condition mapping, disagreement contents, or condition-level summaries.

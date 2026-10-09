# Computational Measurement and Public-Human Calibration Policy

**Canonical authority:** `CHI2027_Blind_Dreams_AI_Research_Guide.md`.

## Current scope

Status: `SYNTHETIC_PANEL_RUNNING; PUBLIC_DATA_ONLY; CONDITIONS_BLINDED`.

This policy governs a zero-new-human-data computational study. The 3,000 frozen
Qwen outputs, locked 1,000-item sample, prompts, generator configuration, and
private condition mapping must not change. No condition unblinding or RQ2--RQ5
analysis occurs before `CODED_DATA_FREEZE`.

No newly recruited coder, participant, same-item human label, human
adjudication, human-human reliability statistic, or Alt-Test decision is a
current-study gate. The previous matched-human methodology remains in
`future_human_validation/` for future research only.

## Synthetic computational measurement instrument

Phi-3.5-mini is the primary frozen judge and Qwen2.5-1.5B is the secondary
sensitivity judge. Qwen2.5-VL-3B is the generator and cannot be its own sole
judge. Freeze model revision, prompt, decoding settings, schema, retry policy,
and abstention policy before unblinding.

Retain per-construct `row_id`, `judge_id`, `label`, `abstain`, optional
confidence, `evidence_span`, `reason_code`, and `parser_status`. A
`PARSE_ERROR:*` placeholder is `TECHNICALLY_INVALID_FOR_MEASUREMENT`, not a
semantic abstention. A positive label without a valid explicit evidence span is
`EVIDENCE_SPAN_INVALID`. Retain invalid records for coverage accounting; never
silently recode, remove, or retry a substantive output.

Synthetic annotation is **model-derived measurement**, not a human substitute.
It may characterize observable output properties but cannot claim what blind
people feel, prefer, rate, or experience without compatible existing human data.

## Methodological analogy

Pataranutaporn et al. used LLM-generated simulations alongside observed human
survey data to examine where model-generated predictions aligned with or
diverged from reported human responses. The relevant lesson here is narrower:
model simulation can be a research object and diagnostic instrument when its
limits are made visible. This study likewise compares computational
measurements with available released human evidence where constructs overlap; it
does not treat a coherent synthetic output as lived understanding or as a
substitute for direct human judgment.

## Construct tiers and statuses

Freeze one prospective tier and one status per construct before unblinding.

- **Tier A / computationally observable:** direct textual-output property,
  explicit evidence span, and robust computational measurement.
- **Tier B / public-human benchmarked:** bounded external comparison with a
  released real-human dataset; it remains external rather than same-item.
- **Tier C / model-derived exploratory:** material synthetic interpretation
  without adequate public-human grounding.

Statuses:

- `COMPUTATIONAL_PRIMARY`
- `PUBLIC_HUMAN_BENCHMARKED`
- `COMPUTATIONAL_SECONDARY`
- `MODEL_DERIVED_EXPLORATORY`
- `MEASUREMENT_UNSTABLE`

No construct is upgraded because a preferred condition effect appears.

## Computational robustness gate

Before unblinding, assess each construct using blinded data only:

1. inter-model agreement and disagreement;
2. parser/coverage completeness, abstention, and evidence-span validity;
3. prevalence stability;
4. frozen prompt-paraphrase stability on a prospectively selected technical
   subset;
5. deterministic rerun consistency where technically appropriate;
6. label-flip sensitivity; and
7. lexical/rule cross-checks where possible.

Agreement between Phi and Qwen is not proof of validity; shared model bias is a
recorded limitation. Failed robustness yields `MEASUREMENT_UNSTABLE`.

## Public-human calibration boundary

Create `PUBLIC_HUMAN_CALIBRATION_MATRIX.csv` before unblinding. For each
construct record source dataset, human label type, population, task relation,
same-item/different-item relation, measurement overlap, validation strength,
and limitations.

VizWiz answers/captions, Kapur--Kreiss BLV ratings, lawfully accessible
GuideDog Gold, and released Be My AI evidence remain separate external sources.
They cannot be pooled or represented as newly collected labels for Qwen outputs.
VizWiz captions are not BLV preference; GuideDog is `ACCESS_UNAVAILABLE` until
authorized access is documented; Be My AI is ecological only.

Persona-conditioned synthetic evaluators are optional exploratory instruments.
Describe their output as model-derived predictions, never as BLV ratings or
human experience.

## Alt-Test

`ALT_TEST_CURRENT_STUDY = NOT_APPLICABLE_TO_CURRENT_DESIGN` because this study
does not claim synthetic-human annotator interchangeability. Do not execute or
approximate Alt-Test without matched human annotations. It remains a future
validation method only.

## Coded-data freeze

Before unblinding, freeze and checksum: both synthetic judges' individual
outputs; model/prompt/config provenance; parser and evidence-span audit;
disagreement map; construct tiers/statuses; computational robustness results;
public-human calibration matrix; available external validation; label
provenance; and a Git commit. No new human data are required.

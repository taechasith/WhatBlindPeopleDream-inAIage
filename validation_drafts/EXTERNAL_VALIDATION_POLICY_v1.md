# External Validation Policy v1

**Status:** frozen pre-label policy; no condition-specific result, synthetic
label, human label, or model-output text was inspected to create this document.

**Date frozen:** 2026-10-08
**Applies:** before `CODED_DATA_FREEZE`, as the frozen public-human calibration
plan, and again after the condition-level analysis is permitted.
**Does not replace:** computational robustness. It is not same-item human
annotation of the current outputs and is never represented as such.

## Boundary

Released external datasets answer construct-specific questions in their own
measurement settings. They provide external public-human calibration, not
synthetic-human equivalence, not same-item ratings of the current outputs, and
not a universal accessibility ground truth. They cannot be pooled into the
primary within-item intervention analysis.

Every external result must retain its source, unit, denominator, comparison
set, and `NOT_ESTIMABLE` reasons. No caption, answer, preference rating, or
human-verified guidance text is a universal accessibility ground truth.

## VizWiz human references

### Frozen source and expected linkage

- Intervention universe: the locked 1,000 VizWiz VQA items.
- HumanSpace source: released VizWiz Captions validation annotations.
- The preflight join found all 1,000 locked images represented in the caption
  source and 4,866 retained captions for those images. These are multiple
  references per image, not 4,866 independent analytic observations.
- Derived-reference provenance is frozen in
  `data/public_reference/processed/build_manifest.json`.

### Unit and multi-reference handling

The image/question item is the inference unit. For caption-based comparisons,
compute a transparent per-caption score first and aggregate within image before
estimating an item-level quantity. Report both the number of images and the
distribution of usable caption references. Bootstrap/resample at the
image/question-item level; never treat captions as independent replicates.

Primary aggregate: the unweighted mean across usable captions for an image.
Sensitivity aggregate: the median across usable captions. If either aggregate
cannot be calculated for an item, mark that item `NOT_ESTIMABLE` for that
caption metric rather than imputing a reference.

### Question and answer fields

- Released `answerable` is a stratification/sensitivity variable only. It is
  not an outcome correctness label and does not require an uncertainty response
  in every unanswerable case.
- Human answers may support bounded reference-coverage checks only when the
  answer is sufficiently specific for the pre-specified coded construct.
- String overlap is never correctness. A non-match is `NOT_ESTIMABLE` when
  source wording is vague, the image is unreadable, or the released reference
  cannot adjudicate the claimed content.
- Preserve the question type and image/question cluster in all resampling.

### Confound controls

All caption comparisons must report output length and use the frozen
`is_precanned` and image-text-detection/source-text fields as stratification or
sensitivity variables where available. No caption similarity statistic may be
interpreted as BLV preference, task success, agency, safety, or user benefit.

## Kapur--Kreiss released BLV preference evidence

- Source unit: released aggregate rating/comparison records, not individual
  participant responses.
- Preflight source: 136 rows over 18 image IDs, in two comparison sets
  (`context_sensitive` and `different_context`).
- Keep comparison sets separate. Cluster uncertainty at the image/comparison
  level; do not pool rows as independent BLV participants.
- A metric may be assessed only in the task-specific released comparison
  setting. Any association is external construct evidence, not evidence that a
  primary-condition output is preferred by BLV users.
- `Spice` is absent in all locally released rows and is therefore
  `NOT_ESTIMABLE`.

## GuideDog human-verified guidance

**Status:** `ACCESS_UNAVAILABLE`.

The provenance register records authorized-token access as required. No gated
data will be bypassed, scraped, or substituted. GuideDog contributes no result
unless lawful access is independently documented and a prospective amendment is
recorded before use.

## Be My AI / Xie et al.

The released local corpus contains 28 examples and may be used only for a
clearly labelled ecological/descriptive check. It is not a gold-label source,
same-item validation source, prevalence sample, or generalizable estimate.

## Reporting rule

External public-human calibration must be reported separately from (1) the
computational measurement robustness audit and (2) the primary Qwen within-item
intervention. Each table must name the construct, source, unit, N, uncertainty
method, limitation, and whether the quantity is estimable. It must not be
described as a new human judgment or as evidence that a synthetic annotator is
human-equivalent.

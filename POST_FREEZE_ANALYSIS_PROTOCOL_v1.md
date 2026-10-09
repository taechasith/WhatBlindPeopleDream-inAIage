# Post-freeze analysis protocol v1

**Status:** frozen before condition unblinding and before RQ2--RQ5 effects are
inspected.

## Authorization

`code/27_run_post_freeze_public_analysis.py` may execute only after
`results/coded_data_freeze/CODED_DATA_FREEZE.json` records
`CODED_DATA_FROZEN_PUBLIC_DATA_ONLY`. It is the single authorized condition
unblinding for this analysis version. The script refuses to run otherwise.

## RQ2 and RQ5: within-item output effects

For each frozen synthetic judge separately, the script joins blinded labels to
the private mapping only after the coded-data freeze. A label is eligible only
when it is `PARSED`, non-abstaining, and binary. For each construct and
predeclared contrast, the estimand is the paired mean difference in binary
label prevalence (numerator condition minus denominator condition), clustered
by `sample_row_id`. It reports 5,000 cluster-bootstrap 95% intervals and a
10,000-draw paired sign-flip permutation p-value.

The primary family is `task_answer`, `spatial_relation`,
`identity_inference`, `social_intent_inference`, and `ambiguity`; BH adjustment
is applied separately within judge and contrast. The construct-strength table
governs whether a row is computational primary, public-human benchmarked,
secondary, exploratory, or unstable. Judges are reported separately; no
synthetic consensus is treated as a human judgment.

RQ5 additions/omissions are the same paired contrasts described as output
properties, not real-world harms, hallucination prevalence, or user effects.

## RQ3: bounded human-reference alignment

Two prospectively fixed reference metrics are calculated after unblinding:

- `human_answer_mode_string_coverage`: exact normalized released answer-mode
  text is present in the output; for officially unanswerable items, the output
  instead must contain a frozen inability/uncertainty phrase.
- `human_caption_max_token_f1`: maximum token-set F1 between the output and
  each released VizWiz human caption for the same image.

They are reference-alignment measures only. They do not measure semantic truth,
BLV preference, usefulness, or accessibility quality. Kapur--Kreiss remains a
separate external construct-validation source, not a substitute outcome table.

## Nonclaims

All results describe frozen VLM outputs under prompt conditions. They do not
establish effects on BLV people, cognition, dream content, safety, dignity,
privacy, or neural organization.

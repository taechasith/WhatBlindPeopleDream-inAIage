# Annotation and Validation Policy

This is an operational checklist. The canonical authority is
`CHI2027_Blind_Dreams_AI_Research_Guide.md`.

## State and boundary

Status: `PRIMARY_MODEL_OUTPUTS_FROZEN_MEASUREMENT_VALIDATION_PENDING`.

The 3,000 frozen Qwen outputs, private condition mapping, prompts, sample,
model revision, and generation configuration must not change. No condition
unblinding or RQ2-RQ5 analysis occurs before `CODED_DATA_FREEZE`.

## 600-row human validation subset

1. Select 200 locked items reproducibly with a prospectively frozen seed.
2. Include all three condition outputs per item: `200 x 3 = 600` rows.
3. Freeze a selection manifest, shuffle rows, and hide grouping and condition
   clues from coders.
4. Three independent human coders receive and code the identical 600 rows.
5. Train using non-analytic examples, freeze instructions, and require a separate
   pseudonymous independence attestation for each return. The attestation binds
   the received file to the distributed packet/material hashes and records that
   no condition metadata, synthetic labels, other-coder labels, or LLM co-coder
   was used.
6. Validate and atomically lock all three raw files before reliability; calculate
   reliability, then adjudicate. Never edit locked raw files.

## Reliability

Assess each construct separately. Retain every pairwise raw agreement,
prevalence, and uncertainty where feasible; use pairwise Cohen's kappa for
suitable binary labels, weighted kappa for ordinal labels, and a three-coder
Krippendorff's alpha where appropriate. Record rare-category paradoxes. Poor
human reliability downgrades or excludes a construct; synthetic consensus cannot
repair it.

For the 600-row subset, bootstrap uncertainty is a prospectively frozen
item-cluster procedure documented in
`annotation_public/RELIABILITY_BOOTSTRAP_POLICY_v1.md`. It preserves all three
outputs and every coder's missingness pattern within each of the 200 opaque
source-item clusters.

No numerical reliability pass/borderline threshold was frozen before human
labels. Therefore the pre-adjudication report must use
`reliability_decision=THRESHOLD_NOT_PREDEFINED` and
`confirmatory_use=BLOCKED_PENDING_PROSPECTIVE_RULE`; it must not infer a pass,
borderline, or final construct eligibility from observed reliability values.
Any future numerical decision must be prospectively governed without access to
condition-level results and recorded as a new deviation. Structural
non-applicability is separated from poor reliability in
`annotation_public/CONSTRUCT_APPLICABILITY_PRECHECK_v1.csv`.

## Synthetic Annotation Panel / HG-SAP

- Freeze multiple blinded judges from different model families where feasible.
- Qwen2.5-VL-3B is not the sole or primary judge of its own outputs.
- Freeze model/version, prompt, generation settings, schema, seed where
  applicable, retry policy, and abstention policy before unblinding.
- Preserve per-construct `row_id`, `judge_id`, `label`, `abstain`, optional
  confidence, `evidence_span`, `reason_code`, and `parser_status`.
- Treat unsupported PRESENT labels as `EVIDENCE_SPAN_INVALID` unless the
  codebook prospectively permits whole-text inference.

`PARSE_ERROR:*` rows are technical decoding/serialization failures, not semantic
abstentions. The frozen runner retains placeholder `NA` rows only to preserve
the output's rectangular record structure. Preserve such rows, raw responses,
and counts for coverage/failure reporting, but mark them
`TECHNICALLY_INVALID_FOR_MEASUREMENT` and exclude them from label prevalence,
human--synthetic agreement, Alt-Test, and scaled construct analysis. Likewise,
an `EVIDENCE_SPAN_INVALID` PRESENT label is retained and reported but is not a
valid positive measurement. Neither category may be recoded as a negative
label or silently retried.

It is a **Synthetic Annotation Panel** until it has passed same-item,
same-rubric comparison with adjudicated human labels. Only a passing construct
may be described as scaled by HG-SAP.

## Construct-specific validation

For each construct, compare judge labels to the 600 adjudicated human labels.
Record confusion matrix, balanced accuracy, precision, recall, F1 or macro-F1,
specificity/sensitivity, MCC where useful, coverage, abstention, evidence-span
validity, and confidence calibration where applicable. Accuracy alone does not
certify rare constructs.

Use the Alternative Annotator Test only through the authors' method/code or a
verified faithful implementation, when compatible. A formal synthetic-scaling
gate requires the three independent human coders above: the official Alt-Test
FAQ explains that two-human leave-one-out comparisons lack a robust consensus
reference. If only two genuine coders are ultimately available, do not fabricate
a third; record `ALT_TEST_TWO_HUMAN_LIMITATION`, interpret Alt-Test evidence as
weaker, and preserve the human-subset confirmatory analysis independently of
synthetic scaling. Otherwise record `ALT_TEST_NOT_APPLICABLE` and apply a
prospectively frozen alternative rule.

### Frozen Alt-Test epsilon policy

The primary Alt-Test cost-benefit hyperparameter is **epsilon = 0.10** for
every compatible construct and frozen synthetic judge. This is deliberately
conservative: the planned coders are trained, independent non-expert coders
using a fixed rubric, and the policy grants no expert-annotator efficiency
premium. Epsilon is not changed after observing human--human reliability,
human--synthetic agreement, judge winning rates, advantage probabilities, or
condition effects. If a construct's human reliability is inadequate, it is
`CONSTRUCT_NOT_RELIABLE` rather than rescued by changing epsilon. Report the
fixed primary epsilon, the coder-role rationale, human reliability, advantage
probability, and winning rate for every Alt-Test result.

Freeze one status per construct:

- `HUMAN_VALIDATED_SYNTHETIC_SCALE_OK`
- `HUMAN_SUBSET_ONLY_CONFIRMATORY`
- `MODEL_DERIVED_EXPLORATORY`
- `MODEL_DERIVED_UNVALIDATED`
- `CONSTRUCT_NOT_RELIABLE`

The final eligibility table is created only after human reliability,
adjudication, same-item validation, and Alt-Test applicability/decisions. A
blinded construct-applicability precheck is an input to those steps, not a
premature eligibility decision.

## External-validation boundary

VizWiz human answers/captions, GuideDog Gold, Kapur-Kreiss real BLV preference
judgments, and released Be My AI data assess convergent validity, ecological
relevance, preference, and quality relationships. They are not same-item,
same-rubric annotations of the 3,000 Qwen outputs, and cannot alone certify
synthetic labels.

Persona prompting is optional and exploratory. Never attribute an LLM judgment
to BLV people; use “synthetic accessibility-oriented evaluator” or
“model-derived accessibility judgment” where accurate.

## Coded-data freeze and unblinding gate

Before unblinding, retain checksums and provenance for: locked human A/B/C files,
human reliability, locked adjudicated subset, frozen synthetic outputs,
inter-model agreement, construct-level human-versus-synthetic validation,
alt-test decisions, separate external validation, eligibility table, and every
label source/status. Commit this gate. Only then may the private mapping be
used for RQ2-RQ5.

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
4. Both independent human coders receive and code the identical 600 rows.
5. Train using non-analytic examples, freeze instructions, lock raw files,
   calculate reliability, then adjudicate. Never edit locked raw files.

## Reliability

Assess each construct separately. Retain raw agreement, prevalence, and
uncertainty where feasible; use Cohen's kappa for suitable binary labels,
weighted kappa for ordinal labels, and Krippendorff's alpha where appropriate.
Record rare-category paradoxes. Poor human reliability downgrades or excludes a
construct; synthetic consensus cannot repair it.

## Synthetic Annotation Panel / HG-SAP

- Freeze multiple blinded judges from different model families where feasible.
- Qwen2.5-VL-3B is not the sole or primary judge of its own outputs.
- Freeze model/version, prompt, generation settings, schema, seed where
  applicable, retry policy, and abstention policy before unblinding.
- Preserve per-construct `row_id`, `judge_id`, `label`, `abstain`, optional
  confidence, `evidence_span`, `reason_code`, and `parser_status`.
- Treat unsupported PRESENT labels as `EVIDENCE_SPAN_INVALID` unless the
  codebook prospectively permits whole-text inference.

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
verified faithful implementation, when compatible. Otherwise record
`ALT_TEST_NOT_APPLICABLE` and apply a prospectively frozen alternative rule.

Freeze one status per construct:

- `HUMAN_VALIDATED_SYNTHETIC_SCALE_OK`
- `HUMAN_SUBSET_ONLY_CONFIRMATORY`
- `MODEL_DERIVED_EXPLORATORY`
- `MODEL_DERIVED_UNVALIDATED`
- `CONSTRUCT_NOT_RELIABLE`

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

Before unblinding, retain checksums and provenance for: locked human A/B files,
human reliability, locked adjudicated subset, frozen synthetic outputs,
inter-model agreement, construct-level human-versus-synthetic validation,
alt-test decisions, separate external validation, eligibility table, and every
label source/status. Commit this gate. Only then may the private mapping be
used for RQ2-RQ5.

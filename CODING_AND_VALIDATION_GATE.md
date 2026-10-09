# Computational measurement and public-human calibration gate

## Status

`PRIMARY_MODEL_OUTPUTS_FROZEN_INTERPRETATION_STILL_BLINDED`

The frozen primary run contains 3,000 valid outputs: the 1,000-item locked
VizWiz validation sample crossed with three frozen prompt conditions. This gate
contains no condition-level outcome, contrast, or hypothesis interpretation.

## Current-study sequence

1. Complete and technically freeze both blinded synthetic judges, preserving
   individual outputs, parser states, evidence spans, abstentions, disagreement,
   provenance, and checksums.
2. Run the frozen computational robustness audit construct by construct:
   coverage, parser completeness, evidence-span validity, label/abstention
   coherence, inter-model disagreement, deterministic rerun consistency,
   frozen prompt-paraphrase stability, controlled label-flip sensitivity, and
   eligible lexical/rule cross-checks.
3. Freeze every construct's Tier A, B, or C classification and measurement
   strength in `CONSTRUCT_MEASUREMENT_TIER_MATRIX.csv`.
4. Run public-human calibration as separate evidence streams:
   - VizWiz human captions/answers: bounded HumanSpace and answer-reference
     comparison; not a proxy for BLV preference.
   - released Kapur--Kreiss BLV preference evidence: external, task-specific
     construct validation only.
   - GuideDog human-verified guidance: domain-external reference only if lawful
     access becomes available; otherwise `ACCESS_UNAVAILABLE`.
   - released Be My AI material: ecological/descriptive check only.
5. Freeze provenance, calibration boundaries, robustness results, and
   measurement status in `CODED_DATA_FREEZE.md`, then and only then unblind
   condition labels and run RQ2--RQ5.

## Blinding controls

The synthetic packet contains a shuffled neutral identifier, the
BLV-originating question, and the model output. It excludes condition, prompt
type, source-image filename, original order, private condition mapping, and
hypothesis direction. No condition mapping may be used until the coded-data
freeze is committed.

## Boundary

This public-data study collects no new human annotation. Synthetic annotation
is a computational measurement instrument, not a human substitute. It may
measure bounded text properties under the frozen rubric; it may not establish
what blind or low-vision people feel, prefer, perceive, or would rate unless a
compatible released public human dataset supports that precise claim.

The former three-coder/adjudication/Alt-Test workflow is preserved under
`future_human_validation/` for a later matched-human validation study. It is
not a current gate.

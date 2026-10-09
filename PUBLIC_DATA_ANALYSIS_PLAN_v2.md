# Public-data analysis plan v2.0

**Status:** frozen before acquisition of the new confirmatory intervention
corpus and before its outcomes are inspected.

## Sample and model-selection rule

Use the VizWiz validation split because its questions and answers are released.
After legal source acquisition, generate an eligibility table without inspecting
model outputs. Select 1,000 rows using seed `20261006`, stratified by
`answerable` and a frozen deterministic question taxonomy. The selected
IDs and the complete exclusion flow are immutable before generation.

Use at least two reproducibly obtainable VLMs. For each model, record immutable
revision, license, retrieval date, compute route, image preprocessing, prompt
text/hash, seed/decoding settings, failure/retry policy, and output hashes.
If two eligible models cannot be reproduced, conduct the intervention with one
model and label all model-generalization claims `NOT_ESTIMABLE`.

## Measurement and calibration hierarchy

1. **Tier A — computationally observable:** direct text-output properties with
   explicit evidence spans, frozen rule/classifier checks, and the pre-specified
   computational robustness gate.
2. **Tier B — public-human benchmarked:** measurements whose bounded use can be
   externally calibrated against released human answers, captions,
   human-verified guidance, or BLV preference evidence. These datasets are
   external evidence, not newly collected or same-item ratings of the current
   outputs.
3. **Tier C — model-derived exploratory:** subjective or grounding-dependent
   constructs without a sufficiently direct public human benchmark.

The study collects no new human annotations and does not claim that synthetic
annotators replace people. Only Tier A measures that pass computational
robustness, and Tier B measures with their stated external boundary, may support
the corresponding confirmatory computational claims. Tier C profiles remain
explicitly model-derived exploratory diagnostics.

## Reporting rules

- Do not call prompt-condition differences human benefit, safety improvement,
  or user preference without matching released evidence.
- Do not pool GuideDog gold, GuideDog silver, VizWiz captions, and Be My AI text
  as exchangeable samples.
- Do not describe DreamSpace as a mental measurement; it is expression in dream
  reports.
- Keep all content-bearing raw data local and excluded from the anonymous
  review bundle unless each source permits redistribution.

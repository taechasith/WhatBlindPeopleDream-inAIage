# Public-data analysis plan v2.0

**Status:** frozen before acquisition of the new confirmatory intervention
corpus and before its outcomes are inspected.

## Sample and model-selection rule

Use the VizWiz validation split because its questions and answers are released.
After legal source acquisition, generate an eligibility table without inspecting
model outputs. Select 1,000 rows using seed `20261006`, stratified by
`answerable` and a deterministic preregistered question taxonomy. The selected
IDs and the complete exclusion flow are immutable before generation.

Use at least two reproducibly obtainable VLMs. For each model, record immutable
revision, license, retrieval date, compute route, image preprocessing, prompt
text/hash, seed/decoding settings, failure/retry policy, and output hashes.
If two eligible models cannot be reproduced, conduct the intervention with one
model and label all model-generalization claims `NOT_ESTIMABLE`.

## Validation hierarchy

1. Released source labels: VizWiz answerability/answers, GuideDog gold status,
   and released preference judgments where compatible.
2. Independent human coding of a preregistered, stratified output subset. This
   is annotation of public source/model material, not participant recruitment;
   obtain any institutional determination required before beginning it.
3. Rule-based or frozen model-assisted coding, evaluated against Level 1/2.

Only measures with a documented validation path may be confirmatory. All other
CSO profiles remain descriptive diagnostics.

## Reporting rules

- Do not call prompt-condition differences human benefit, safety improvement,
  or user preference without matching released evidence.
- Do not pool GuideDog gold, GuideDog silver, VizWiz captions, and Be My AI text
  as exchangeable samples.
- Do not describe DreamSpace as a mental measurement; it is expression in dream
  reports.
- Keep all content-bearing raw data local and excluded from the anonymous
  review bundle unless each source permits redistribution.

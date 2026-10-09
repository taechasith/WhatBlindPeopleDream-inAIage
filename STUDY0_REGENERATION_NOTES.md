# Study 0 regeneration and applicability notes

**Date:** 2026-10-05 (Asia/Bangkok)  
**Status:** exploratory lexical-diagnostic regeneration; not confirmatory
analysis.

**Current-scope note (2026-10-09):** This historical Study 0 diagnostic remains
limited to public-data lexical measurement. Its lack of human coding does not
create a current prerequisite for the separate public-data computational
measurement scope. It does not authorize RQ2--RQ5, access to private model
outputs or condition mappings, or a claim of human-equivalent measurement.
Before `CODED_DATA_FREEZE`, it also does not authorize human-readable label
substance or condition-level inspection; designated blinded scripts may perform
technical and robustness audits without exposing their contents.

## Purpose

This note documents the correction made after an audit found that several
automated candidate-label columns had been represented as binary values even
when their codebook definitions required unavailable context. The correction
does not create human labels, repair the semantic validity of lexical rules, or
upgrade any Study 0 result to confirmatory evidence.

## Inputs and units

| Source role | Input file | Unit count |
|---|---|---:|
| Dream expression | `data/dreambank/processed/dream_reports.csv` | 381 reports |
| BLV question wording | `data/ai_sensory/processed/corpus_items.csv` | 24,842 questions |
| Released AI-description wording | `data/ai_sensory/processed/corpus_items.csv` | 28 descriptions |

The analysis identifiers total 25,251 unique text units. The raw and processed
source texts are intentionally not versioned in the anonymous analysis
repository. Provenance records exist in `data/MANIFEST.csv`,
`data/CHECKSUMS.csv`, and `data/LICENSES.md`, but they are not yet sufficient
for clean-clone reproduction: the current manifest does not enumerate the Xie
text source and the checksum ledger does not yet record every local raw
snapshot used by the scripts.

## What was corrected

`code/04_apply_codebook.py` retains deterministic regular-expression hits only
as lexical candidate labels. It now emits an empty cell (`NA` in this note) for
the following source/category combinations:

| Category | Why unavailable | Affected source role(s) |
|---|---|---|
| `task_relevance` | Requires judging an output against a stated task; no paired request/output is available | DreamBank reports; AI descriptions |
| `intent_match` | Requires a paired user request and output | DreamBank reports; BLV questions; AI descriptions |
| `unsupported_information` | Requires a gold/reference validation basis | DreamBank reports; BLV questions; AI descriptions |

This is an applicability correction, not evidence that the remaining columns
are semantically valid across all source roles. The 26 retained columns still
include lexical features with important role differences (for example,
identity, privacy, reading, navigation, and nightmare terms). Those features
are not human-validated cross-domain constructs and must not be presented as
such.

## Alignment calculation

`code/07_ai_alignment.py` includes a column in a pairwise profile only when it
is non-empty for every item in both source groups. All three pairwise
comparisons therefore use 26 columns and explicitly list the three excluded
non-estimable categories in `results/alignment_metrics.csv`. "26" means
mechanically non-empty columns, not a human-validated common ontology.

The vector for a source group is the per-item prevalence of each retained
lexical rule. Jensen--Shannon divergence, cosine similarity, and Hellinger
distance are computed from those prevalence vectors after the normalization in
the script. This is a description of word-pattern distributions, not a measure
of mental representation or information quality.

## Regenerated outputs

The following values were regenerated from the current label table with Python
3.10.4 and the fixed seed in `code/07_ai_alignment.py` (`20261005`). A
read-only parity check reproduced every stored point metric and bootstrap bound
exactly.

| Comparison | Categories | JS divergence | Diagnostic bootstrap 95% interval | Cosine | Hellinger |
|---|---:|---:|---:|---:|---:|
| AI descriptions vs. BLV questions | 26 | 0.350812 | 0.327469--0.402357 | 0.545230 | 0.519755 |
| AI descriptions vs. DreamBank reports | 26 | 0.191052 | 0.163119--0.266954 | 0.729732 | 0.386590 |
| BLV questions vs. DreamBank reports | 26 | 0.432980 | 0.413303--0.452258 | 0.315960 | 0.571950 |

The intervals are **diagnostic only**: they use 100 item-level bootstrap
resamples and do not model DreamBank's repeated reports within pseudonymous
dreamers. They are not confirmatory confidence intervals.

## Validation checks completed

- 25,251 label rows have unique item identifiers and only `0`, `1`, or empty
  applicability values.
- All 28 AI descriptions have `NA` for `task_relevance`, `intent_match`, and
  `unsupported_information`.
- All 24,842 BLV questions have `NA` for `intent_match` and
  `unsupported_information`.
- All 381 DreamBank reports have `NA` for all three unavailable categories.
- `results/automated_candidate_distribution.csv` uses
  `NOT_ESTIMABLE_NO_VALIDATION_BASIS` rather than a zero prevalence for an
  unavailable category.
- Point metrics and the stored diagnostic bootstrap bounds in
  `results/alignment_metrics.csv` reproduced exactly from the current labels.

## Limits that remain

1. No independent human coding, adjudication, kappa, alpha, or model-versus-human
   performance estimate is claimed. See `results/reliability.csv`. This limits
   Study 0 to its stated lexical-diagnostic interpretation, but does not make
   new human coding or an AltTest a current prerequisite for public-data
   computational measurement.
2. The AI sample is only 28 heterogeneous released examples, not a deployment
   sample or an estimate of any model's behavior.
3. Source roles differ: questions express requests, descriptions provide text,
   and dream reports are retrospective narratives. A divergence is neither an
   error rate nor a preference score.
4. The current bootstrap is not cluster-aware and does not meet the frozen
   confirmatory mixed-model plan.
5. The correction occurred after the original exploratory results were seen;
   it is recorded as a deviation and cannot convert those results into
   confirmatory evidence.
6. A fresh checkout cannot yet recreate the source corpora from acquisition
   scripts alone; the provenance/checksum gap must be closed before a full
   reproducibility claim.

## Permitted interpretation

Study 0 can motivate preregistered questions for Study 1. It cannot establish
that AI changes cognition, neural organization, dream content, safety, agency,
or lived experience. Any future use of its output must retain the label
`EXPLORATORY_AUTOMATED_CANDIDATE`. A released human reference may be used only
as source-specific calibration for a named measure, with its unit and provenance
recorded; it is not new coding or evidence of general human equivalence. The
separate `future_human_validation/` archive remains prospective and cannot
retroactively validate these results.

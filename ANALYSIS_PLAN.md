# Analysis plan

> **HISTORICAL / SUPERSEDED FOR ACTIVE WORK (2026-10-09).** This v1 plan is
> preserved as an immutable record of the former full-program analysis design.
> Active work is governed by the public-data-only computational-measurement
> scope in `PROTOCOL_PUBLIC_DATA_v2.md` and `PUBLIC_DATA_ANALYSIS_PLAN_v2.md`.
> The active scope does not require new human coding or an AltTest, does not
> authorize human-readable label substance, private condition mappings, or
> condition-level inspection before `CODED_DATA_FREEZE`, and does not authorize
> RQ2--RQ5. Designated automated blinded scripts may perform technical and
> robustness audits without exposing their contents.
> `future_human_validation/` remains a separate prospective archive and cannot
> retroactively validate current computational measurements.

**Version:** v1.0, frozen 2026-10-05 before data acquisition/outcome inspection.

## Shared representation

Every eligible text unit receives the frozen CSO labels in `CODEBOOK_v0.csv`.
For each category retain binary expression (`0`, `1`, or `NA`), count where
applicable, coding provenance, and source type. For free-recall dream text,
`0` means *not expressed in this report*, not absent from the dreamer's
experience.

## Quality gates before primary inference

1. Provenance, license, source URL, and data-unit fields are complete.
2. Human double-coding covers at least 20% of material, stratified by corpus
   type; first-pass reliability is reported before adjudication.
3. Major-category reliability target is Cohen's kappa >= .70, while reporting
   prevalence effects and using weighted kappa/Krippendorff's alpha where
   appropriate. Definitions are revised and material re-coded if the target
   fails.
4. If a model assists coding, archive model/version/date, deterministic settings,
   exact prompt, per-category precision/recall/F1 against human labels, and
   systematic-error review. Unsupported model labels do not enter confirmatory
   analysis.

## Dream analysis

- Extract one literature row per reported estimate. Keep participant, dream, and
  study-estimate denominators separate.
- Where sufficiently comparable estimates exist, use random-effects
  meta-analysis with effect estimates, 95% confidence intervals, heterogeneity,
  and sensitivity analyses.
- For item-level DreamBank data, fit binomial/logistic mixed models for each
  prespecified category with onset group as a fixed effect and dreamer/series as
  random intercepts where identifiers and sample sizes permit. If models are
  unstable, use pre-specified bootstrap/permutation alternatives and report the
  failure.
- Treat collection method (free recall versus prompted), dataset/series, and
  onset metadata confidence as design variables. Never impute onset.

## BLV intent and AI mediation vectors

- Estimate category distributions separately for BLV questions, human
  descriptions, AI descriptions, human-verified AI guidance, and preference
  data. Preserve task type, human/AI origin, gold/silver label, and source.
- Measure frequencies with bootstrap confidence intervals resampled at the
  highest defensible clustering level (dataset and paired item where available).
- Compare AI and human text only within release-supported comparable task sets.
- For grounded comparisons, report HAGS components separately on a 0--1 scale;
  do not manufacture a weighted composite after viewing results.
- AHSEP is descriptive only: visual-object, spatial, social inference,
  aesthetic, cross-modal, uncertainty, and actionable-safety information.

## Cross-domain alignment audit

For a prespecified common category set, calculate normalized profile vectors and
pairwise Jensen-Shannon divergence, cosine similarity, Hellinger distance, and
category-level differences with bootstrap 95% confidence intervals. The planned
comparisons are:

1. Dream expression by eligible blindness-history group.
2. BLV intent versus human accessibility descriptions.
3. BLV intent versus AI accessibility descriptions.
4. Human descriptions versus AI descriptions.
5. AI descriptions versus human-verified AI guidance.
6. Dream expression versus each waking/description corpus, explicitly as a
   descriptive alignment comparison rather than cognitive transfer.

## Robustness and falsification

Run and report: congenital-only; congenital versus acquired when metadata
permits; free recall versus prompted; removal of smallest dream series; human
versus AI text; human-verified versus silver GuideDog; text-length controls;
vocabulary-confound inspection; bootstrap uncertainty; task-context
stratification; geographic/language limitations; and manual review of the 50
strongest AI-human mismatches. If any required test is not estimable, report
`NOT_ESTIMABLE` with the cause.

## Multiple comparisons and reporting

Report effect sizes and interval estimates before p-values. For families of
category-level confirmatory tests, use Benjamini-Hochberg false-discovery-rate
adjustment and preserve unadjusted values in machine-readable outputs. No result
is elevated solely because it is statistically significant.

## Social-impact translation

Each major result is recorded as: finding -> affected capability -> plausible
real-world consequence -> design implication -> evidence strength ->
uncertainty/limitation. Plausible risk is never reported as measured harm.

## Reproducibility outputs

All generated values must flow from versioned scripts to machine-readable output
files. Randomized analysis records a seed; raw source files are immutable;
exclusions, access failures, decisions, model use, and protocol deviations are
logged. The review package contains no author-identifying metadata.

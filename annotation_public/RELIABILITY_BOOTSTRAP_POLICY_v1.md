# Blinded human-reliability bootstrap policy v1

**Status:** frozen before any genuine human coder labels are received.

## Unit and resampling rule

The 600-row validation subset contains three blinded outputs from each of 200
locked source items. Reliability uncertainty will therefore use an item-cluster
bootstrap, not an independent-row or independent-coder-cell bootstrap. Each
replicate resamples the 200 opaque item clusters with replacement and retains
all three outputs and all A/B/C labels within each selected cluster.

The mapping from `blind_item_id` to an opaque `cluster_id` is built
mechanically from the private map using only `blind_item_id` and
`sample_row_id`. It contains no condition, prompt, model, output, or source
image field, remains under ignored `annotation/locked/`, and is not inspected
for condition effects.

## Frozen inference settings

- Replicates: 2,000.
- Seed: 20261008.
- Interval: two-sided 95% percentile bootstrap interval.
- Metrics: pairwise raw agreement and Cohen's kappa where estimable; three-coder
  nominal Krippendorff alpha where estimable.
- Degenerate replicates are excluded only from the CI calculation for their
  non-estimable metric and their count is reported. They are never converted to
  a favorable value.

## Decision boundary

The bootstrap quantifies uncertainty; it does not create a reliability pass
threshold. Until a separate prospective governance decision supplies a
criterion, every text-packet-applicable construct has
`reliability_decision=THRESHOLD_NOT_PREDEFINED` and
`confirmatory_use=BLOCKED_PENDING_PROSPECTIVE_RULE` after its raw metrics are
calculated. Structurally unavailable constructs retain their separate
`NOT_ESTIMABLE_STRUCTURAL_NO_REFERENCE` status in the frozen applicability
precheck.
